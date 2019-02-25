from django.contrib import admin
from .models import EventDefinition, Trigger, Event, Measure

class TriggerInline(admin.TabularInline):
    model = Trigger

@admin.register(EventDefinition)
class EventDefinitionAdmin(admin.ModelAdmin):
    inlines = [TriggerInline]

admin.site.register(Trigger)
admin.site.register(Event)
admin.site.register(Measure)
