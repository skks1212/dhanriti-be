# Generated by Django 4.2.3 on 2023-07-18 13:24

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):
    dependencies = [
        ("dhanriti", "0023_leaf_bg_url_leaf_meta_alter_leaf_img_url"),
    ]

    operations = [
        migrations.AddField(
            model_name="leaf",
            name="reads",
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name="notification",
            name="type",
            field=models.IntegerField(
                choices=[
                    (1, "Story Views Milestone"),
                    (2, "Leaf Views Milestone"),
                    (3, "Clap Milestone"),
                    (4, "Comment"),
                    (5, "Follow"),
                    (6, "Comment Reply"),
                    (7, "Part Publish"),
                    (8, "Clap"),
                    (9, "Comment Like"),
                    (10, "Report Judgement"),
                ]
            ),
        ),
        migrations.CreateModel(
            name="LeafRead",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "external_id",
                    models.UUIDField(db_index=True, default=uuid.uuid4, unique=True),
                ),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, db_index=True, null=True),
                ),
                (
                    "modified_at",
                    models.DateTimeField(auto_now=True, db_index=True, null=True),
                ),
                ("deleted", models.BooleanField(db_index=True, default=False)),
                ("reader_ip", models.GenericIPAddressField(blank=True, null=True)),
                (
                    "leaf",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT, to="dhanriti.leaf"
                    ),
                ),
                (
                    "reader",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
    ]
