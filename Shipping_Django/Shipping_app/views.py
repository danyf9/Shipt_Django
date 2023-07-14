from django.contrib.auth import login
from django.contrib.auth.models import User, Group
from django.db.models import Q
from django.shortcuts import render, redirect
from django.views import View
from channels.layers import get_channel_layer

from .models import Item, Shipment, Categories, Image
from .forms import Search, ItemForm, EditShipment, \
    FullSignup, ItemCategoryForm, ImageForm, EditUserForm


# Create your views here.


def search_all(var):
    item_list = Item.objects.filter(
        Q(id__contains=var) |
        Q(name__contains=var) |
        Q(description__contains=var) |
        Q(description__contains=var) |
        Q(price__contains=var)
    )
    shipment_list = Shipment.objects.filter(
        Q(id__contains=var) |
        Q(order_date__contains=var)
    )
    return {'items': item_list, 'shipments': shipment_list}


def get_items(category):
    obj_lst = {}
    for c in list(zip(*Categories.categories))[0]:
        if c == {lst[1]: lst[0] for lst in Categories.categories}[category]:
            obj_lst.update(
                {c: [obj.item for obj in Categories.objects.filter(category=c)]})
    return obj_lst[{lst[1]: lst[0] for lst in Categories.categories}[category]]


class Home(View):
    @classmethod
    def get(cls, request):
        return render(request=request, template_name='Home.html')

    @classmethod
    def post(cls, request):
        return redirect('Search', var=request.POST.dict()['Var'])


class SearchView(View):
    @classmethod
    def get(cls, request, var):
        return render(request=request, template_name='Search.html',
                      context=search_all(var))

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
        return render(request=request, template_name='List.html',
                      context={'obj_list': obj_lst,
                               'kind': kind})

    @classmethod
    def post(cls, request, kind):
        data = Search(data=request.POST).data.dict()
        return render(request=request, template_name='Search.html',
                      context=search_all(data['Var']))


class Add(View):

    @classmethod
    def get(cls, request, kind):
        forms = ''
        permission = Group.objects.get(name='Add_permission') in request.user.groups.all()

        if kind == 'Item':
            forms = [ItemForm(action='Add'), ImageForm]
        elif kind == 'Category':
            forms = [ItemCategoryForm]
        elif kind == 'Image':
            forms = [ImageForm(item=True)]

        return render(request=request, template_name='FormModel.html',
                      context={'kind': kind, 'action': 'Add', 'forms': forms,
                               'permission': permission})

    @classmethod
    def post(cls, request, kind):
        form, msg, status = '', '', ''
        permission = Group.objects.get(name='Add_permission') in request.user.groups.all()

        if not permission:
            return render(request=request, template_name='Modal.html',
                          context={'direct': 'List', 'kind': kind, 'msg': 'permission denied',
                                   'status': 'Permission denied'})
        elif kind == 'Item':
            form = ItemForm(data=request.POST, action='Add')
        elif kind == 'Category':
            form = ItemCategoryForm(data=request.POST)
        elif kind == 'Image':
            form = ImageForm(instance=Image(
                item=Item.objects.get(pk=request.POST['item']),
                image=request.FILES['image']), item=True)

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
                    request.FILES['image'].name = f"{form.instance.id}.jpg"
                    Image(
                        item=Item.objects.get(pk=form.instance.pk),
                        image=request.FILES['image']
                    ).save()
            except Exception as e:
                msg = f'Error: {e}'
                status = 'Error'
        elif kind == 'Image':
            request.FILES['image'].name = f"{form.instance.item.id}.jpg"
            form.instance.save()
            msg = f'Image added successfully'
            status = 'Success'
            kind = 'Item'
        else:
            return render(request=request, template_name='FormModel.html',
                          context={'forms': [form], 'kind': kind, 'action': 'Add'})

        return render(request=request, template_name='Modal.html',
                      context={'direct': 'List', 'kind': kind, 'msg': msg,
                               'status': status})


