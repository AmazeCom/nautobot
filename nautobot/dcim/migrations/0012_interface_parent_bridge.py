# Generated by Django 3.2.12 on 2022-04-18 08:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("dcim", "0011_interface_status_data_migration"),
    ]

    operations = [
        migrations.AddField(
            model_name="interface",
            name="parent_interface",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="child_interfaces",
                to="dcim.interface",
            ),
        ),
        migrations.AddField(
            model_name="interface",
            name="bridge",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="bridged_interfaces",
                to="dcim.interface",
            ),
        ),
    ]
