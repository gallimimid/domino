from __future__ import absolute_import, unicode_literals
from celery import shared_task,group
from devices.models import Device,Measure
from vmomi.models import VmomiConfig
from pyVmomi import vim, vmodl
import atexit,ssl,time
from octospork import *


@shared_task
def poll(vmomi_polling_id): #pass polling config info into this task
    config = VmomiConfig.objects.get(pk=vmomi_config_id)
    devices = config.devices.all()

    for device in devices:
        service_instance = get_service_instance(ip_address,
                                                user,
                                                password,
                                                port)
        if service_instance:
            for endpoint in config.endpoint_set.all():
                view = retrieve_content(service_instance, endpoint.vim_type)
                for subview in view:
                    continue
@shared_task
def discover(ip_address,user_name,password,port):
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
            object, created = Device.objects.update_or_create(ip_address=ip_address)
    except vmodl.MethodFault as error:
        pass