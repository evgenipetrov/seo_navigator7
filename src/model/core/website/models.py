import logging
from typing import Any, Dict, List

import pandas as pd
from django.core.exceptions import ValidationError
from django.db import IntegrityError, models

from model.base_model_manager import BaseModelManager
from model.core.url.models import UrlModel

logger = logging.getLogger(__name__)


class WebsiteModelManager(BaseModelManager):
    @staticmethod
    def push(**kwargs: Dict[str, Any]) -> "WebsiteModel":
        # Validate identifying fields
        identifying_fields = {field: kwargs.pop(field) for field in WebsiteModel.IDENTIFYING_FIELDS if field in kwargs}
        for field, value in identifying_fields.items():
            if value is None or pd.isna(value):  # Using pandas to check for NaN
                logger.error(f"Invalid identifying field '{field}' with value '{value}'")
                return None  # Or handle this case as appropriate

        # Handle missing identifying fields
        if not identifying_fields:
            logger.error("No identifying fields provided for WebsiteModel")
            return None  # Or handle this case as appropriate

        # Attempt to update or create the WebsiteModel instance, handling potential exceptions
        try:
            kwargs = {k: v for k, v in kwargs.items() if not pd.isna(v)}
            model_row, created = WebsiteModel.objects.update_or_create(defaults=kwargs, **identifying_fields)
            if created:
                logger.debug(f"[created instance] {model_row}")
            else:
                logger.debug(f"[updated instance] {model_row}")
            return model_row
        except IntegrityError as e:
            logger.error(f"Integrity error while pushing WebsiteModel: {e}")
        except ValidationError as e:
            logger.error(f"Validation error while pushing WebsiteModel: {e}")
        except Exception as e:
            logger.error(f"Unexpected error while pushing WebsiteModel: {e}")

        return None  # Or handle this case as appropriate

    def get_manual_fields(self):
        pass

    def get_identifying_fields(self) -> List[str]:
        identifying_fields = self.model.IDENTIFYING_FIELDS
        return identifying_fields

    def get_field_names(self) -> List[str]:
        return [field.name for field in WebsiteModel._meta.fields]

    @staticmethod
    def get_all() -> models.QuerySet:
        return WebsiteModel.objects.all()

    def get_instance_id(self, instance_str: str) -> int:
        try:
            return self.model.objects.get(root_url__full_address=instance_str).id
        except self.model.DoesNotExist:
            logger.error(f"WebsiteModel instance with root_url '{instance_str}' does not exist.")
            return None


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
    objects = WebsiteModelManager()

    def __str__(self) -> str:
        return self.root_url.full_address

    class Meta:
        db_table = "core_websites"
