import logging
from typing import Any, Dict, List

from django.db import models

from model.base_model_manager import BaseModelManager
from model.core.website.models import WebsiteModel

logger = logging.getLogger(__name__)


class ProjectModelManager(BaseModelManager):

    @staticmethod
    def push(**kwargs: Dict[str, Any]) -> "ProjectModel":
        identifying_fields = {field: kwargs.pop(field) for field in ProjectModel.IDENTIFYING_FIELDS if field in kwargs}
        model_row, created = ProjectModel.objects.update_or_create(defaults=kwargs, **identifying_fields)

        if created:
            logger.debug(f"[created instance] {model_row.name}")
        else:
            logger.debug(f"[updated instance] {model_row.name}")

        return model_row

    def get_identifying_fields(self) -> List[str]:
        identifying_fields = self.model.IDENTIFYING_FIELDS
        return identifying_fields

    def get_field_names(self) -> List[str]:
        return [field.name for field in ProjectModel._meta.fields]

    @staticmethod
    def get_all() -> models.QuerySet:
        return ProjectModel.objects.all()


class ProjectModel(models.Model):
    IDENTIFYING_FIELDS = [
        "website",
        "data_folder",
    ]
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
        return self.name

    @property
    def identifying_fields(self) -> Dict[str, Any]:
        """Dynamically constructs a dictionary of identifying fields and their values."""
        return {field: getattr(self, field) for field in self.IDENTIFYING_FIELDS}

    class Meta:
        verbose_name = "Project"
        verbose_name_plural = "Projects"

        db_table = "core_projects"

        unique_together = (
            "website",
            "data_folder",
        )
