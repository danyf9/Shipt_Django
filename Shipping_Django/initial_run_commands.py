import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Shipping_Django.settings")

import django

django.setup()

from django.core.cache import cache
from Shipping_app.models import Categories
from django.contrib.auth.models import User, Group
from rest_framework.authtoken.models import Token

# change to 'python3' before launch in ubuntu
os.system('python.exe ./manage.py makemigrations')
os.system('python.exe ./manage.py migrate')
try:
    # user = User.objects.create_user(username='Admin', password='123').save()
    user = User.objects.get(username='Admin')
    token = Token.objects.create(user=user)
    Group(name='User_permission').save()
    Group(name='Edit_permission').save()
    Group(name='View_permission').save()
    Group(name='Chat_permission').save()
    Group(name='Add_permission').save()
    for group in Group.objects.all():
        try:
            user.groups.add(group)
        except:
            pass
except Exception as e:
    print(e)
cache.set('category_CAT_dict', {c[1]: c[0] for c in Categories.categories}, timeout=None)
cache.set('categories', [c[1] for c in Categories.categories], timeout=None)
