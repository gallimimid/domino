from django.urls import path

from . import views

urlpatterns = [
    path('measurements', views.measurements, name='measurements'),
    path('event/<device>/<event>', views.event, name='event'),
]
