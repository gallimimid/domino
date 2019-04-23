from __future__ import absolute_import, unicode_literals
from celery import shared_task,group
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
    devices = config.group.device_set.all()
    for device in devices:
        print(device,': ',device.id)
        group(burst.s(
        device.id,
        device.ip_address,
        config.port,
        config.community_string,
        address.name,
        address.address)
        for address in config.address_set.all())()
    keep = Measure.objects.filter(
        device__in=devices).order_by(
        '-time_stamp')[:config.max_polls].values_list("id", flat=True)
    Measure.objects.exclude(pk__in=list(keep)).delete()

    
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
    measure = Measure(device_id=device_id, key=key, value=value)
    measure.save()
    return str(ip_address) + ': ' + str(value)

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