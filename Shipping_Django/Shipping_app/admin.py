from django.contrib import admin
from .models import Item, Shipment, Categories, Image
# Register your models here.

admin.site.register(Item)
admin.site.register(Shipment)
admin.site.register(Categories)
admin.site.register(Image)
