from django.http import JsonResponse
from events.models import Measure, Event, EventDefinition
from events.tasks import trigger_event
from automations.models import Automation
from octospork import *


def measurements(request):
    results = {'results': list(Measure.objects.all().values())}
    return JsonResponse(results)
    
def event(request, group, event):
    trigger_event(group, event)
    results = {'results':'success'}
    return JsonResponse(results)