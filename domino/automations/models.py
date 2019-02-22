from django.db import models
import uuid
from django.utils.translation import ugettext_lazy as _

class Automation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cause = models.ForeignKey('events.EventDefinition', on_delete=models.CASCADE)
    effect = models.CharField(_('task name'), max_length=200)

    def __str__(self):
        return '{} - {}'.format(self.cause,self.effect)

