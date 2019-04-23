from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django_celery_beat.models import PeriodicTask,IntervalSchedule
import uuid

class VmomiConfig(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    group = models.ForeignKey('devices.Group', on_delete=models.CASCADE)
    port = models.IntegerField(default=443,validators=[MinValueValidator(1),MaxValueValidator(65535)])
    user = models.CharField(max_length=64)
    password = models.CharField(max_length=64)
    session_key = models.CharField(max_length=64, blank=True)
    max_polls = models.IntegerField(default=100,validators=[MinValueValidator(1),MaxValueValidator(1000)])
    periodic_task = models.OneToOneField(PeriodicTask,on_delete=models.CASCADE,null=True)
    
    def __str__(self):
        if self.periodic_task:
            return self.periodic_task.name
        else:
            return str(self.id)

class EndPoint(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    vmomi_config = models.ForeignKey(VmomiConfig, on_delete=models.CASCADE)
    key = models.CharField(max_length=128)
    vim_type = models.CharField(max_length=128)
    attribute = models.CharField(max_length=128)

    def __str__(self):
        return self.name
