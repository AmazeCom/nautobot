# Generated by Django 3.1.14 on 2022-03-07 17:28

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("extras", "0027_job_gitrepository_data_migration"),
    ]

    operations = [
        migrations.AlterField(
            model_name="job",
            name="source",
            field=models.CharField(db_index=True, editable=False, max_length=16),
        ),
    ]
