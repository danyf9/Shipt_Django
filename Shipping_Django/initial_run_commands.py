import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Shipping_Django.settings")

import django
django.setup()

from django.core.cache import cache
from Shipping_app.models import Categories
from django.contrib.auth.models import User

os.system('python.exe ./manage.py makemigrations')
os.system('python.exe ./manage.py migrate')
User.objects.create_superuser(username='Admin', password='123').save()
cache.set('category_CAT_dict', {c[1]: c[0] for c in Categories.categories}, timeout=None)
cache.set('categories', [c[1] for c in Categories.categories], timeout=None)
