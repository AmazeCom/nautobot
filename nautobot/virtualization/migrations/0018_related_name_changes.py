# Generated by Django 3.2.18 on 2023-02-23 21:44

from django.db import migrations
import django.db.models.deletion
import nautobot.core.models.fields
import nautobot.extras.models.roles
import nautobot.extras.models.statuses
import nautobot.extras.utils


class Migration(migrations.Migration):

    dependencies = [
        ("contenttypes", "0002_remove_content_type_name"),
        ("extras", "0067_created_datetime"),
        ("virtualization", "0017_created_datetime"),
    ]

    operations = [
        migrations.AlterField(
            model_name="virtualmachine",
            name="local_config_context_data_owner_content_type",
            field=nautobot.core.models.fields.ForeignKeyWithAutoRelatedName(
                blank=True,
                default=None,
                limit_choices_to=nautobot.extras.utils.FeatureQuery("config_context_owners"),
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="virtual_machines",
                to="contenttypes.contenttype",
            ),
        ),
        migrations.AlterField(
            model_name="virtualmachine",
            name="local_config_context_schema",
            field=nautobot.core.models.fields.ForeignKeyWithAutoRelatedName(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="virtual_machines",
                to="extras.configcontextschema",
            ),
        ),
        migrations.AlterField(
            model_name="virtualmachine",
            name="role",
            field=nautobot.extras.models.roles.RoleField(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="virtual_machines",
                to="extras.role",
            ),
        ),
        migrations.AlterField(
            model_name="virtualmachine",
            name="status",
            field=nautobot.extras.models.statuses.StatusField(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="virtual_machines",
                to="extras.status",
            ),
        ),
        migrations.AlterField(
            model_name="vminterface",
            name="status",
            field=nautobot.extras.models.statuses.StatusField(
                null=True, on_delete=django.db.models.deletion.PROTECT, related_name="vm_interfaces", to="extras.status"
            ),
        ),
    ]
