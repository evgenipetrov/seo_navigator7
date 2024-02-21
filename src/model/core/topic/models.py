import logging

from django.db import models

from model.base_model_manager import BaseModelManager

logger = logging.getLogger(__name__)


class TopicModelManager(BaseModelManager):
    @staticmethod
    def push(**kwargs) -> "TopicModel":
        # Validate identifying fields
        identifying_fields = {field: kwargs.pop(field) for field in TopicModel.IDENTIFYING_FIELDS if field in kwargs}
        if not identifying_fields:
            logger.error("No identifying fields provided for TopicModel")
            return None

        # Attempt to update or create the TopicModel instance, handling potential exceptions
        try:
            model_row, created = TopicModel.objects.update_or_create(defaults=kwargs, **identifying_fields)
            if created:
                logger.info(f"[created instance] {model_row}")
            else:
                logger.info(f"[updated instance] {model_row}")
            return model_row
        except models.IntegrityError as e:
            logger.error(f"Integrity error while pushing TopicModel: {e}")
        except models.ValidationError as e:
            logger.error(f"Validation error while pushing TopicModel: {e}")
        except Exception as e:
            logger.error(f"Unexpected error while pushing TopicModel: {e}")

        return None

    def get_all(self) -> models.QuerySet:
        return self.model.objects.all()

    def get_instance(self, instance_str: str) -> int:
        try:
            return self.model.objects.get(phrase=instance_str).id
        except self.model.DoesNotExist:
            logger.error(f"UrlModel instance with full_address '{instance_str}' does not exist.")
            return None


class TopicModel(models.Model):
    IDENTIFYING_FIELDS = [
        "phrase",
    ]
    # required relations
    # required fields
    phrase = models.CharField(max_length=255, unique=True)  # required
    # optional fields
    # system attributes
    created_at = models.DateTimeField(auto_now_add=True)  # auto
    updated_at = models.DateTimeField(auto_now=True)  # auto
    # model manager
    objects = TopicModelManager()

    def __str__(self) -> str:
        return self.phrase

    class Meta:
        db_table = "core_topics"
