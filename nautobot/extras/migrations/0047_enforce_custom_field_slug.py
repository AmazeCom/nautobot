# Generated by Django 3.2.14 on 2022-08-01 18:52

from django.db import migrations
import nautobot.core.models.fields


class Migration(migrations.Migration):
    dependencies = [
        ("extras", "0046_populate_custom_field_slug_label"),
    ]

    operations = [
        migrations.AlterField(
            model_name="customfield",
            name="slug",
            field=nautobot.core.models.fields.AutoSlugField(
                blank=False, max_length=50, populate_from="label", unique=True
            ),
        ),
    ]
