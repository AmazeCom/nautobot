import time

from django.conf import settings
from django.db import transaction

from nautobot.core.celery import register_jobs
from nautobot.dcim.models import Device, Location
from nautobot.extras.choices import ObjectChangeActionChoices
from nautobot.extras.jobs import DryRunVar, IntegerVar, Job, JobHookReceiver, JobButtonReceiver


name = "ExamplePlugin jobs"


class ExampleDryRunJob(Job):
    dryrun = DryRunVar()

    class Meta:
        approval_required = True
        has_sensitive_variables = False
        description = "Example job to remove serial number on all devices, supports dryrun mode."

    def run(self, dryrun):
        try:
            with transaction.atomic():
                devices_with_serial = Device.objects.exclude(serial="")
                log_msg = f"Removing serial on {devices_with_serial.count()} devices."
                if dryrun:
                    log_msg += " (DRYRUN)"
                self.logger.info(log_msg)
                for device in devices_with_serial:
                    if not dryrun:
                        device.serial = ""
                        device.save()
        except Exception:
            self.logger.error(f"{self.__name__} failed. Database changes rolled back.")


class ExampleJob(Job):
    # specify template_name to override the default job scheduling template
    template_name = "example_plugin/example_with_custom_template.html"

    class Meta:
        name = "Example job, does nothing"
        description = """
            Markdown Formatting

            *This is italicized*
        """

    def run(self):
        pass


class ExampleHiddenJob(Job):
    class Meta:
        hidden = True
        name = "Example hidden job"
        description = "I should not show in the UI!"

    def run(self):
        pass


class ExampleLoggingJob(Job):
    interval = IntegerVar(default=4, description="The time in seconds to sleep.")

    class Meta:
        name = "Example logging job."
        description = "I log stuff to demonstrate how UI logging works."
        task_queues = [
            settings.CELERY_TASK_DEFAULT_QUEUE,
            "priority",
            "bulk",
        ]

    def run(self, interval):
        self.logger.debug(f"Running for {interval} seconds.")
        for step in range(1, interval + 1):
            time.sleep(1)
            self.logger.info(f"Step {step}")
        self.logger.info("Success")
        return f"Ran for {interval} seconds"


class ExampleJobHookReceiver(JobHookReceiver):
    class Meta:
        name = "Example job hook receiver"
        description = "Validate changes to object serial field"

    def receive_job_hook(self, change, action, changed_object):
        # return on delete action
        if action == ObjectChangeActionChoices.ACTION_DELETE:
            return

        # log diff output
        snapshots = change.get_snapshots()
        self.logger.info(f"DIFF: {snapshots['differences']}")

        # validate changes to serial field
        if "serial" in snapshots["differences"]["added"]:
            old_serial = snapshots["differences"]["removed"]["serial"]
            new_serial = snapshots["differences"]["added"]["serial"]
            self.logger.info(f"{changed_object} serial has been changed from {old_serial} to {new_serial}")

            # Check the new serial is valid and revert if necessary
            if not self.validate_serial(new_serial):
                changed_object.serial = old_serial
                changed_object.save()
                self.logger.info(f"{changed_object} serial {new_serial} was not valid. Reverted to {old_serial}")

            self.logger.info("Success", validation_completed=changed_object)

    def validate_serial(self, serial):
        # add business logic to validate serial
        return False


class ExampleSimpleJobButtonReceiver(JobButtonReceiver):
    class Meta:
        name = "Example Simple Job Button Receiver"

    def receive_job_button(self, obj):
        self.logger.info("Running Job Button Receiver.", obj=obj)
        # Add job logic here


class ExampleComplexJobButtonReceiver(JobButtonReceiver):
    class Meta:
        name = "Example Complex Job Button Receiver"

    def _run_location_job(self, obj):
        self.logger.info("Running Location Job Button Receiver.", obj=obj)
        # Run Location Job function

    def _run_device_job(self, obj):
        self.logger.info("Running Device Job Button Receiver.", obj=obj)
        # Run Device Job function

    def receive_job_button(self, obj):
        user = self.request.user
        if isinstance(obj, Location):
            if not user.has_perm("dcim.add_location"):
                self.logger.error(
                    f"User '{user}' does not have permission to add a Location.",
                    obj=obj,
                )
            else:
                self._run_location_job(obj)
        if isinstance(obj, Device):
            if not user.has_perm("dcim.add_device"):
                self.logger.error(
                    f"User '{user}' does not have permission to add a Device.",
                    obj=obj,
                )
            else:
                self._run_device_job(obj)
        self.logger.error(f"Unable to run Job Button for type {type(obj).__name__}.", obj=obj)


jobs = (
    ExampleDryRunJob,
    ExampleJob,
    ExampleHiddenJob,
    ExampleLoggingJob,
    ExampleJobHookReceiver,
    ExampleSimpleJobButtonReceiver,
    ExampleComplexJobButtonReceiver,
)
register_jobs(*jobs)
