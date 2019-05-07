from django.contrib import admin
from events.models import *

class TriggerInline(admin.TabularInline):
    model = Trigger

@admin.register(EventDefinition)
class EventDefinitionAdmin(admin.ModelAdmin):
    inlines = [TriggerInline]

admin.site.register(Trigger)
admin.site.register(Event)
admin.site.register(Measure)
admin.site.register(Key)