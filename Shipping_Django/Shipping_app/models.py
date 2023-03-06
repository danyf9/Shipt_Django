from time import time

from django.db import models

# Create your models here.


def auto_id():
    return int(time())


class Item(models.Model):

    id = models.PositiveIntegerField(primary_key=True, default=auto_id)
    name = models.CharField(max_length=50)
    description = models.TextField(max_length=200)

    shipment = models.ManyToManyField(to='Shipment', related_name='Shipment_Item')

    class Meta:
        db_table = 'Items'

    def __str__(self):
        return f'[{self.id}] {self.name}'


class Shipment(models.Model):

    id = models.PositiveIntegerField(primary_key=True, default=auto_id)
    order_date = models.DateField(auto_now_add=True)

    class Meta:
        db_table = 'Shipments'

    def __str__(self):
        return f'Shipment {self.id}'
