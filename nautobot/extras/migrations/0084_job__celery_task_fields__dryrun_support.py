# Generated by Django 3.2.18 on 2023-04-13 14:50

from django.db import migrations, models

import nautobot.core.celery.encoders


class Migration(migrations.Migration):
    dependencies = [
        ("extras", "0083_job_result__result_data_migration"),
    ]

    operations = [
        migrations.RenameField(
            model_name="job",
            old_name="commit_default_override",
            new_name="dryrun_default_override",
        ),
        migrations.RenameField(
            model_name="job",
            old_name="commit_default",
            new_name="dryrun_default",
        ),
        migrations.AlterField(
            model_name="job",
            name="dryrun_default",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="job",
            name="supports_dryrun",
            field=models.BooleanField(default=False),
        ),
        migrations.RemoveField(
            model_name="job",
            name="read_only_override",
        ),
        migrations.RemoveField(
            model_name="jobresult",
            name="data",
        ),
        migrations.RemoveField(
            model_name="jobresult",
            name="obj_type",
        ),
        migrations.RemoveField(
            model_name="jobresult",
            name="periodic_task_name",
        ),
        migrations.RemoveField(
            model_name="jobresult",
            name="task_id",
        ),
        migrations.AddField(
            model_name="jobresult",
            name="celery_kwargs",
            field=models.JSONField(
                blank=True, default=dict, encoder=nautobot.core.celery.encoders.NautobotKombuJSONEncoder
            ),
        ),
        migrations.AddField(
            model_name="scheduledjob",
            name="celery_kwargs",
            field=models.JSONField(
                blank=True, default=dict, encoder=nautobot.core.celery.encoders.NautobotKombuJSONEncoder
            ),
        ),
        migrations.AlterField(
            model_name="job",
            name="read_only",
            field=models.BooleanField(default=False, editable=False),
        ),
        migrations.AlterField(
            model_name="job",
            name="supports_dryrun",
            field=models.BooleanField(default=False, editable=False),
        ),
        migrations.AlterField(
            model_name="jobresult",
            name="task_args",
            field=models.JSONField(
                blank=True, default=list, encoder=nautobot.core.celery.encoders.NautobotKombuJSONEncoder
            ),
        ),
        migrations.AlterField(
            model_name="jobresult",
            name="task_kwargs",
            field=models.JSONField(
                blank=True, default=dict, encoder=nautobot.core.celery.encoders.NautobotKombuJSONEncoder
            ),
        ),
        migrations.AlterField(
            model_name="jobresult",
            name="result",
            field=models.JSONField(
                blank=True, editable=False, null=True, encoder=nautobot.core.celery.encoders.NautobotKombuJSONEncoder
            ),
        ),
    ]
