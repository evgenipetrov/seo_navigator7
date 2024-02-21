import logging
from typing import Dict, Any

from django.db import models

from model.base_model_manager import BaseModelManager
from model.core.project.models import ProjectModel  # Replace with your model
from model.core.topic.models import TopicModel, TopicModelManager
from model.core.url.models import UrlModel

logger = logging.getLogger(__name__)


class EmergingQueryReportModelManager(BaseModelManager):

    @staticmethod
    def push(**kwargs: Dict[str, Any]) -> "EmergingQueryReportModel":
        # Validate key column
        topic = kwargs.pop("topic", None)
        if topic is None:
            logger.error("No 'topic' provided to push method")
            return None

        topic = TopicModelManager.push(phrase=topic)
        if topic is None:
            logger.error(f"Failed to obtain 'TopicModel' for topic: {topic}")
            return None
        kwargs["topic"] = topic

        # Validate 'response_url'
        response_url = kwargs.pop("response_url", None)
        if response_url and response_url != request_url:
            response_url_model = UrlModelManager.push(full_address=response_url)
            if response_url_model is None:
                logger.error(f"Failed to obtain 'UrlModel' for response_url: {response_url}")
                return None
            kwargs["response_url"] = response_url_model
        else:
            kwargs["response_url"] = request_url_model

        # Validate identifying fields
        identifying_fields = {field: kwargs.pop(field) for field in UrlInventoryReportModel.objects.get_identifying_fields() if field in kwargs}
        if not identifying_fields:
            logger.error("No identifying fields provided for UrlInventoryReportModel")
            return None

        # Attempt to update or create the UrlInventoryReportModel instance, handling potential exceptions
        try:
            kwargs = {k: v for k, v in kwargs.items() if not pd.isna(v)}
            model_row, created = UrlInventoryReportModel.objects.update_or_create(defaults=kwargs, **identifying_fields)
            if created:
                logger.info(f"[created instance] {model_row}")
            else:
                logger.info(f"[updated instance] {model_row}")
            return model_row
        except IntegrityError as e:
            logger.error(f"Integrity error while pushing UrlInventoryReportModel: {e}")
        except ValidationError as e:
            logger.error(f"Validation error while pushing UrlInventoryReportModel: {e}")
        except Exception as e:
            logger.error(f"Unexpected error while pushing UrlInventoryReportModel: {e}")

        return None

    def get_instance(self, instance_str: str) -> int:
        pass

    def get_all(self) -> models.QuerySet:
        return self.model.objects.all()


class EmergingQueryReportModel(models.Model):
    # List of column names that are updated manually by users. These fields might require
    # special handling during data import/export or synchronization processes.
    _MANUAL_FIELDS = [
        "note",
    ]
    _IDENTIFYING_FIELDS = [
        "project",
        "topic",
    ]
    # required relations
    project = models.ForeignKey(ProjectModel, on_delete=models.CASCADE, blank=True, null=True)
    topic = models.ForeignKey(TopicModel, on_delete=models.CASCADE, blank=True, null=True)
    url_last_week = models.ForeignKey(UrlModel, on_delete=models.CASCADE, blank=True, null=True, related_name="page_query_last_week")
    url_last_month = models.ForeignKey(UrlModel, on_delete=models.CASCADE, blank=True, null=True, related_name="page_query_last_month")
    # required fields
    impressions_last_week = models.IntegerField(blank=True, null=True)
    clicks_last_week = models.IntegerField(blank=True, null=True)
    ctr_last_week = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    position_last_week = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    impressions_last_month = models.IntegerField(blank=True, null=True)
    clicks_last_month = models.IntegerField(blank=True, null=True)
    ctr_last_month = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    position_last_month = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    from_last_week = models.BooleanField(default=False)
    from_last_month = models.BooleanField(default=False)
    # optional fields
    note = models.CharField(max_length=255, blank=True, null=True)
    # system attributes
    created_at = models.DateTimeField(auto_now_add=True)  # auto
    updated_at = models.DateTimeField(auto_now=True)  # auto
    # model manager
    objects = EmergingQueryReportModelManager()

    def __str__(self) -> str:
        return f"NewModel: project = {self.project.name}"

    class Meta:
        db_table = "report_emerging_query"
