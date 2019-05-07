from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django_celery_beat.models import PeriodicTask,IntervalSchedule
import uuid

class ProtocolConfig(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    device_group = models.ForeignKey('devices.Group', on_delete=models.CASCADE)
    port = models.IntegerField(default=161,validators=[MinValueValidator(1),MaxValueValidator(65535)])
    community_string = models.CharField(max_length=128)
    max_polls = models.IntegerField(default=100,validators=[MinValueValidator(1),MaxValueValidator(1000)])
    periodic_task = models.OneToOneField(PeriodicTask,on_delete=models.CASCADE,null=True)
    
    def __str__(self):
        if self.periodic_task:
            return self.periodic_task.name
        else:
            return str(self.id)

class Address(models.Model): 
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    protocol_config = models.ForeignKey(ProtocolConfig, on_delete=models.CASCADE)
    key = models.ForeignKey('events.Key', on_delete=models.CASCADE,null=True)
    address = models.CharField(max_length=128)

    def __str__(self):
        return str(self.key)
