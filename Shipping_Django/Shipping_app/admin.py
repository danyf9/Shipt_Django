from django.contrib import admin
from .models import Item, Shipment, Categories, Image, Comment, ShipmentList, WishList

# Register your models here.

admin.site.register(Item)
admin.site.register(Shipment)
admin.site.register(Categories)
admin.site.register(Image)
admin.site.register(Comment)
admin.site.register(ShipmentList)
admin.site.register(WishList)
