# Generated by Django 4.2.2 on 2023-07-23 13:43

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):
    dependencies = [
        ("dhanriti", "0023_leaf_bg_url_leaf_meta_alter_leaf_img_url"),
    ]

    operations = [
        migrations.CreateModel(
            name="Preset",
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
                (
                    "type",
                    models.IntegerField(
                        choices=[(1, "Leaf Background"), (2, "Leaf Fonts")], default=1
                    ),
                ),
                ("content", models.JSONField(default=dict)),
                ("priority", models.IntegerField(default=0)),
                ("hidden", models.BooleanField(default=False)),
            ],
            options={
                "abstract": False,
            },
        ),
    ]
