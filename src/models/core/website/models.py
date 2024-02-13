import logging

from django.db import models

from models.base_model_manager import BaseModelManager
from models.core.url.models import UrlModelManager, UrlModel

logger = logging.getLogger(__name__)


class WebsiteModelManager(BaseModelManager):
    @staticmethod
    def push(**kwargs) -> "WebsiteModel":
        # process foreign key(s)
        base_url = kwargs.pop("base_url", None)
        sitemap_url = kwargs.pop("sitemap_url", None)
        if base_url is not None:
            base_url = UrlModelManager.get_root_url(base_url)
            root_url_kwargs = {"full_address": base_url}
            root_url = UrlModelManager.push(**root_url_kwargs)
            sitemap_url_kwargs = {"full_address": sitemap_url}
            sitemap_url = UrlModelManager.push(**sitemap_url_kwargs)
            kwargs["root_url"] = root_url
            kwargs["sitemap_url"] = sitemap_url

        # Separate the identifying fields from the updating fields
        identifying_fields = {"root_url": kwargs.pop("root_url")}
        website, created = WebsiteModel.objects.update_or_create(defaults=kwargs, **identifying_fields)

        if created:
            logger.info(f"Website {website.root_url.full_address} created successfully.")
        else:
            logger.info(f"Website {website.root_url.full_address} updated successfully.")

        return website


class WebsiteModel(models.Model):
    # relations
    root_url = models.OneToOneField(UrlModel, on_delete=models.CASCADE, related_name="root_url")
    sitemap_url = models.ForeignKey(UrlModel, on_delete=models.CASCADE, related_name="sitemap_url", null=True, blank=True)

    # system attributes
    created_at = models.DateTimeField(auto_now_add=True)  # auto
    updated_at = models.DateTimeField(auto_now=True)  # auto

    # managers
    objects = WebsiteModelManager()

    def __str__(self):
        return self.root_url.full_address

    class Meta:
        verbose_name = "Website"
        verbose_name_plural = "Websites"

        db_table = "core_websites"
