# import logging
#
# from django.db import models
#
# from model.core.project.models import ProjectModel  # Replace with your model
#
# logger = logging.getLogger(__name__)
#
#
# class NewModelManager(models.Manager):
#     def get_all(self) -> models.QuerySet:
#         return self.model.objects.all()
#
#
# class NewModel(models.Model):
#     # required relations
#     project = models.ForeignKey(ProjectModel, on_delete=models.CASCADE, related_name="project")
#     # required fields
#     status_code = models.IntegerField()
#     # optional fields
#     note = models.CharField(max_length=255, blank=True, null=True)
#     # system attributes
#     created_at = models.DateTimeField(auto_now_add=True)  # auto
#     updated_at = models.DateTimeField(auto_now=True)  # auto
#     # model manager
#     objects = NewModelManager()
#
#     def __str__(self) -> str:
#         return f"NewModel: project = {self.project.name}"
#
#     class Meta:
#         db_table = "new_model"
#         unique_together = ("project",)
