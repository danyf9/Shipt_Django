from time import time
from django.db import models
from django.contrib.auth.models import User

# Create your models here.


def auto_id():
    return int(time())


class Item(models.Model):

    id = models.PositiveIntegerField(primary_key=True, default=auto_id)
    name = models.CharField(max_length=50, null=False)
    description = models.TextField(max_length=200, null=False)
    price = models.PositiveIntegerField(null=False)
    image = models.CharField(max_length=100, null=True)

    class Meta:
        db_table = 'ItemsAPI'

    def __str__(self):
        return f'[{self.id}] {self.name}'


class Shipment(models.Model):

    id = models.PositiveIntegerField(primary_key=True, default=auto_id)
    order_date = models.DateField(auto_now_add=True)
    user = models.ForeignKey(to=User, related_name='User_shipment', on_delete=models.RESTRICT,
                             null=True, blank=True)

    class Meta:
        db_table = 'Shipments'

    def __str__(self):
        return f'Shipment {self.id}'


class ShipmentList(models.Model):

    shipment = models.ForeignKey(to=Shipment, related_name="list_shipment",
                                 on_delete=models.RESTRICT)
    item = models.ForeignKey(to=Item, related_name="list_item",
                             on_delete=models.RESTRICT)


class Categories(models.Model):

    categories = [('TECH', 'Technology'),
                  ('TOY', 'Toys'),
                  ('CLOTH', 'Clothes'),
                  ('MCLOTH', 'Men Clothes'),
                  ('FCLOTH', 'Women Clothes'),
                  ('GAME', 'Gaming'),
                  ]

    category = models.CharField(max_length=50, choices=categories)
    item = models.ForeignKey(to=Item, related_name='Item_category', on_delete=models.RESTRICT)
