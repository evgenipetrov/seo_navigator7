import logging
from typing import Any, Dict, Optional

from django.db import models

from model.base_model_manager import BaseModelManager
from model.core.url.models import UrlModel, UrlModelManager

logger = logging.getLogger(__name__)


class WebsiteModelManager(BaseModelManager):
    @staticmethod
    def push(**kwargs: Any) -> "WebsiteModel":
        base_url: Optional[str] = kwargs.pop("base_url", None)
        sitemap_url: Optional[str] = kwargs.pop("sitemap_url", None)

        if base_url is not None:
            root_url = UrlModelManager.get_root_url(base_url)
            root_url_kwargs: Dict[str, Any] = {"full_address": root_url}
            root_url_model: UrlModel = UrlModelManager.push(**root_url_kwargs)

            # Ensure no None values are passed in **kwargs
            sitemap_url_kwargs: Dict[str, Any] = {"full_address": sitemap_url} if sitemap_url else {}
            sitemap_url_model: Optional[UrlModel] = UrlModelManager.push(**sitemap_url_kwargs) if sitemap_url_kwargs else None
            kwargs["root_url"] = root_url_model
            kwargs["sitemap_url"] = sitemap_url_model

        identifying_fields: Dict[str, Any] = {"root_url": kwargs.pop("root_url")}
        website, created = WebsiteModel.objects.update_or_create(defaults=kwargs, **identifying_fields)

        if created:
            logger.info(f"Website {website.root_url.full_address} created successfully.")
        else:
            logger.info(f"Website {website.root_url.full_address} updated successfully.")

        return website

    @staticmethod
    def get_all() -> models.QuerySet:
        return WebsiteModel.objects.all()


class WebsiteModel(models.Model):
    # relations
    root_url = models.OneToOneField(UrlModel, on_delete=models.CASCADE, related_name="root_url")
    sitemap_url = models.ForeignKey(UrlModel, on_delete=models.CASCADE, related_name="sitemap_url", null=True, blank=True)

    # system attributes
    created_at = models.DateTimeField(auto_now_add=True)  # auto
    updated_at = models.DateTimeField(auto_now=True)  # auto

    # managers
    objects: models.Manager = WebsiteModelManager()

    def __str__(self) -> str:
        return self.root_url.full_address

    class Meta:
        verbose_name = "Website"
        verbose_name_plural = "Websites"

        db_table = "core_websites"
