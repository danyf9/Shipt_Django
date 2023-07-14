from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Item, Shipment, Categories, Image


class Search(forms.Form):
    var = forms.CharField(required=False, max_length=100)


class ItemForm(forms.ModelForm):

    category = forms.ChoiceField(choices=Categories.categories)
    id = forms.IntegerField(disabled=True)

    def __init__(self, *args, action, **kwargs):
        super().__init__(*args, **kwargs)
        if action == 'Add':
            self.fields['id'].disabled = False
        elif action == 'Edit':
            self.fields['category'].widget = forms.HiddenInput()

    class Meta:
        model = Item
        fields = '__all__'


class EditShipment(forms.ModelForm):
    id = forms.IntegerField(disabled=True)

    class Meta:
        model = Shipment
        fields = '__all__'


class ItemCategoryForm(forms.ModelForm):

    class Meta:
        model = Categories
        fields = '__all__'


class ImageForm(forms.ModelForm):

    def __init__(self, *args, item, **kwargs):
        super().__init__(*args, **kwargs)
        if not item:
            self.fields['item'].widget = forms.HiddenInput()

    class Meta:
        model = Image
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


class EditUserForm(forms.ModelForm):

    first_name = forms.CharField(min_length=1)
    last_name = forms.CharField(min_length=1)

    def __init__(self, *args, email=False, kind='', **kwargs):
        super().__init__(*args, **kwargs)
        if not email:
            self.email = forms.EmailField()
        if kind == 'Profile':
            self.password = forms.CharField(widget=forms.PasswordInput, label='Old password')
            self.password1 = forms.CharField(widget=forms.PasswordInput, label='New password')
            self.password2 = forms.CharField(widget=forms.PasswordInput, label='New password confirmation')

    class Meta:
        model = User
        exclude = ['username', 'last_login', 'is_superuser', 'groups',
                   'user_permissions', 'is_staff', 'password',
                   'is_active', 'date_joined']
        fields = '__all__'
