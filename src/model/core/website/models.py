import logging
from typing import Any, Dict, List

from django.db import models

from model.base_model_manager import BaseModelManager
from model.core.url.models import UrlModel

logger = logging.getLogger(__name__)


class WebsiteModelManager(BaseModelManager):
    @staticmethod
    def push(**kwargs: Dict[str, Any]) -> "WebsiteModel":
        identifying_fields = {field: kwargs.pop(field) for field in WebsiteModel.IDENTIFYING_FIELDS if field in kwargs}
        model_row, created = WebsiteModel.objects.update_or_create(defaults=kwargs, **identifying_fields)

        if created:
            logger.debug(f"[created instance] {model_row}")
        else:
            logger.debug(f"[updated instance] {model_row}")

        return model_row

    def get_identifying_fields(self) -> List[str]:
        identifying_fields = self.model.IDENTIFYING_FIELDS
        return identifying_fields

    def get_field_names(self) -> List[str]:
        return [field.name for field in WebsiteModel._meta.fields]

    @staticmethod
    def get_all() -> models.QuerySet:
        return WebsiteModel.objects.all()


class WebsiteModel(models.Model):
    IDENTIFYING_FIELDS = [
        "root_url",
    ]
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
        return self.root_url.full_address

    class Meta:
        db_table = "core_websites"
