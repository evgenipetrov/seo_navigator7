# Generated by Django 5.0.2 on 2024-02-13 18:44

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("website", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="ProjectModel",
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
                ("name", models.CharField(max_length=255, unique=True)),
                ("data_folder", models.CharField(max_length=255)),
                (
                    "gsc_auth_email",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                (
                    "gsc_property_name",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                (
                    "ga4_auth_email",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                (
                    "ga4_property_id",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "website",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="website",
                        to="website.websitemodel",
                    ),
                ),
            ],
            options={
                "verbose_name": "Project",
                "verbose_name_plural": "Projects",
                "db_table": "core_projects",
                "unique_together": {("data_folder", "website")},
            },
        ),
    ]
