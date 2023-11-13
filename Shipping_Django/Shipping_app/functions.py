import os
import random
import string
import boto3
from django.db.models import Q
from botocore.config import Config
from django.http import HttpResponse

from . import models
from django.contrib.auth.models import User, Group
from time import time


def auto_id():
    return int(time())


def search_all(var, request):
    group = groups(request.user)
    if group['View_permission']:
        if group['Item_permission']:
            item_list = models.Item.objects.filter(
                Q(id__contains=var) |
                Q(name__contains=var) |
                Q(description__contains=var) |
                Q(price__contains=var)
            )
        else:
            item_list = {}
        if group['Shipment_permission']:
            shipment_list = models.Shipment.objects.filter(
                Q(id__contains=var) |
                Q(user__username__contains=var) |
                Q(order_date__contains=var)
            )
        else:
            shipment_list = {}
        if group['User_permission']:
            user_list = User.objects.filter(
                Q(username__contains=var) |
                Q(first_name__contains=var) |
                Q(last_name__contains=var) |
                Q(email__contains=var)
            )
        else:
            user_list = {}
    else:
        item_list = shipment_list = user_list = {}
    return {'items': item_list, 'shipments': shipment_list, 'users': user_list}


def get_items(category):
    return [c.item for c in models.CategoryOptions.objects.get(category=category).Category.all()]

def groups(user):
    return {group.name: (group in user.groups.all()) for group in Group.objects.all()}


def permissions(user, kind, action):
    if kind != 'Profile' and kind != 'Password':
        group = groups(user)
        return group[f'{action}_permission'] and (group[f'{kind}_permission'])
    return True


def s3_url():
    s3_client = boto3.client('s3', aws_access_key_id=os.environ.get('ACCESS_KEY'),
                             aws_secret_access_key=os.environ.get('SECRET_ACCESS_KEY'),
                             region_name='eu-north-1', config=Config(signature_version='s3v4'))
    rand_id = "".join(
        random.SystemRandom().choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in
        range(20))
    models.Image(image=f"{rand_id}.png", status='W').save()
    return {'url': s3_client.generate_presigned_url(
        ClientMethod='put_object',
        Params={
            'Bucket': 'shiptbucket',
            'Key': f'items/{rand_id}.png',
        },
        ExpiresIn=5000
    ), 'id': rand_id}


def s3_delete(img_list):
    s3_client = boto3.client('s3', aws_access_key_id=os.environ.get('ACCESS_KEY'),
                             aws_secret_access_key=os.environ.get('SECRET_ACCESS_KEY'),
                             region_name='eu-north-1', config=Config(signature_version='s3v4'))
    for img in img_list:
        s3_client.delete_object(Bucket='shiptbucket', Key=f'items/{img.image}')


def all_rating(item_id):
    rating = 0
    lst = models.Item.objects.get(id=item_id).Item_comment.filter()
    for i in lst:
        rating += i.rating
    return rating / len(lst)


def user_text(self):
    return f'{self.username}{" (staff)" if self.is_staff else ""}'


def not_found():
    return HttpResponse('404 page not found <br> <a href="/Shipt">home<a/>')
