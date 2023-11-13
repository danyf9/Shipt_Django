from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.contrib.auth.models import User
from .functions import auto_id, user_text

# Create your models here.


class Item(models.Model):

    id = models.PositiveIntegerField(primary_key=True, default=auto_id)
    name = models.CharField(max_length=50, null=False)
    description = models.TextField(max_length=200, null=False)
    price = models.PositiveIntegerField(null=False)

    class Meta:
        db_table = 'Items'

    def __str__(self):
        return f'[{self.id}] {self.name}'


class Shipment(models.Model):

    id = models.PositiveIntegerField(primary_key=True, default=auto_id)
    order_date = models.DateField(auto_now_add=True)
    user = models.ForeignKey(to=User, related_name='User_shipment', on_delete=models.CASCADE,
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

    def __str__(self):
        return f'{self.shipment}->{self.item}'


class CategoryOptions(models.Model):
    category = models.CharField(max_length=50)

    def __str__(self):
        return self.category


class Categories(models.Model):
    category = models.ForeignKey(to=CategoryOptions, related_name='Category', on_delete=models.CASCADE)
    item = models.ForeignKey(to=Item, related_name='Item_category', on_delete=models.CASCADE)

    class Meta:
        db_table = 'Categories'
        unique_together = ('category', 'item')


class Image(models.Model):
    item = models.ForeignKey(to=Item, related_name='Item_image', on_delete=models.CASCADE, null=True)
    image = models.CharField(max_length=50, null=True)
    status = models.CharField(max_length=10, null=False, choices=[
        ('W', 'Waiting'), ('C', 'Confirmed')], default='W')

    def __str__(self):
        return f"{self.item}, {self.image}"


class Comment(models.Model):
    user = models.ForeignKey(to=User, related_name='User_comment', on_delete=models.CASCADE)
    comment_text = models.CharField(max_length=100)
    rating = models.PositiveIntegerField(default=5, validators=[
        MinValueValidator(1), MaxValueValidator(5)])
    item = models.ForeignKey(to=Item, related_name='Item_comment', on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'item')


class WishList(models.Model):
    user = models.ForeignKey(to=User, related_name='wishlist_user', on_delete=models.CASCADE)
    item = models.ForeignKey(to=Item, related_name='wishlist_item', on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'item')


User.add_to_class('__str__', user_text)

