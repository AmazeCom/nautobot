from django_celery_results.backends import DatabaseBackend

from nautobot.extras.models import JobResult


class NautobotDatabaseBackend(DatabaseBackend):
    """
    Nautobot extensions to support database integration of Job machinery.
    """

    TaskModel = JobResult

    def _get_extended_properties(self, request, traceback):
        """
        Overload default so that `argsrepr` and `kwargsrepr` aren't used to construct `args` and `kwargs`.
        """
        extended_props = {
            "periodic_task_name": None,
            "task_args": None,
            "task_kwargs": None,
            "task_name": None,
            "traceback": None,
            "worker": None,
        }
        if request and self.app.conf.find_value_for_key("extended", "result"):

            # do not encode args/kwargs as we store these in a JSONField instead of TextField
            task_args = getattr(request, "args", None)
            task_kwargs = getattr(request, "kwargs", None)

            properties = getattr(request, "properties", {}) or {}
            periodic_task_name = properties.get("periodic_task_name", None)
            extended_props.update(
                {
                    "periodic_task_name": periodic_task_name,
                    "task_args": task_args,
                    "task_kwargs": task_kwargs,
                    "task_name": getattr(request, "task", None),
                    "traceback": traceback,
                    "worker": getattr(request, "hostname", None),
                }
            )

        return extended_props
