from django.db import models
import uuid

class ProductModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    type = models.CharField(max_length=64)
    manufacturer = models.CharField(max_length=64)
    product_line = models.CharField(max_length=128)
    name = models.CharField(max_length=128)

    def __str__(self):
        return self.name

class DeviceGroup(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=128)

    def __str__(self):
        return self.name

class Device(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product_model = models.ForeignKey(ProductModel, on_delete=models.CASCADE)
    group = models.ForeignKey(DeviceGroup, on_delete=models.CASCADE)
    description = models.CharField(max_length=128)
    department = models.CharField(max_length=64)
    owner = models.CharField(max_length=64)
    location = models.CharField(max_length=128)
    hostname = models.CharField(max_length=63)
    ip_address = models.GenericIPAddressField()
    mac_address = models.CharField(max_length=17)

    def __str__(self):
        return self.name
