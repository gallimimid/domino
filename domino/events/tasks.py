from __future__ import absolute_import, unicode_literals
from celery import shared_task,chain,group
from celery.execute import send_task
from devices.models import Device
from automations.models import Automation
from events.models import Measure, Event, EventDefinition
import json
from django.utils import timezone

def evaluate_condition(condition):
    if condition == '&&': # all
        return lambda x: all(x)
    if condition == '||': # any
        return lambda x: any(x)


def evaluate_operator(operator):
    if operator == '==': # equal to
        return lambda x, y: x == y
    if operator == '!=': # not equal to
        return lambda x, y: x != y
    if operator == '>': # greater than
        return lambda x, y: int(x) > int(y)
    if operator == '<': # less than
        return lambda x, y: int(x) < int(y)
    if operator == '>=': # greater than or equal to
        return lambda x, y: int(x) >= int(y)
    if operator == '<=': # less than or equal to
        return lambda x, y: int(x) <= int(y)
    if operator == '.*': # contains
        return lambda x, y: x in y
    if operator == '!*': # does not contain
        return lambda x, y: x not in y
    if operator == '^*': # starts with
        return lambda x, y: x.startswith(y)
    if operator == '*$': # ends with
        return lambda x, y: x.endswith(y)


def trigger_event(device, event):
    event_source = Device.objects.get(ip_address=device.ip_address)
    event_definition = EventDefinition.objects.get(name=event)
    event_write = Event(event_definition = event_definition, device = event_source)
    event_write.save()
    
    automations = Automation.objects.filter(cause=event_definition,source_group=event_source.group)
    for automation in automations:
        event_target = automation.target_group
        vmomi_config_id = [str(event_target.vmomiconfig.id)]
        send_task(automation.effect,args=vmomi_config_id)


@shared_task(name='events.tasks.evaluate_measures')
def evaluate_measures():
    # get all event definitions
    event_definitions =  EventDefinition.objects.all()
    measurements = Measure.objects.all()
    devices = Device.objects.all()
    for device in devices:
        measurements_by_device = measurements.filter(device = device)
        for event_definition in event_definitions:
            # get triggers for each event definition
            triggers = event_definition.trigger_set.all()
            # initialize trigger container
            trigger_container = []
            for trigger in triggers:
                # get measurements for trigger key and hysteresis
                measurements_by_keys = measurements_by_device.filter(key = trigger.key)
                if measurements_by_keys:
                    # number of data points returned in hysteresis period
                    points = measurements_by_keys.filter(
                        time_stamp__gt = timezone.now() - trigger.hysteresis
                        ).count()
                    # add one data point previous
                    hysteresis_measurements = measurements_by_keys.order_by(
                        '-time_stamp')[:points+1]
                    # evaluate measurements against trigger value
                    measurement_container = []
                    for measurement in hysteresis_measurements:
                        if type(measurement.value) is dict:
                            measure_value = measurement.value['value']
                        else:
                            measure_value = measurement.value
                        if evaluate_operator(trigger.operator)(measure_value,trigger.value):
                            measurement_container.append(True)
                        else:
                            measurement_container.append(False)
                    if all(measurement_container):
                        trigger_container.append(True)
                    else:
                        trigger_container.append(False)
                else:
                    trigger_container.append(False)
            current_trigger = evaluate_condition(event_definition.condition)(trigger_container)
            device_events = Event.objects.filter(
                device=device,
                event_definition=event_definition
                )
            if device_events:
                previous_event = device_events.latest('time_stamp')
                previous_trigger = previous_event.triggered
            else:
                previous_trigger = False
            if ((current_trigger and not previous_trigger) or
                (current_trigger and event_definition.retriggerable)):
                trigger_event(device,event_definition.name)
            elif not current_trigger and previous_trigger:
                previous_event.triggered = False
                previous_event.save()
            
    return None
