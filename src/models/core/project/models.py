import logging

from django.db import models

from models.base_model_manager import BaseModelManager
from models.core.website.models import WebsiteModelManager, WebsiteModel

logger = logging.getLogger(__name__)


class ProjectModelManager(BaseModelManager):
    @staticmethod
    def push(**kwargs) -> "ProjectModel":
        # process foreign key(s)
        base_url = kwargs.pop("base_url", None)
        sitemap_url = kwargs.pop("sitemap_url", None)
        if base_url is not None:
            website_kwargs = {"base_url": base_url, "sitemap_url": sitemap_url}
            website = WebsiteModelManager.push(**website_kwargs)
            kwargs["website"] = website

        # Separate the identifying fields from the updating fields
        identifying_fields = {
            "data_folder": kwargs.pop("data_folder"),
            "website": kwargs["website"],
        }
        project, created = ProjectModel.objects.update_or_create(defaults=kwargs, **identifying_fields)

        if created:
            logger.info(f"Project {project.name} created successfully.")
        else:
            logger.info(f"Project {project.name} updated successfully.")

        return project


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
    objects = ProjectModelManager()

    def __str__(self):
        return f"Project: {self.name} - Website: {self.website.root_url.full_address} - Data Folder: {self.data_folder}"

    class Meta:
        verbose_name = "Project"
        verbose_name_plural = "Projects"

        db_table = "core_projects"

        unique_together = (
            "data_folder",
            "website",
        )
