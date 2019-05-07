from django.contrib import admin

from .models import VmomiConfig,EndPoint

admin.site.register(VmomiConfig)
admin.site.register(EndPoint)
