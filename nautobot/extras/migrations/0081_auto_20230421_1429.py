# Generated by Django 3.2.18 on 2023-04-21 19:29

from django.db import migrations, models

import nautobot.core.celery


class Migration(migrations.Migration):
    dependencies = [
        ("extras", "0080_job_result__result_data_migration"),
    ]

    operations = [
        migrations.AddField(
            model_name="jobresult",
            name="celery_kwargs",
            field=models.JSONField(blank=True, encoder=nautobot.core.celery.NautobotKombuJSONEncoder, null=True),
        ),
        migrations.AddField(
            model_name="scheduledjob",
            name="celery_kwargs",
            field=models.JSONField(blank=True, encoder=nautobot.core.celery.NautobotKombuJSONEncoder, null=True),
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
    ]
