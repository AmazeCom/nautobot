import logging
import os
from pathlib import Path
import pkgutil
import sys

from celery import Celery, shared_task, signals
from celery.fixups.django import DjangoFixup
from django.conf import settings
from kombu.serialization import register
from prometheus_client import CollectorRegistry, multiprocess, start_http_server

from nautobot.core.celery.encoders import _dumps, _loads
from nautobot.core.celery.log import NautobotLogHandler


logger = logging.getLogger(__name__)
# The Celery documentation tells us to call setup on the app to initialize
# settings, but we will NOT be doing that because of a chicken-and-egg problem
# when bootstrapping the Django settings with `nautobot-server`.
#
# Note this would normally set the `DJANGO_SETTINGS_MODULE` environment variable
# which Celery and its workers need under the hood.The Celery docs and examples
# normally have you set it here, but because of our custom settings bootstrapping
# it is handled in the `nautobot.setup() call, and we have implemented a
# `nautobot-server celery` command to provide the correct context so this does
# NOT need to be called here.
# nautobot.setup()


class NautobotCelery(Celery):
    task_cls = "nautobot.core.celery.task:NautobotTask"

    def register_task(self, task, **options):
        """Override the default task name for job classes to allow app provided jobs to use the full module path."""
        from nautobot.extras.jobs import Job

        if issubclass(task, Job):
            task = task()
            task.name = task.registered_name

        return super().register_task(task, **options)


app = NautobotCelery("nautobot")

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes. Again, this is possible
# only after calling `nautobot.setup()` which sets `DJANGO_SETTINGS_MODULE`.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Because of the chicken-and-egg Django settings bootstrapping issue,
# Celery doesn't automatically install its Django-specific patches.
# So we need to explicitly do so ourselves:
DjangoFixup(app).install()

# Load task modules from all registered Django apps.
app.autodiscover_tasks()


# Load jobs from JOBS_ROOT on celery workers
@signals.import_modules.connect
def import_tasks_from_jobs_root(sender, **kwargs):
    jobs_root = settings.JOBS_ROOT
    if jobs_root and os.path.exists(jobs_root):
        if jobs_root not in sys.path:
            sys.path.append(jobs_root)
        for _, module_name, _ in pkgutil.iter_modules([jobs_root]):
            try:
                sender.loader.import_task_module(module_name)
            except Exception as exc:
                # logger.error(f"Unable to load module '{module_name}' from {jobs_root}: {exc:}")
                logger.exception(exc)


@signals.after_setup_task_logger.connect
def setup_nautobot_joblogentry_logger(logger, loglevel, logfile, format, colorize, **kwargs):
    logger.addHandler(NautobotLogHandler())


@signals.worker_ready.connect
def setup_prometheus(**kwargs):
    """This sets up an HTTP server to serve prometheus metrics from the celery workers."""
    # Don't set up the server if the port is undefined
    if not settings.CELERY_WORKER_PROMETHEUS_PORTS:
        return

    logger.info("Setting up prometheus metrics HTTP server for celery worker.")

    # Ensure that the multiprocess coordination directory exists. Note that we explicitly don't clear this directory
    # out because the worker might share its filesystem with the core app or another worker. The multiprocess
    # mechanism from prometheus-client takes care of this.
    multiprocess_coordination_directory = Path(os.environ["prometheus_multiproc_dir"])
    multiprocess_coordination_directory.mkdir(parents=True, exist_ok=True)

    # Set up the collector registry
    registry = CollectorRegistry()
    multiprocess.MultiProcessCollector(registry, path=multiprocess_coordination_directory)
    for port in settings.CELERY_WORKER_PROMETHEUS_PORTS:
        try:
            start_http_server(port, registry=registry)
            break
        except OSError:
            continue
    else:
        logger.warning("Cannot export Prometheus metrics from worker, no available ports in range.")


# Register the custom serialization type
register("nautobot_json", _dumps, _loads, content_type="application/x-nautobot-json", content_encoding="utf-8")


#
# nautobot_task
#
# By exposing `shared_task` within our own namespace, we leave the door open to
# extending and expanding the usage and meaning of shared_task without having
# to undergo further refactoring of task's decorators. We could also transparently
# swap out shared_task to a custom base task.
#

nautobot_task = shared_task


def register_jobs(*jobs):
    """Helper method to register multiple jobs."""
    for job in jobs:
        app.register_task(job)
