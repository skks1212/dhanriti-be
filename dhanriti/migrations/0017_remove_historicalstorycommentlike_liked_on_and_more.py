# Generated by Django 4.1.4 on 2023-06-07 04:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dhanriti', '0016_auto_removve_external_id_none'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='historicalstorycommentlike',
            name='liked_on',
        ),
        migrations.RemoveField(
            model_name='storycommentlike',
            name='liked_on',
        ),
        migrations.RemoveField(
            model_name='storyread',
            name='read_time',
        ),
    ]
