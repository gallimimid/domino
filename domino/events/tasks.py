from __future__ import absolute_import, unicode_literals
from celery import shared_task,chain,group,signature
from celery.bin.purge import purge
#from celery.execute import send_task
from devices.models import Device, Group
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


def trigger_event(group_name, event_name):

    event_source = Group.objects.get(name=group_name)
    event_definition = EventDefinition.objects.get(name=event_name)
    event_write = Event(event_definition = event_definition, device_group = event_source)
    event_write.save()
    # completion of automation writes an event which could trigger another automation
    automations = Automation.objects.filter(cause=event_definition,source_group=event_source)
    for automation in automations:
        dummy_result = [None]
        event_target = automation.target_group
        config_id = str(event_target.get_config_id())
        # initialize automation chain with triggered automation
        automation_chain = signature(
            automation.effect,
            args = dummy_result,
            kwargs = {'config_id':config_id}
            )
        a = automation
        while a.next:
            a = a.next
            automation_chain |= (
                signature(
                'events.tasks.evaluate_event',
                kwargs={'group_name':group_name,'event_name':event_name}
                ) |
                signature(
                a.effect,
                kwargs={'config_id':config_id}
                )
            )
        automation_chain.apply_async()

        
@shared_task(name='events.tasks.evaluate_event', bind=True)
def evaluate_event(self, previous, group_name, event_name):
    event_source = Group.objects.get(name=group_name)
    event_definition = EventDefinition.objects.get(name=event_name)
    e = Event.objects.filter(
        device_group = event_source,
        event_definition = event_definition).latest('time_stamp')
    if not e.triggered:
        self.request.chain = None


@shared_task(name='events.tasks.evaluate_measures')
def evaluate_measures():
    # get all event definitions
    event_definitions =  EventDefinition.objects.all()
    measurements = Measure.objects.all()
    device_groups = Group.objects.all()
    for event_definition in event_definitions:
        for group in device_groups:
            device_container = []
            for device in group.device_set.all():
                measurements_by_device = measurements.filter(device = device)
                # get triggers for each event definition
                triggers = event_definition.trigger_set.all()
                if not triggers:
                    continue
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
                            try:
                                measure_json = json.loads(measurement.value)
                                measure_value = measure_json.get('value', measure_json)
                            except:
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
                # test whether any or all triggers are satisfied
                current_trigger = evaluate_condition(event_definition.condition)(trigger_container)
                if current_trigger:
                    device_container.append(True)
                else:
                    device_container.append(False)
            group_trigger = all(device_container)
            # check if there are any existing events for this group
            group_events = Event.objects.filter(
                device_group=group,
                event_definition=event_definition
                )
            if group_events:
                previous_event = group_events.latest('time_stamp')
                previous_trigger = previous_event.triggered
            else:
                previous_trigger = False
            if ((current_trigger and not previous_trigger) or
                (current_trigger and event_definition.retriggerable)):
                trigger_event(group.name,event_definition.name)
            elif not current_trigger and previous_trigger:
                previous_event.triggered = False
                previous_event.save()
                
    return None
