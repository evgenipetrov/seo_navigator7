import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Tuple, Type, List

import pandas as pd
from django.db import models

logger = logging.getLogger(__name__)


class BaseModelManager(models.Manager, ABC):
    def __init__(self, *args: Tuple[Any, ...], **kwargs: Dict[str, Any]) -> None:
        super().__init__(*args, **kwargs)

    def push(self, **kwargs: Any) -> Optional[models.Model]:
        logger.debug(f"Entering push method of {self.__class__.__name__} with kwargs: {kwargs}")
        kwargs = {k: v for k, v in kwargs.items() if not pd.isna(v)}
        logger.debug(f"Cleaned kwargs: {kwargs}")
        related_data = {}
        nested_properties = {}
        for key, value in list(kwargs.items()):  # Create a copy for iteration
            if "__" in key:
                nested_property = kwargs.pop(key)  # Modify the original dictionary
                main_obj, nested_prop = key.split("__", 1)
                nested_properties[main_obj] = {nested_prop: nested_property}
        for field in self.model._meta.fields:
            logger.debug(f"Processing field: {field.name}")
            if isinstance(field, models.BigAutoField):
                continue
            if (isinstance(field, models.ForeignKey) or isinstance(field, models.OneToOneField)) and field.name in kwargs:
                if field.name in nested_properties:
                    related_data = nested_properties[field.name]
                related_data[field.name] = kwargs[field.name]
                related_manager = field.related_model.objects
                logger.debug(f"Related data for field {field.name}: {related_data}")

                if not isinstance(related_data, models.Model):
                    if hasattr(related_manager, "get_instance"):
                        related_instance = related_manager.get_instance(related_data)
                        logger.debug(f"Related instance ID for field {field.name}: {related_instance.id}")
                        kwargs[field.name] = related_instance
                    else:
                        logger.error(f"The manager for {field.related_model.__name__} does not implement 'get_instance_id'.")
                        return None
                else:
                    kwargs[field.name] = related_data[field.name]

        identifying_fields = {field.name: kwargs.pop(field.name) for field in self.model._meta.fields if field.name in self.get_identifying_fields()}
        logger.debug(f"Identifying fields: {identifying_fields}")

        try:
            model_instance, created = self.model.objects.update_or_create(defaults=kwargs, **identifying_fields)
            if created:
                logger.debug(f"[{self.model.__name__} created] {model_instance}")
            else:
                logger.debug(f"[{self.model.__name__} updated] {model_instance}")
            return model_instance
        except Exception as e:
            logger.error(f"Unexpected error while pushing {self.model.__name__}: {e}")

        logger.debug("Exiting push method")
        return None

    # def push(self, **kwargs: Any) -> Optional[models.Model]:
    #     logger.debug(f"Entering push method of {self.__class__.__name__} with kwargs: {kwargs}")
    #     kwargs = {k: v for k, v in kwargs.items() if not pd.isna(v)}
    #     logger.debug(f"Cleaned kwargs: {kwargs}")
    #
    #     nested_properties = {}
    #     for key, value in list(kwargs.items()):  # Create a copy for iteration
    #         if "__" in key:
    #             nested_property = kwargs.pop(key)  # Modify the original dictionary
    #             main_obj, nested_prop = key.split("__", 1)
    #             nested_properties[main_obj] = nested_prop
    #
    #     for field in self.model._meta.fields:
    #         logger.debug(f"Processing field: {field.name}")
    #         if isinstance(field, models.BigAutoField):
    #             continue
    #         if (isinstance(field, models.ForeignKey) or isinstance(field, models.OneToOneField)) and field.name in kwargs:
    #             related_data = kwargs[field.name]
    #             related_manager = field.related_model.objects
    #             logger.debug(f"Related data for field {field.name}: {related_data}")
    #
    #             if not isinstance(related_data, models.Model):
    #                 if hasattr(related_manager, "get_instance"):
    #                     related_instance = related_manager.get_instance(related_data)
    #                     logger.debug(f"Related instance ID for field {field.name}: {related_instance.id}")
    #                     kwargs[field.name] = related_instance
    #                 else:
    #                     logger.error(f"The manager for {field.related_model.__name__} does not implement 'get_instance_id'.")
    #                     return None
    #
    #     identifying_fields = {field.name: kwargs.pop(field.name) for field in self.model._meta.fields if field.name in self.get_identifying_fields()}
    #     logger.debug(f"Identifying fields: {identifying_fields}")
    #
    #     try:
    #         model_instance, created = self.model.objects.update_or_create(defaults=kwargs, **identifying_fields)
    #         if created:
    #             logger.debug(f"[{self.model.__name__} created] {model_instance}")
    #         else:
    #             logger.debug(f"[{self.model.__name__} updated] {model_instance}")
    #         return model_instance
    #     except Exception as e:
    #         logger.error(f"Unexpected error while pushing {self.model.__name__}: {e}")
    #
    #     logger.debug("Exiting push method")
    #     return None

    # def push(self, **kwargs: Any) -> Optional[models.Model]:
    #     logger.debug(f"Entering push method of {self.__class__.__name__} with kwargs: {kwargs}")
    #     kwargs = {k: v for k, v in kwargs.items() if not pd.isna(v)}
    #     logger.debug(f"Cleaned kwargs: {kwargs}")
    #
    #     for field in self.model._meta.fields:
    #         logger.debug(f"Processing field: {field.name}")
    #         if isinstance(field, models.BigAutoField):
    #             continue
    #         if (isinstance(field, models.ForeignKey) or isinstance(field, models.OneToOneField)) and field.name in kwargs:
    #             related_data = kwargs[field.name]
    #             related_manager = field.related_model.objects
    #             logger.debug(f"Related data for field {field.name}: {related_data}")
    #
    #             if not isinstance(related_data, models.Model):
    #                 if hasattr(related_manager, "get_instance"):
    #                     related_instance = related_manager.get_instance(related_data)
    #                     logger.debug(f"Related instance ID for field {field.name}: {related_instance.id}")
    #                     kwargs[field.name] = related_instance
    #                 else:
    #                     logger.error(f"The manager for {field.related_model.__name__} does not implement 'get_instance_id'.")
    #                     return None
    #
    #     identifying_fields = {field.name: kwargs.pop(field.name) for field in self.model._meta.fields if field.name in self.get_identifying_fields()}
    #     logger.debug(f"Identifying fields: {identifying_fields}")
    #
    #     try:
    #         model_instance, created = self.model.objects.update_or_create(defaults=kwargs, **identifying_fields)
    #         if created:
    #             logger.debug(f"[{self.model.__name__} created] {model_instance}")
    #         else:
    #             logger.debug(f"[{self.model.__name__} updated] {model_instance}")
    #         return model_instance
    #     except IntegrityError as e:
    #         logger.error(f"Integrity error while pushing {self.model.__name__}: {e}")
    #     except ValidationError as e:
    #         logger.error(f"Validation error while pushing {self.model.__name__}: {e}")
    #     except Exception as e:
    #         logger.error(f"Unexpected error while pushing {self.model.__name__}: {e}")
    #
    #     logger.debug("Exiting push method")
    #     return None

    @staticmethod
    @abstractmethod
    def get_all() -> models.QuerySet:
        pass

    def get_instance_by_id(self, instance_id: int) -> models.Model:
        return self.get(id=instance_id)

    def get_manual_fields(self) -> List[str]:
        return self.model._MANUAL_FIELDS

    def get_identifying_fields(self) -> List[str]:
        return self.model._IDENTIFYING_FIELDS

    @abstractmethod
    def get_instance(self, instance_str: str) -> int:
        pass

    def get_field_names(self) -> List[str]:
        return [field.name for field in self.model._meta.fields]

    def get_foreign_key_fields(self) -> Dict[str, Type[models.Model]]:
        return {field.name: field.related_model for field in self.model._meta.fields if field.is_relation}
