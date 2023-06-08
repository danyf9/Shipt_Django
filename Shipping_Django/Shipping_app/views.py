from django.contrib.auth import login
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views import View
from channels.layers import get_channel_layer

from .models import Item, Shipment, Categories
from .forms import Search, AddItem, EditItem, AddShipment, EditShipment, FullSignup, ItemCategoryForm


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
        form = ''

        if kind == 'Item':
            form = AddItem
        elif kind == 'Shipment':
            form = AddShipment
        elif kind == 'Category':
            form = ItemCategoryForm

        return render(request=request, template_name='FormModel.html',
                      context={'kind': kind, 'action': 'Add', 'form': form})

    @classmethod
    def post(cls, request, kind):
        form, msg, status = '', '', ''
        if kind == 'Item':
            form = AddItem(data=request.POST)
        elif kind == 'Shipment':
            form = AddShipment(data=request.POST)
        elif kind == 'Category':
            form = ItemCategoryForm(data=request.POST)

        if form.is_valid():
            try:
                form.save()
                msg = f'{kind} added successfully'
                status = 'Success'
                if kind == 'Item':
                    ItemCategoryForm(instance=Categories(
                        item=Item.objects.get(pk=form.instance.pk),
                        category=form.cleaned_data['category']
                    )).save()
            except Exception as e:
                msg = f'Error: {e}'
                status = 'Error'
        else:
            error = form.errors
            msg = f'An unknown error has occurred\n{error}'
            status = 'Error'
        return render(request=request, template_name='Modal.html',
                      context={'direct': 'List', 'kind': kind, 'msg': msg,
                               'status': status})


class Full(View):

    @classmethod
    def get(cls, request, kind, pk):
        obj_dict = {}
        if kind == 'Item':
            obj = Item.objects.get(id=pk)
            l1, l2 = [], []
            for q in [c.category for c in obj.Item_category.all()]:
                l1.append({'category': {c[0]: c[1] for c in Categories.categories}[q],
                           'pk': Categories.objects.get(item=obj, category=q).pk})

            obj_dict = {'ID': obj.pk, 'Name': obj.name, 'Description': obj.description,
                        'Price': obj.price,
                        'Categories': l1}

        elif kind == 'Shipment':
            obj = Shipment.objects.get(id=pk)
            obj_dict = {'ID': obj.pk, 'Date': obj.order_date, 'User': obj.user.username}

        elif kind == 'Category':
            obj = Categories.objects.get(pk=pk)
            obj_dict = {'ID': obj.pk, 'Category': obj.category, 'Item': obj.item}

        return render(request=request, template_name='Full_details.html',
                      context={'obj_dict': obj_dict})


class Edit(View):

    @classmethod
    def get(cls, request, kind, pk):
        form = ''
        if kind == 'Item':
            form = EditItem(instance=Item.objects.get(id=pk))
        elif kind == 'User':
            form = FullSignup(instance=User.objects.get(id=pk))
        elif kind == 'Category':
            form = ItemCategoryForm(instance=Categories)
        return render(request=request, template_name='FormModel.html',
                      context={'form': form, 'kind': kind, 'pk': pk, 'action': 'Edit'})

    @classmethod
    def post(cls, request, kind, pk):
        form = ''
        if kind == 'Item':
            form = EditItem(data=request.POST, instance=Item.objects.get(id=pk))
        elif kind == 'Shipment':
            form = EditShipment(data=request.POST, instance=Shipment.objects.get(id=pk))
        elif kind == 'Category':
            form = ItemCategoryForm(data=request.POST, instance=Categories.objects.get(pk=pk))
        elif kind == 'User':
            form = FullSignup(data=request.POST, instance=request.user)
        if form.is_valid():
            try:
                form.save()
                msg = f'{kind} saved successfully'
                status = 'Success'
            except Exception as e:
                msg = f'Error: {e}'
                status = 'Error'
        else:
            error = form.errors
            msg = f'An unknown error has occurred\n{error}'
            status = 'Error'
        if kind == 'User':
            login(request=request, user=form.instance)
            return render(request=request, template_name='Modal.html',
                          context={'direct': 'Home', 'kind': kind, 'msg': msg,
                                   'status': status})

        return render(request=request, template_name='Modal.html',
                      context={'direct': 'List', 'kind': kind, 'msg': msg,
                               'status': status})


class Delete(View):

    @classmethod
    def get(cls, request, kind, pk):
        obj, re = '', ''
        if kind == 'Item':
            obj = Item.objects.get(pk=pk)
        elif kind == 'Shipment':
            obj = Shipment.objects.get(pk=pk)
        elif kind == 'Category':
            obj = Categories.objects.get(pk=pk)
        obj.delete()
        return redirect('List', kind=kind)


class SignupView(View):

    @classmethod
    def get(cls, request):
        return render(request=request, template_name='registration/Login.html',
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
            return render(request=request, template_name='registration/Login.html',
                          context={'form': user, 'action': 'Signup', 'user': user.instance.username})


class WS(View):
    @classmethod
    def get(cls, request):
        return render(request=request, template_name='chat/Channel.html')
