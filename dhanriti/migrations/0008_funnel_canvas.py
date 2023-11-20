# Generated by Django 4.2.6 on 2023-11-20 13:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("dhanriti", "0007_canvas_filled_tank_filled"),
    ]

    operations = [
        migrations.AddField(
            model_name="funnel",
            name="canvas",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="canvas",
                to="dhanriti.canvas",
            ),
        ),
    ]
