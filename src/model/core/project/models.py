import logging
from typing import Any, Dict

from django.db import models

from model.base_model_manager import BaseModelManager
from model.core.website.models import WebsiteModel

logger = logging.getLogger(__name__)


class ProjectModelManager(BaseModelManager):

    @staticmethod
    def push(**kwargs: Dict[str, Any]) -> "ProjectModel":
        identifying_fields: Dict[str, Any] = {
            "data_folder": kwargs.pop("data_folder"),
            "website": kwargs.pop("website"),
        }
        project, created = ProjectModel.objects.update_or_create(defaults=kwargs, **identifying_fields)

        if created:
            logger.debug(f"Project {project.name} created successfully.")
        else:
            logger.debug(f"Project {project.name} updated successfully.")

        return project

    @staticmethod
    def get_all() -> models.QuerySet:
        return ProjectModel.objects.all()


class ProjectModel(models.Model):
    # required relations
    website = models.ForeignKey(WebsiteModel, on_delete=models.CASCADE, related_name="website")
    # required fields
    name = models.CharField(max_length=255, unique=True)
    data_folder = models.CharField(max_length=255)
    # optional fields
    gsc_auth_email = models.CharField(max_length=255, blank=True, null=True)
    gsc_property_name = models.CharField(max_length=255, blank=True, null=True)
    ga4_auth_email = models.CharField(max_length=255, blank=True, null=True)
    ga4_property_id = models.CharField(max_length=255, blank=True, null=True)
    # system attributes
    created_at = models.DateTimeField(auto_now_add=True)  # auto
    updated_at = models.DateTimeField(auto_now=True)  # auto
    # model manager
    objects: models.Manager = ProjectModelManager()

    def __str__(self) -> str:
        return f"ProjectModel: website = {self.website}"

    class Meta:
        verbose_name = "Project"
        verbose_name_plural = "Projects"

        db_table = "core_projects"

        unique_together = (
            "website",
            "data_folder",
        )
