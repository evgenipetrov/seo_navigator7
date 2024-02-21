import logging
from typing import List
from urllib.parse import urljoin, urlparse

from django.db import models

from model.base_model_manager import BaseModelManager

logger = logging.getLogger(__name__)


class UrlModelManager(BaseModelManager):

    # @staticmethod
    # def push(**kwargs: Dict[str, Any]) -> "UrlModel":
    #     # Validate identifying fields
    #     identifying_fields = {field: kwargs.pop(field) for field in UrlModel.IDENTIFYING_FIELDS if field in kwargs}
    #     for field, value in identifying_fields.items():
    #         if value is None or pd.isna(value):  # Using pandas to check for NaN
    #             logger.error(f"Invalid identifying field '{field}' with value '{value}'")
    #             return None  # Or handle this case as appropriate
    #
    #     # Handle missing identifying fields
    #     if not identifying_fields:
    #         logger.error("No identifying fields provided for UrlModel")
    #         return None  # Or handle this case as appropriately
    #
    #     try:
    #         kwargs = {k: v for k, v in kwargs.items() if not pd.isna(v)}
    #         model_row, created = UrlModel.objects.update_or_create(defaults=kwargs, **identifying_fields)
    #         if created:
    #             logger.debug(f"[created instance] {model_row.full_address}")
    #         else:
    #             logger.debug(f"[updated instance] {model_row.full_address}")
    #         return model_row
    #     except IntegrityError as e:
    #         logger.error(f"Integrity error while pushing UrlModel: {e}")
    #     except ValidationError as e:
    #         logger.error(f"Validation error while pushing UrlModel: {e}")
    #     except Exception as e:
    #         logger.error(f"Unexpected error while pushing UrlModel: {e}")
    #
    #     return None  # Or handle this case as appropriately

    def get_field_names(self) -> List[str]:
        return [field.name for field in UrlModel._meta.fields]

    @staticmethod
    def get_all() -> models.QuerySet:
        return UrlModel.objects.all()

    @staticmethod
    def get_root_url(url: str) -> str:
        parsed_url = urlparse(url)
        root_url_str = f"{parsed_url.scheme}://{parsed_url.netloc}"
        return root_url_str

    @staticmethod
    def get_full_address(root_url: str, path: str) -> str:
        return urljoin(root_url, path)

    @staticmethod
    def is_fragmented(url: str) -> bool:
        return bool(urlparse(url).fragment)

    def get_instance(self, data) -> int:
        if "root_url" in data:
            data["full_address"] = data.pop("root_url")
        if "sitemap_url" in data:
            data["full_address"] = data.pop("sitemap_url")

        kwargs = {k: v for k, v in data.items() if v is not None}
        try:
            return self.model.objects.push(**kwargs)
        except self.model.DoesNotExist:
            full_address = data.get("full_address")
            logger.error(f"UrlModel instance with full_address '{full_address}' does not exist.")
            return None


class UrlModel(models.Model):
    _IDENTIFYING_FIELDS = [
        "full_address",
    ]
    # required relations
    # required fields
    full_address = models.URLField(max_length=200, unique=True)  # required
    # optional fields
    # system attributes
    created_at = models.DateTimeField(auto_now_add=True)  # auto
    updated_at = models.DateTimeField(auto_now=True)  # auto
    # model manager
    objects = UrlModelManager()

    def __str__(self) -> str:
        return self.full_address

    class Meta:
        db_table = "core_urls"
