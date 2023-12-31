# Generated by Django 4.2.6 on 2023-10-31 21:12

from django.db import migrations, models
import utils.helpers


class Migration(migrations.Migration):
    dependencies = [
        ("dhanriti", "0004_remove_canvas_old_pk_remove_flow_old_pk_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="canvas",
            name="inflow_rate",
            field=models.CharField(
                max_length=255, validators=[utils.helpers.is_valid_crontab_expression]
            ),
        ),
        migrations.AlterField(
            model_name="funnel",
            name="flow_rate",
            field=models.CharField(
                max_length=255,
                null=True,
                validators=[utils.helpers.is_valid_crontab_expression],
            ),
        ),
    ]
