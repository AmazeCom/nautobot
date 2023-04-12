from django_celery_results.backends import DatabaseBackend

from nautobot.extras.models import JobResult


class NautobotDatabaseBackend(DatabaseBackend):
    """
    Nautobot extensions to support database integration of Job machinery.
    """

    TaskModel = JobResult

    def encode_content(self, data):
        """Pass through encoding since we're storing as JSON explicitly."""
        return "application/x-nautobot-json", "utf-8", data

    def decode_content(self, obj, content):
        """Pass through decoding since we're storing as JSON explicitly."""
        return content

    def _get_extended_properties(self, request, traceback):
        """
        Overload default so that `argsrepr` and `kwargsrepr` aren't used to construct `args` and `kwargs`.
        Also adds `user_id` passed in on `apply_async` calls.
        """
        extended_props = {
            "periodic_task_name": None,
            "task_args": None,
            "task_kwargs": None,
            "task_name": None,
            "traceback": None,
            "user_id": None,
            "worker": None,
        }
        if request and self.app.conf.find_value_for_key("extended", "result"):
            # do not encode args/kwargs as we store these in a JSONField instead of TextField
            task_args = getattr(request, "args", None)
            task_kwargs = getattr(request, "kwargs", None)

            properties = getattr(request, "properties", {}) or {}
            extended_props.update(
                {
                    "periodic_task_name": properties.get("periodic_task_name", None),
                    "task_args": task_args,
                    "task_kwargs": task_kwargs,
                    "task_name": getattr(request, "task", None),
                    "traceback": traceback,
                    "user_id": properties.get("user_id", None),
                    "worker": getattr(request, "hostname", None),
                }
            )

        return extended_props
