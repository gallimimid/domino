from __future__ import absolute_import, unicode_literals
from celery import shared_task, group
from devices.models import Device
from events.models import Key,Measure
from vmomi.models import VmomiConfig
from pyVmomi import vim, vmodl
import atexit
import ssl
import time
import json
from django.db import transaction
from octospork import *


def get_vim_types(config):

    vim_type_output = {}

    vim_types = config.endpoint_set.order_by('vim_type').values_list('vim_type', flat=True).distinct()
    for vim_type in vim_types:
        vim_type_output[vim_type] = config.endpoint_set.filter(vim_type=vim_type)

def get_service_instances(config):

    vim_type_output = {}
    device_output = {}
    
    
    vim_types = config.endpoint_set.order_by('vim_type').values_list('vim_type', flat=True).distinct()
    for vim_type in vim_types:
        vim_type_output[vim_type] = config.endpoint_set.filter(vim_type=vim_type)
    
    devices = config.group.device_set.all()
    for device in devices:
        try:
            service_instance = get_service_instance(device.ip_address,
                                                    config.user,
                                                    config.password,
                                                    config.port)
            device_output[device.id] = service_instance
        except ConnectionRefusedError:
            key = Key.objects.get(name='comm_loss')
            measure = Measure(device_id=device.id,
                              key=key,
                              value='bad')
            measure.save()
    return vim_type_output, device_output
    
    
@shared_task
def poll(vmomi_config_id):  # pass polling config info into this task
    config = VmomiConfig.objects.get(pk=vmomi_config_id)
    vim_types, devices = get_service_instances(config)
    for device_id, service_instance in devices.items():
        if service_instance:
            for vim_type, endpoints in vim_types.items():
                view = retrieve_content(service_instance, vim_type)
                for endpoint in endpoints:
                    for subview in view:
                        value = {'parent': str(subview.parent),
                                 'object': str(subview.name),
                                 'value': str(deepgetattr(subview, endpoint.attribute))}
                        measure = Measure(device_id=device_id,
                                          key_id=endpoint.key.id,
                                          value=json.dumps(value))
                        measure.save()
            
    discard = Measure.objects.filter(
        device__in=devices).order_by(
        '-time_stamp')[config.max_polls:].values_list("id", flat=True)
    Measure.objects.filter(pk__in=list(discard)).delete()


@shared_task
def discover(ip_address, user_name, password, port):
    service_instance = None
    context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    context.verify_mode = ssl.CERT_NONE

    try:
        service_instance = SmartConnect(host=ip_address,
                                        user=user_name,
                                        pwd=password,
                                        port=int(port),
                                        sslContext=context)
        if service_instance:
            object, created = Device.objects.update_or_create(
                ip_address=ip_address)
    except vmodl.MethodFault as error:
        pass
        
        
@shared_task(name='vmomi.tasks.simple_shutdown')
def simple_shutdown(vmomi_config_id):
    config = VmomiConfig.objects.get(pk=vmomi_config_id)
    vim_types, devices = get_service_instances(config)

    vms = []
    for host, service_instance in devices.items():
        if service_instance:
            vms.extend(get_vms(service_instance))
    shutdown_vms(vms)

    hosts = []
    for host, service_instance in devices.items():
        if service_instance:
            hosts.extend(get_hosts(service_instance))
    enter_maint_mode(hosts)

@shared_task(name='vmomi.tasks.simple_startup')
def simple_startup(vmomi_config_id):
    config = VmomiConfig.objects.get(pk=vmomi_config_id)
    vim_types, devices = get_service_instances(config)

    hosts = []
    for host, service_instance in devices.items():
        if service_instance:
            hosts.extend(get_hosts(service_instance))
    exit_maint_mode(hosts)

    vms = []
    for host, service_instance in devices.items():
        if service_instance:
            vms.extend(get_vms(service_instance))
    start_vms(vms)
