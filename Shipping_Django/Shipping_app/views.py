import random
import string
import boto3
import os
from botocore.config import Config
from django.contrib.auth import login
from django.contrib.auth.models import User, Group
from django.db.models import Q
from django.shortcuts import render, redirect
from django.views import View
from channels.layers import get_channel_layer

from .models import Item, Shipment, Categories, Image
from .forms import Search, ItemForm, EditShipment, \
    FullSignup, ItemCategoryForm, ImageForm, EditUserForm, GroupsForm


def search_all(var, request):
    group = groups(request.user)
    if group['View_permission']:
        if group['Item_permission']:
            item_list = Item.objects.filter(
                Q(id__contains=var) |
                Q(name__contains=var) |
                Q(description__contains=var) |
                Q(price__contains=var)
            )
        else:
            item_list = {}
        if group['Shipment_permission']:
            shipment_list = Shipment.objects.filter(
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
    obj_lst = {}
    for c in list(zip(*Categories.categories))[0]:
        if c == {lst[1]: lst[0] for lst in Categories.categories}[category]:
            obj_lst.update(
                {c: [obj.item for obj in Categories.objects.filter(category=c)]})
    return obj_lst[{lst[1]: lst[0] for lst in Categories.categories}[category]]


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
    Image(image=f"{rand_id}.png", status='W').save()
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


class Home(View):
    @classmethod
    def get(cls, request):
        return render(request=request, template_name='Home.html',
                      context={'groups': groups(request.user)})

    @classmethod
    def post(cls, request):
        return redirect('Search', var=request.POST.dict()['Var'])


class SearchView(View):
    @classmethod
    def get(cls, request, var):
        return render(request=request, template_name='Search.html',
                      context=dict(search_all(var, request), groups=groups(request.user)))

    @classmethod
    def post(cls, request, var):
        return redirect('Search', var=request.POST.dict()['Var'])


class List(View):

    @classmethod
    def get(cls, request, kind, category=None):
        obj_lst = ''
        if kind == 'Item':
            obj_lst = Item.objects.all()

        elif kind == 'Shipment':
            obj_lst = Shipment.objects.all()

        elif kind == 'Category':
            if category is None:
                obj_lst = [o for o in Categories.categories]
            else:
                obj_lst = get_items(category)
                kind = 'Item'

        elif kind == 'Room':
            obj_lst = [k.split('_')[1] for k in list(get_channel_layer().groups.keys())]

        elif kind == 'User':
            obj_lst = User.objects.all()

        return render(request=request, template_name='List.html',
                      context={'obj_list': obj_lst,
                               'kind': kind, 'groups': groups(request.user)})

    @classmethod
    def post(cls, request, kind):
        data = Search(data=request.POST).data.dict()
        return render(request=request, template_name='Search.html',
                      context=dict(search_all(data['Var'], request), groups=groups(request.user)))


class Add(View):

    @classmethod
    def get(cls, request, kind):
        forms = url = img_name = ''
        permission = permissions(request.user, kind, 'Add')

        if not permission:
            return render(request=request, template_name='Modal.html',
                          context={'direct': 'Home', 'kind': 'Profile', 'msg': 'permission denied',
                                   'status': 'Permission denied'})

        if kind == 'Item':
            ps = s3_url()
            url = ps['url']
            img_name = ps['id']
            forms = [ItemForm(action='Add'), ImageForm(img_name=img_name)]
        elif kind == 'Category':
            forms = [ItemCategoryForm]
        elif kind == 'Image':
            ps = s3_url()
            url = ps['url']
            img_name = ps['id']
            forms = [ImageForm(item=True, img_name=img_name)]
        elif kind == 'User':
            forms = [FullSignup, GroupsForm]

        return render(request=request, template_name='Form.html',
                      context={'kind': kind, 'action': 'Add', 'forms': forms,
                               'permission': permission, 'groups': groups(request.user), 'url': url,
                               'img_name': img_name})

    @classmethod
    def post(cls, request, kind):
        form, msg, status = '', '', ''
        permission = permissions(request.user, kind, 'Add')

        if not permission:
            return render(request=request, template_name='Modal.html',
                          context={'direct': 'Home', 'kind': 'Profile', 'msg': 'permission denied',
                                   'status': 'Permission denied'})

        elif kind == 'Item':
            form = ItemForm(data=request.POST, action='Add')
        elif kind == 'Category':
            form = ItemCategoryForm(data=request.POST)
        elif kind == 'Image':
            form = ImageForm(instance=Image(
                item=Item.objects.get(pk=request.POST['item']),
                image=f"{request.POST['img_name']}.png", status='C'), item=True)
        elif kind == 'User':
            form = FullSignup(data=request.POST)
            form.instance.is_staff = True

        if form.is_valid():
            try:
                form.save()
                msg = f'{kind} added successfully'
                status = 'Success'
                if kind == 'Item':
                    Categories(
                        item=Item.objects.get(pk=form.instance.pk),
                        category=form.cleaned_data['category']
                    ).save()
                    img = Image.objects.get(image=f"{request.POST['img_name']}.png", status='W')
                    img.item = form.instance
                    img.status = 'C'
                    img.save()
            except Exception as e:
                msg = f'Error: {e}'
                status = 'Error'
        elif kind == 'Image':
            img = Image.objects.get(image=f"{request.POST['img_name']}.png", status='W')
            img.item = form.instance.item
            img.status = 'C'
            img.save()
            msg = f'Image added successfully'
            status = 'Success'
            kind = 'Item'
        else:
            return render(request=request, template_name='Form.html',
                          context={'forms': [form], 'kind': kind, 'action': 'Add', 'groups': groups(request.user),
                                   'permission': permission})

        if kind == 'User':
            groups_form = dict(GroupsForm(data=request.POST).data)
            for field in groups_form.keys():
                if 'permission' in field:
                    User.objects.get(username=form.instance.username).groups.add(
                        Group.objects.get(name=field.capitalize()))

        return render(request=request, template_name='Modal.html',
                      context={'direct': 'List', 'kind': kind, 'msg': msg,
                               'status': status, 'pk': form.instance.id})


class Full(View):

    @classmethod
    def get(cls, request, kind, pk):
        obj_dict = {}
        permission = permissions(request.user, kind, 'View')

        if not permission:
            return render(request=request, template_name='Modal.html',
                          context={'direct': 'Home', 'kind': 'Profile', 'msg': 'permission denied',
                                   'status': 'Permission denied'})
        if kind == 'Item':
            obj = Item.objects.get(pk=pk)
            l1 = []
            for q in [c.category for c in obj.Item_category.all()]:
                l1.append({'category': {c[0]: c[1] for c in Categories.categories}[q],
                           'pk': Categories.objects.get(item=obj, category=q).pk})

            obj_dict = {'ID': obj.pk, 'Name': obj.name, 'Description': obj.description,
                        'Price': obj.price,
                        'Categories': l1}
            try:
                obj_dict = dict(obj_dict, Picture=f"{os.environ.get('S3_URL')}/{obj.Item_image.filter()[0].image}")
            except Exception as e:
                obj_dict = dict(obj_dict, Picture="")

        elif kind == 'Shipment':
            obj = Shipment.objects.get(pk=pk)
            obj_dict = {'ID': obj.pk, 'Date': obj.order_date, 'User': obj.user.username,
                        'shipment_items':
                            sorted([shipment.item for shipment in obj.list_shipment.all()], key=lambda item: item.id)}
        elif kind == 'Category':
            obj = Categories.objects.get(pk=pk)
            obj_dict = {'ID': obj.pk, 'Category': obj.category, 'Item': obj.item}
        elif kind == 'Profile' or 'User':
            obj = User.objects.get(pk=pk)
            obj_dict = {'Username': obj.username, 'Full Name': obj.get_full_name(), 'email': obj.email}

        return render(request=request, template_name='Full_details.html',
                      context={'obj_dict': obj_dict, 'groups': groups(request.user), 'kind': kind})

    @classmethod
    def post(cls, request, kind, pk):
        return redirect('Search', var=request.POST.dict()['Var'])


class Edit(View):

    @classmethod
    def get(cls, request, kind, pk):
        forms = ''
        permission = permissions(request.user, kind, 'Edit') if kind != 'User' \
            else (permissions(request.user, kind, 'Edit') and request.user.pk != pk)

        if not permission:
            return render(request=request, template_name='Modal.html',
                          context={'direct': 'Home', 'kind': 'Profile', 'msg': 'permission denied',
                                   'status': 'Permission denied'})
        if kind == 'Item':
            forms = [ItemForm(instance=Item.objects.get(id=pk), action='Edit')]
        elif kind == 'Shipment':
            forms = [EditShipment(instance=Shipment.objects.get(id=pk))]
        elif kind == 'Profile':
            forms = [EditUserForm(instance=User.objects.get(id=pk),
                                  email=groups(request.user)['User_permission'],
                                  kind=kind)]
        elif kind == 'Password':
            forms = [EditUserForm(instance=User.objects.get(id=pk), kind='Password')]
        elif kind == 'Category':
            forms = [ItemCategoryForm(instance=Categories)]
        elif kind == 'User':
            forms = [EditUserForm(instance=User.objects.get(pk=pk), kind=kind),
                     GroupsForm(groups=groups(User.objects.get(pk=pk)))]
        return render(request=request, template_name='Form.html',
                      context={'forms': forms, 'kind': kind, 'pk': pk, 'action': 'Edit',
                               'permission': permission, 'groups': groups(request.user)})

    @classmethod
    def post(cls, request, kind, pk):
        form = msg = status = ''
        direct = 'List'
        permission = permissions(request.user, kind, 'Edit') if kind != 'User' \
            else (permissions(request.user, kind, 'Edit') and request.user.pk != pk)

        if not permission:
            return render(request=request, template_name='Modal.html',
                          context={'direct': 'Home', 'kind': 'Profile', 'msg': 'permission denied',
                                   'status': 'Permission denied'})

        if not permission:
            return render(request=request, template_name='Modal.html',
                          context={'direct': 'List', 'kind': kind, 'msg': 'permission denied',
                                   'status': 'Permission denied'})
        elif kind == 'Item':
            form = ItemForm(data=request.POST, instance=Item.objects.get(id=pk), action='Edit')
        elif kind == 'Shipment':
            form = EditShipment(data=request.POST, instance=Shipment.objects.get(id=pk))
        elif kind == 'Category':
            form = ItemCategoryForm(data=request.POST, instance=Categories.objects.get(pk=pk))
        elif kind == 'Profile':
            form = EditUserForm(data=request.POST, instance=request.user,
                                email=groups(request.user)['User_permission'])
        elif kind == 'Password':
            form = EditUserForm(data=request.POST, instance=User.objects.get(id=pk))
            if form.data['new_password1'] == form.data['new_password2'] \
                    and form.instance.check_password(form.data['old_password']):
                form.instance.set_password(form.data['new_password1'])
                form.instance.save()
            else:
                return render(request=request, template_name='Modal.html',
                              context={'direct': 'Home', 'kind': kind, 'msg': 'one or more of the following could not '
                                                                              'be satisfied:\n1. Old password did not '
                                                                              'match with user password\n2. Password '
                                                                              'confirmation could not be established',
                                       'status': 'Failed'})
        elif kind == 'User':
            form = EditUserForm(data=request.POST, instance=User.objects.get(pk=pk), kind=kind)
            form.instance.set_password(form.data['password'])
            form.instance.save()
        if form.is_valid():
            try:
                form.save()
                msg = f'{kind} saved successfully'
                status = 'Success'
            except Exception as e:
                msg = f'Error: {e}'
                status = 'Error'
        else:
            return render(request=request, template_name='Form.html',
                          context={'forms': [form], 'kind': kind, 'pk': pk, 'action': 'Edit',
                                   'permission': permission, 'groups': groups(request.user)})

        if kind == 'User':
            groups_form = dict(GroupsForm(data=request.POST).data)
            user = User.objects.get(username=form.instance.username)
            user.groups.clear()
            for field in groups_form.keys():
                if 'permission' in field:
                    user.groups.add(
                        Group.objects.get(name=field.capitalize()))

        if kind == 'Profile' or kind == 'Password':
            login(request=request, user=form.instance)
            direct = 'Home'
        return render(request=request, template_name='Modal.html',
                      context={'direct': direct, 'kind': kind, 'msg': msg,
                               'status': status})


class Delete(View):

    @classmethod
    def get(cls, request, kind, pk):
        obj = ''
        permission = permissions(request.user, kind, 'Delete') if kind != 'User' \
            else (permissions(request.user, kind, 'Delete') and request.user.pk != pk)

        if not permission:
            return render(request=request, template_name='Modal.html',
                          context={'direct': 'Home', 'kind': 'Profile', 'msg': 'permission denied',
                                   'status': 'Permission denied'})

        if kind == 'Item':
            obj = Item.objects.get(pk=pk)
            s3_delete(obj.Item_image.all())
        elif kind == 'Shipment':
            obj = Shipment.objects.get(pk=pk)
        elif kind == 'Category':
            obj = Categories.objects.get(pk=pk)
        elif kind == 'User':
            obj = User.objects.get(pk=pk)
        elif kind == 'Image':
            item = Item.objects.get(pk=pk)
            for image in item.Item_image.all():
                image.delete()
            s3_delete(item.Item_image.all())
            return redirect('Full', kind='Item', pk=pk)
        obj.delete()
        return redirect('List', kind=kind)


class WS(View):
    @classmethod
    def get(cls, request):
        return render(request=request, template_name='chat/Channel.html',
                      context={'groups': groups(request.user)})
