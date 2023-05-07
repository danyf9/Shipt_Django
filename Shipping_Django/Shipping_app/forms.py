from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Item, Shipment, Categories


class Search(forms.Form):
    var = forms.CharField(required=False, max_length=100)


class AddItem(forms.ModelForm):
    class Meta:
        model = Item
        fields = '__all__'


class EditItem(forms.ModelForm):
    id = forms.IntegerField(disabled=True)

    class Meta:
        model = Item
        fields = '__all__'


class AddShipment(forms.ModelForm):
    class Meta:
        model = Shipment
        fields = '__all__'


class EditShipment(forms.ModelForm):
    id = forms.IntegerField(disabled=True)

    class Meta:
        model = Shipment
        fields = '__all__'


class FullSignup(UserCreationForm):
    username = forms.CharField()
    password1 = forms.CharField(label="Password",
                                widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
                                help_text='')
    password2 = forms.CharField(label="Password confirmation",
                                widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
                                help_text='')

    class Meta:
        model = User
        exclude = ['last_login', 'is_superuser', 'groups',
                   'user_permissions', 'password', 'is_staff',
                   'is_active', 'date_joined']
        fields = '__all__'


class ItemCategoryForm(forms.ModelForm):

    class Meta:
        model = Categories
        fields = '__all__'
