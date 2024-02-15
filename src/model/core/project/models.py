import logging
from typing import Any, Dict, Optional

from django.db import models

from model.base_model_manager import BaseModelManager
from model.core.website.models import WebsiteModel, WebsiteModelManager

logger = logging.getLogger(__name__)


class ProjectModelManager(BaseModelManager):

    @staticmethod
    def push(**kwargs: Dict[str, Any]) -> "ProjectModel":
        # Extract base_url and sitemap_url, ensuring they are either str or None
        base_url: Optional[str] = None
        sitemap_url: Optional[str] = None

        if "base_url" in kwargs and isinstance(kwargs["base_url"], str):
            base_url = kwargs.pop("base_url")
        elif "base_url" in kwargs:
            # Handle or log the unexpected type
            logger.error(f"Expected string for base_url, got {type(kwargs['base_url'])}")

        if "sitemap_url" in kwargs and isinstance(kwargs["sitemap_url"], str):
            sitemap_url = kwargs.pop("sitemap_url")
        elif "sitemap_url" in kwargs:
            # Handle or log the unexpected type
            logger.error(f"Expected string for sitemap_url, got {type(kwargs['sitemap_url'])}")

        website: Optional[WebsiteModel] = None

        if base_url is not None:
            website_kwargs = {"base_url": base_url, "sitemap_url": sitemap_url}
            website = WebsiteModelManager.push(**website_kwargs)

        if website is not None:
            identifying_fields: Dict[str, Any] = {
                "data_folder": kwargs.pop("data_folder"),
                "website": website,
            }
            project, created = ProjectModel.objects.update_or_create(defaults=kwargs, **identifying_fields)

            if created:
                logger.info(f"Project {project.name} created successfully.")
            else:
                logger.info(f"Project {project.name} updated successfully.")

            return project
        else:
            # Handle the case where a project can't be created due to missing website
            raise ValueError("A valid website is required to create a project.")

    @staticmethod
    def get_all() -> models.QuerySet:
        return ProjectModel.objects.all()


class ProjectModel(models.Model):
    # fields
    name = models.CharField(max_length=255, unique=True)
    data_folder = models.CharField(max_length=255)

    gsc_auth_email = models.CharField(max_length=255, blank=True, null=True)
    gsc_property_name = models.CharField(max_length=255, blank=True, null=True)

    ga4_auth_email = models.CharField(max_length=255, blank=True, null=True)
    ga4_property_id = models.CharField(max_length=255, blank=True, null=True)

    # relations
    website = models.ForeignKey(WebsiteModel, on_delete=models.CASCADE, related_name="website")

    # system attributes
    created_at = models.DateTimeField(auto_now_add=True)  # auto
    updated_at = models.DateTimeField(auto_now=True)  # auto

    # managers
    objects: models.Manager = ProjectModelManager()

    def __str__(self) -> str:
        return f"Project: {self.name} - Website: {self.website.root_url.full_address} - Data Folder: {self.data_folder}"

    class Meta:
        verbose_name = "Project"
        verbose_name_plural = "Projects"

        db_table = "core_projects"

        unique_together = (
            "data_folder",
            "website",
        )
