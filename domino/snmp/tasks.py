from __future__ import absolute_import, unicode_literals
from celery import shared_task,chain,group
from celery.execute import send_task
from devices.models import Device
from events.models import Measure
import channels.layers
from asgiref.sync import async_to_sync
from snmp.models import ProtocolConfig
from subprocess import run,PIPE
from pysnmp.hlapi import *
import json,time


@shared_task
def poll(protocol_config_id): #pass polling config info into this task
    
    config = ProtocolConfig.objects.get(pk=protocol_config_id)
    devices = config.device_group.device_set.all()
    addresses = config.address_set.all()
    job = group([
        burst.s(
        device.id,
        device.ip_address,
        config.port,
        config.community_string,
        address.key.id,
        address.address)
        for device in devices 
        for address in addresses
        ])
        
    results = job.apply_async()
    
    time.sleep(1)
    while results.waiting():
        time.sleep(1)
        pass

    measures = [
        Measure(
            device_id = result.result['device_id'],
            key_id = result.result['key'],
            value = result.result['value']
        )
        for result in results.results
    ]
    created = Measure.objects.bulk_create(measures)

    send_task('events.tasks.evaluate_measures')

    discard = Measure.objects.filter(
        device__in=devices).order_by(
        '-time_stamp')[config.max_polls:].values_list("id", flat=True)
    Measure.objects.filter(pk__in=list(discard)).delete()
    
@shared_task
def burst(device_id,ip_address,port,community_string,key,oid):
    errorIndication, errorStatus, errorIndex, varBinds = next(
        getCmd(SnmpEngine(),
               CommunityData(community_string, mpModel=0),
               UdpTransportTarget((str(ip_address), port)),
               ContextData(),
               ObjectType(ObjectIdentity(oid))
        )
    )
    if errorIndication:
        value = errorIndication
    elif errorStatus:
        value = '%s at %s' % (errorStatus.prettyPrint(),
                            errorIndex and varBinds[int(errorIndex) - 1][0] or '?')
    else:
        oid,value = varBinds[0]

    return {'device_id':device_id,'key':key,'value':str(value)}

@shared_task
def discover(ip_address,community_string,port,oid):
    errorIndication, errorStatus, errorIndex, varBinds = next(
        getCmd(SnmpEngine(),
               CommunityData(community_string, mpModel=0),
               UdpTransportTarget((ip_address, port)),
               ContextData(),
               ObjectType(ObjectIdentity(oid))
        )
    )

    if errorIndication:
        value = errorIndication
    elif errorStatus:
        value = '%s at %s' % (errorStatus.prettyPrint(),
                            errorIndex and varBinds[int(errorIndex) - 1][0] or '?')
    else:
        object, created = Device.objects.update_or_create(ip_address=ip_address)
        oid,value = varBinds[0]
    return ip_address + ': ' + str(value)#socket.gethostbyaddr
'''
@shared_task
def send_message_task(room_name, message):
    channel_layer = get_channel_layer()

    async_to_sync(channel_layer.group_send)(
        room_name,
        {'type': 'chat_message', 'message': message}
    )
'''
