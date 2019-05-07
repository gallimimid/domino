from django.db import models
import uuid

class Key(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=128)
    
    def __str__(self):
        return self.name


class EventDefinition(models.Model):

    SEVERITY_CHOICES = (
        ('C', 'CRITICAL'),
        ('W', 'Warning'),
        ('I', 'information'),
    )
    
    CONDITION_CHOICES = (
        ('&&', 'All'),
        ('||', 'Any'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=128)
    message = models.CharField(max_length=256)
    severity = models.CharField(max_length=1,choices=SEVERITY_CHOICES)
    condition = models.CharField(max_length=2,choices=CONDITION_CHOICES)
    retriggerable = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class Trigger(models.Model):

    OPERATOR_CHOICES = (
        ('==', 'equal to'),
        ('!=', 'not equal to'),
        ('>', 'greater than'),
        ('<', 'less than'),
        ('>=', 'greater than or equal to'),
        ('<=', 'less than or equal to'),
        ('.*', 'contains'),
        ('!*', 'does not contain'),
        ('^*', 'starts with'),
        ('*$', 'ends with'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    key = models.ForeignKey(Key, on_delete=models.CASCADE)
    operator = models.CharField(max_length=3,choices=OPERATOR_CHOICES)
    value = models.CharField(max_length=128)
    hysteresis = models.DurationField()
    event_definition = models.ForeignKey(EventDefinition, on_delete=models.CASCADE)

    def __str__(self):
        return '{} {} {}'.format(self.key,self.operator,self.value)

class Event(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    time_stamp = models.DateTimeField(auto_now_add=True)
    event_definition = models.ForeignKey(EventDefinition, on_delete=models.CASCADE)
    device = models.ForeignKey('devices.Device', on_delete=models.CASCADE)
    triggered = models.BooleanField(default=True)

    class Meta:
        ordering = ['-time_stamp']

    def __str__(self):
        return '{} - {} - {}'.format(self.time_stamp,self.device,self.event_definition)

class Measure(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    time_stamp = models.DateTimeField(auto_now_add=True)
    key = models.ForeignKey(Key, on_delete=models.CASCADE)
    value = models.CharField(max_length=128)
    device = models.ForeignKey('devices.Device', on_delete=models.CASCADE)
    
    class Meta:
        ordering = ['-time_stamp']

    def __str__(self):
        return '{} - {} - {} - {}'.format(self.device,self.key.name,self.value,self.time_stamp)

measures = {}