class Full(View):

    @classmethod
    def get(cls, request, kind, pk):
        obj_dict = {}
        if kind == 'Item':
            obj = Item.objects.get(pk=pk)
            l1 = []
            for q in [c.category for c in obj.Item_category.all()]:
                l1.append({'category': {c[0]: c[1] for c in Categories.categories}[q],
                           'pk': Categories.objects.get(item=obj, category=q).pk})

            obj_dict = {'ID': obj.pk, 'Name': obj.name, 'Description': obj.description,
                        'Price': obj.price,
                        'Categories': l1, 'Picture': f"API/media/{obj.Item_image.filter()[0].image}"}

        elif kind == 'Shipment':
            obj = Shipment.objects.get(pk=pk)
            obj_dict = {'ID': obj.pk, 'Date': obj.order_date, 'User': obj.user.username,
                        'sitems': {shipment.item for shipment in obj.list_shipment.all()}}
        elif kind == 'Category':
            obj = Categories.objects.get(pk=pk)
            obj_dict = {'ID': obj.pk, 'Category': obj.category, 'Item': obj.item}

        elif kind == 'Profile':
            obj = User.objects.get(pk=pk)
            obj_dict = {'Username': obj.username, 'Full Name': obj.get_full_name(), 'email': obj.email}

        return render(request=request, template_name='Full_details.html',
                      context={'obj_dict': obj_dict})


class Edit(View):

    @classmethod
    def get(cls, request, kind, pk):
        forms = ''
        permission = Group.objects.get(name='Edit_permission') in request.user.groups.all()

        if kind == 'Item':
            forms = [ItemForm(instance=Item.objects.get(id=pk), action='Edit')]
        elif kind == 'Shipment':
            forms = [EditShipment(instance=Shipment.objects.get(id=pk))]
        elif kind == 'Profile':
            forms = [EditUserForm(instance=User.objects.get(id=pk),
                                  email=Group.objects.get(name='User_permission') in request.user.groups.all(),
                                  kind=kind)]
            permission = True
        elif kind == 'Password':
            forms = [EditUserForm(instance=User.objects.get(id=pk))]
            permission = Group.objects.get(name='User_permission') in request.user.groups.all()
        elif kind == 'Category':
            forms = [ItemCategoryForm(instance=Categories)]
        return render(request=request, template_name='FormModel.html',
                      context={'forms': forms, 'kind': kind, 'pk': pk, 'action': 'Edit',
                               'permission': permission})

    @classmethod
    def post(cls, request, kind, pk):
        form = msg = status = ''
        direct = 'List'
        permission = Group.objects.get(name='Edit_permission') in request.user.groups.all()

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
                                email=Group.objects.get(name='User_permission') in request.user.groups.all())
        elif kind == 'Password':
            form = EditUserForm(instance=request.user)
            if form.cleaned_data['password1'] == form.cleaned_data['password2'] \
                    and form.instance.check_password(form.cleaned_data['password']):
                form.instance.set_password(form.cleaned_data['password1'])
        if form.is_valid():
            try:
                form.save()
                msg = f'{kind} saved successfully'
                status = 'Success'
            except Exception as e:
                msg = f'Error: {e}'
                status = 'Error'
        else:
            return render(request=request, template_name='FormModel.html',
                          context={'forms': [form], 'kind': kind, 'pk': pk, 'action': 'Edit',
                                   'permission': permission})

        if kind == 'Profile':
            login(request=request, user=form.instance)
            direct = 'Home'

        return render(request=request, template_name='Modal.html',
                      context={'direct': direct, 'kind': kind, 'msg': msg,
                               'status': status})


class Delete(View):

    @classmethod
    def get(cls, request, kind, pk):
        obj = ''
        if kind == 'Item':
            obj = Item.objects.get(pk=pk)
            obj.Item_image.get().image.delete(save=False)
        elif kind == 'Shipment':
            obj = Shipment.objects.get(pk=pk)
        elif kind == 'Category':
            obj = Categories.objects.get(pk=pk)
        obj.delete()
        return redirect('List', kind=kind)


class SignupView(View):

    @classmethod
    def get(cls, request):
        return render(request=request, template_name='registration/login.html',
                      context={'form': FullSignup, 'action': 'Signup'})

    @classmethod
    def post(cls, request):
        user = FullSignup(data=request.POST)
        if user.is_valid():
            try:
                user.save()
                login(request=request, user=user.instance)
                status = 'Success'
                msg = ''
            except Exception as e:
                status = 'Error'
                msg = str(e)
            return render(request=request, template_name='Modal.html',
                          context={'direct': 'Home', 'kind': 'User', 'msg': msg,
                                   'status': status})
        else:
            return render(request=request, template_name='registration/login.html',
                          context={'form': user, 'action': 'Signup', 'user': user.instance.username})


class WS(View):
    @classmethod
    def get(cls, request):
        return render(request=request, template_name='chat/Channel.html')
