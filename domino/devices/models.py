from django.db import models
import uuid

class Product(models.Model):

    TYPE_CHOICES = (
        ('UPS','UPS'),
        ('PDU','PDU'),
        ('VMG','Virtual Machine Guest'),
        ('VMH','Virtual Machine Host'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    type = models.CharField(max_length=3,choices=TYPE_CHOICES)
    manufacturer = models.CharField(max_length=64)
    product_line = models.CharField(max_length=128, blank=True)
    name = models.CharField(max_length=128)

    def __str__(self):
        return self.name

class Group(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=128)

    def __str__(self):
        return self.name

class Device(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, blank=True)
    description = models.CharField(max_length=128, blank=True)
    department = models.CharField(max_length=64, blank=True)
    owner = models.CharField(max_length=64, blank=True)
    location = models.CharField(max_length=128, blank=True)
    hostname = models.CharField(max_length=63, blank=True)
    ip_address = models.GenericIPAddressField()
    mac_address = models.CharField(max_length=17, blank=True)
    state = models.CharField(max_length=64, blank=True)

    def __str__(self):
        if self.hostname:
            return self.hostname
        else:
            return self.ip_address
