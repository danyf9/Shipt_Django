import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Shipping_Django.settings")

import django

django.setup()

from django.contrib.auth.models import User, Group
from rest_framework.authtoken.models import Token
from Shipping_app.models import CategoryOptions

os.system('python3 ./manage.py makemigrations')
os.system('python3 ./manage.py migrate')
try:
    user = User.objects.create_user(username='Admin', password='123', is_staff=True)
    user.save()
    token = Token.objects.create(user=user)
    Group(name='User_permission').save()
    Group(name='Edit_permission').save()
    Group(name='View_permission').save()
    Group(name='Chat_permission').save()
    Group(name='Add_permission').save()
    Group(name='Delete_permission').save()
    Group(name='Item_permission').save()
    Group(name='Shipment_permission').save()
    Group(name='Category_permission').save()
    Group(name='Image_permission').save()
    for group in Group.objects.all():
        try:
            user.groups.add(group)
        except:
            pass
except Exception as e:
    print(e)

basic_categories = ['Technology', 'Toys', 'Clothes', 'Men Clothes', 'Women Clothes', 'Gaming']
for category in basic_categories:
    CategoryOptions(category=category).save()
