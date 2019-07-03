from django.shortcuts import render
from devices.models import Device
from django.contrib.auth.decorators import login_required

@login_required
def index(request):
    context = {'devices': Device.objects.all()}
    return render(request, 'devices/index.html', context)