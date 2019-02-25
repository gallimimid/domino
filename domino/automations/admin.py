from __future__ import absolute_import, unicode_literals

from django import forms
from django.forms.widgets import Select
from django.contrib import admin
from .models import Automation
from celery import current_app
from celery.utils import cached_property
from django.utils.translation import ugettext_lazy as _

class TaskSelectWidget(Select):
    """Widget that lets you choose between task names."""

    celery_app = current_app
    _choices = None

    def tasks_as_choices(self):
        _ = self._modules  # noqa
        tasks = list(sorted(name for name in self.celery_app.tasks
                            if not name.startswith('celery.')))
        return (('', ''), ) + tuple(zip(tasks, tasks))

    @property
    def choices(self):
        if self._choices is None:
            self._choices = self.tasks_as_choices()
        return self._choices

    @choices.setter
    def choices(self, _):
        # ChoiceField.__init__ sets ``self.choices = choices``
        # which would override ours.
        pass

    @cached_property
    def _modules(self):
        self.celery_app.loader.import_default_modules()


class TaskChoiceField(forms.ChoiceField):
    """Field that lets you choose between task names."""

    widget = TaskSelectWidget

    def valid_value(self, value):
        return True

class EffectTaskForm(forms.ModelForm):
    
    task_effect = TaskChoiceField(
        label = _('Effect'),
        required = False,
    )
    
    effect = forms.CharField(
        label=_('Effect (custom)'),
        required=False,
        max_length=200,
    )

    class Meta:

        model = Automation
        exclude = ()

    def clean(self):
        data = super(EffectTaskForm, self).clean()
        task_effect = data.get('task_effect')
        if task_effect:
            data['task'] = task_effect
        if not data['task']:
            exc = forms.ValidationError(_('Need name of task'))
            self._errors['task'] = self.error_class(exc.messages)
            raise exc
        return data

class AutomationAdmin(admin.ModelAdmin):
    form = EffectTaskForm
    model = Automation
        
admin.site.register(Automation, AutomationAdmin)
