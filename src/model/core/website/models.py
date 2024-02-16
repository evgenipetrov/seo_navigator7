import logging
from typing import Any, Dict

from django.db import models

from model.base_model_manager import BaseModelManager
from model.core.url.models import UrlModel

logger = logging.getLogger(__name__)


class WebsiteModelManager(BaseModelManager):
    @staticmethod
    def push(**kwargs: Dict[str, Any]) -> "WebsiteModel":
        identifying_fields: Dict[str, Any] = {
            "root_url": kwargs.pop("root_url"),
        }
        website, created = WebsiteModel.objects.update_or_create(defaults=kwargs, **identifying_fields)

        if created:
            logger.debug(f"Website {website} created successfully.")
        else:
            logger.debug(f"Website {website} updated successfully.")

        return website

    @staticmethod
    def get_all() -> models.QuerySet:
        return WebsiteModel.objects.all()


class WebsiteModel(models.Model):
    # required relations
    root_url = models.OneToOneField(UrlModel, on_delete=models.CASCADE, related_name="root_url")  # required
    sitemap_url = models.ForeignKey(UrlModel, on_delete=models.CASCADE, related_name="sitemap_url", null=True, blank=True)
    # required fields
    # optional fields
    # system attributes
    created_at = models.DateTimeField(auto_now_add=True)  # auto
    updated_at = models.DateTimeField(auto_now=True)  # auto
    # model manager
    objects: models.Manager = WebsiteModelManager()

    def __str__(self) -> str:
        return f"WebsiteModel: root_url = {self.root_url}"

    class Meta:
        db_table = "core_websites"
