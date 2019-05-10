from django.db import models
import uuid
from django.utils.translation import ugettext_lazy as _

class Automation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    next = models.ForeignKey('self', on_delete=models.SET_NULL, blank=True, null=True)
    source_group = models.ForeignKey('devices.Group', related_name='source_group',on_delete=models.CASCADE,blank=True,null=True)
    cause = models.ForeignKey('events.EventDefinition', on_delete=models.CASCADE, blank=True, null=True)
    target_group = models.ForeignKey('devices.Group', related_name='target_group', on_delete=models.CASCADE,null=True)
    effect = models.CharField(_('task name'), max_length=200)

    def __str__(self):
        return '{} - {}'.format(self.cause,self.effect)

