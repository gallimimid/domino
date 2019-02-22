from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django_celery_beat.models import PeriodicTask,IntervalSchedule
import uuid

class ProtocolConfig(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    device_group = models.ForeignKey('devices.DeviceGroup', on_delete=models.CASCADE)
    port = models.IntegerField(default=161,validators=[MinValueValidator(1),MaxValueValidator(65535)])
    community_string = models.CharField(max_length=128)
    periodic_task = models.OneToOneField(PeriodicTask,on_delete=models.CASCADE,null=True)
    
    def __str__(self):
        if self.periodic_task:
            return self.periodic_task.name
        else:
            return str(self.id)

class Address(models.Model): # add translation capabilities
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    protocol_config = models.ForeignKey(ProtocolConfig, on_delete=models.CASCADE)
    name = models.CharField(max_length=128)
    address = models.CharField(max_length=128)

    def __str__(self):
        return self.name
