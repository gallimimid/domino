"""
vSphere Python SDK methods for automating virtual environments
"""
from pyvim.connect import SmartConnect, Disconnect
from pyVmomi import vim, vmodl
from pysnmp.hlapi import *

import argparse
import atexit
import getpass
import sys,time
import smtplib,ssl
import settings


def deepgetattr(obj, attr):
    """Recurses through an attribute chain to get the ultimate value."""
    return reduce(getattr, attr.split('.'), obj)

def send_email(subject, message = ''):
    print(subject)
    print(message)

    sender = settings.EMAIL_FROM
    recipients = settings.EMAIL_TO
    recipient_str = ''.join('<' + recipient + '>' for recipient in recipients)
    
    if settings.SMTP_USE_TLS or settings.SMTP_USE_SSL:
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
    
    email_message = settings.EMAIL_MESSAGE.format(sender=sender,to=recipient_str,subject=subject,message=message)

    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
        if settings.SMTP_USE_TLS:
            server.starttls(context=context)
        if settings.DEBUG:
            server.set_debuglevel(True)
        server.sendmail(sender, recipients, email_message)
    
def snmp_get(url,port,community_string,mib):
    value = None
    errorIndication, errorStatus, errorIndex, varBinds = next(
        getCmd(SnmpEngine(),
               CommunityData(community_string, mpModel=0),
               UdpTransportTarget((url, port)),
               ContextData(),
               ObjectType(ObjectIdentity(mib['oid']))
        )
    )
    if errorIndication:
        print(errorIndication)
    elif errorStatus:
        print('%s at %s' % (errorStatus.prettyPrint(),
                            errorIndex and varBinds[int(errorIndex) - 1][0] or '?'))
    else:
        oid,value = varBinds[0]
    return value

def get_service_instance(host,user,password,port=443):

    service_instance = None
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE

    try:
        service_instance = SmartConnect(host=host,
                                        user=user,
                                        pwd=password,
                                        port=int(port),
                                        sslContext=context)
        if not service_instance:
            print("Could not authenticate with the specified ESXi host using "
                  "the supplied credentials")
        atexit.register(Disconnect, service_instance)
        
    except vmodl.MethodFault as error:
        print("Caught vmodl fault : " + error.msg)

    except TimeoutError:
        print('Connection timeout to Vsphere')
    return service_instance

"""
Retrieve content from the service instance.
vim_types is a list containing the following objects
vim.Datacenter
vim.ClusterComputeResource
vim.HostSystem
vim.VirtualMachine
vim.Datastore
vim.ResourcePool
vim.Folder
vim.Network
"""
def retrieve_content(service_instance,vim_types):
    content = service_instance.RetrieveContent()
    container = content.viewManager.CreateContainerView(
        content.rootFolder,
        vim_types,
        True)
        
    view = container.view
    container.DestroyView()
    return view

def get_vms(service_instance):

    try:
        content = service_instance.RetrieveContent()
        container = content.viewManager.CreateContainerView(
            content.rootFolder,
            [vim.VirtualMachine],
            True)
        
        vms = container.view
        container.DestroyView()
        
    except vmodl.MethodFault as error:
        print("Caught vmodl fault : " + error.msg)
    
    return vms

def get_hosts(service_instance):

    try:
        content = service_instance.RetrieveContent()
        container = content.viewManager.CreateContainerView(
            content.rootFolder,
            [vim.HostSystem],
            True)
        
        hosts = container.view
        container.DestroyView()
        
    except vmodl.MethodFault as error:
        print("Caught vmodl fault : " + error.msg)
    
    return hosts

def get_failed_tools(vms):
    try:
        bad_vms = None
        
        if any([vm.guest.toolsStatus != 'toolsOk' and 
                vm.guest.guestState == 'running' 
                for vm in vms]):
            bad_vms = [vm for vm in vms]
            for vm in bad_vms:
                print(vm.name, vm.guest.guestState, vm.guest.toolsStatus)
            
    except vmodl.MethodFault as error:
        print("Caught vmodl fault : " + error.msg)
    
    return bad_vms

def shutdown_vms(vms):
    try:
        for vm in vms:
            if vm.runtime.powerState != vim.VirtualMachinePowerState.poweredOff:
                if vm.guest.toolsStatus == 'toolsOk':
                    vm.ShutdownGuest()
                else:
                    vm.PowerOff()
                
        TasksRunning = True
        while TasksRunning:
            TasksRunning = False
            for vm in vms:
                if vm.runtime.powerState != vim.VirtualMachinePowerState.poweredOff:
                    TasksRunning = True
                    print("Still shutting down VM: {vm_name}".format(vm_name=vm.name))
                else:
                    print("Shutdown  complete for VM: {vm_name}".format(vm_name=vm.name))
            time.sleep(1)
            
    except vmodl.MethodFault as error:
        print("Caught vmodl fault : " + error.msg)

def start_vms(vms):
    try:
        for vm in vms:
            if vm.runtime.powerState == vim.VirtualMachinePowerState.poweredOff:
                vm.PowerOn()
                
        TasksRunning = True
        while TasksRunning:
            TasksRunning = False
            for vm in vms:
                if vm.runtime.powerState == vim.VirtualMachinePowerState.poweredOff:
                    TasksRunning = True
                    print("Still starting VM: {vm_name}".format(vm_name=vm.name))
                else:
                    print("VM started: {vm_name}".format(vm_name=vm.name))
            time.sleep(1)
            
    except vmodl.MethodFault as error:
        print("Caught vmodl fault : " + error.msg)

def enter_maint_mode(hosts):
    try:
        for host in hosts:
            host.EnterMaintenanceMode(0)
                
        TasksRunning = True
        while TasksRunning:
            TasksRunning = False
            for host in hosts:
                if not host.runtime.inMaintenanceMode:
                    TasksRunning = True
                    print("{host_name} still entering maintenance mode".format(host_name=host.name))
                else:
                    print("{host_name} has entered maintenance mode".format(host_name=host.name))
            time.sleep(1)
            
    except vmodl.MethodFault as error:
        print("Caught vmodl fault : " + error.msg)
        
def exit_maint_mode(hosts):
    try:
        for host in hosts:
            host.ExitMaintenanceMode(0)
                
        TasksRunning = True
        while TasksRunning:
            TasksRunning = False
            for host in hosts:
                if host.runtime.inMaintenanceMode:
                    TasksRunning = True
                    print("{host_name} still exiting maintenance mode".format(host_name=host.name))
                else:
                    print("{host_name} has exiting maintenance mode".format(host_name=host.name))
            time.sleep(1)
            
    except vmodl.MethodFault as error:
        print("Caught vmodl fault : " + error.msg)