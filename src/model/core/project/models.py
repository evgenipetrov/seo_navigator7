import logging
from typing import Any, Dict, List

from django.db import models

from model.base_model_manager import BaseModelManager
from model.core.website.models import WebsiteModel

logger = logging.getLogger(__name__)


class ProjectModelManager(BaseModelManager):
    def get_field_names(self) -> List[str]:
        return [field.name for field in ProjectModel._meta.fields]

    @staticmethod
    def get_all() -> models.QuerySet:
        return ProjectModel.objects.all()

    def get_instance(self, instance_str: str) -> int:
        try:
            return self.model.objects.get(name=instance_str).id
        except self.model.DoesNotExist:
            logger.error(f"ProjectModel instance with name '{instance_str}' does not exist.")
            return None

    #
    # @staticmethod
    # def push(**kwargs: Dict[str, Any]) -> "ProjectModel":
    #     # Validate identifying fields
    #     identifying_fields = {field: kwargs.pop(field) for field in ProjectModel.IDENTIFYING_FIELDS if field in kwargs}
    #     for field, value in identifying_fields.items():
    #         if value is None or pd.isna(value):  # Using pandas to check for NaN
    #             logger.error(f"Invalid identifying field '{field}' with value '{value}'")
    #             return None  # Or handle this case as appropriate
    #
    #     # Handle missing identifying fields
    #     if not identifying_fields:
    #         logger.error("No identifying fields provided for ProjectModel")
    #         return None  # Or handle this case as appropriate
    #
    #     # Attempt to update or create the ProjectModel instance, handling potential exceptions
    #     try:
    #         kwargs = {k: v for k, v in kwargs.items() if not pd.isna(v)}
    #         model_row, created = ProjectModel.objects.update_or_create(defaults=kwargs, **identifying_fields)
    #         if created:
    #             logger.debug(f"[created instance] {model_row.name}")
    #         else:
    #             logger.debug(f"[updated instance] {model_row.name}")
    #         return model_row
    #     except IntegrityError as e:
    #         logger.error(f"Integrity error while pushing ProjectModel: {e}")
    #     except ValidationError as e:
    #         logger.error(f"Validation error while pushing ProjectModel: {e}")
    #     except Exception as e:
    #         logger.error(f"Unexpected error while pushing ProjectModel: {e}")
    #
    #     return None  # Or handle this case as appropriate


class ProjectModel(models.Model):
    _IDENTIFYING_FIELDS = [
        "website",
        "data_folder",
    ]
    # required relations
    website = models.ForeignKey(WebsiteModel, on_delete=models.CASCADE, related_name="websites")
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
    objects = ProjectModelManager()

    def __str__(self) -> str:
        return self.name

    @property
    def identifying_fields(self) -> Dict[str, Any]:
        """Dynamically constructs a dictionary of identifying fields and their values."""
        return {field: getattr(self, field) for field in self.IDENTIFYING_FIELDS}

    class Meta:
        db_table = "core_projects"

        unique_together = (
            "website",
            "data_folder",
        )
