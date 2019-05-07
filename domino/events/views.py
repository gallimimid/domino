from django.http import JsonResponse
from events.models import Measure, Event, EventDefinition
from automations.models import Automation
from octospork import *


def measurements(request):
    results = {'results': list(Measure.objects.all().values())}
    return JsonResponse(results)
    
def event(request, device, event):
    trigger_event(device, event)
    results = {'results':'success'}
    return JsonResponse(results)