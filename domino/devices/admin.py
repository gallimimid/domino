from django.contrib import admin
from .models import Device,Product,Group,Connector

admin.site.register(Device)
admin.site.register(Product)
admin.site.register(Group)
admin.site.register(Connector)
