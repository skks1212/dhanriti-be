# Generated by Django 4.2.4 on 2023-08-29 16:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dhanriti', '0041_asset'),
    ]

    operations = [
        migrations.AddField(
            model_name='leaf',
            name='preference_points',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='story',
            name='preference_points',
            field=models.IntegerField(default=0),
        ),
    ]
