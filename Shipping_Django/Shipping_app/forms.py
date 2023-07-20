from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Item, Shipment, Categories, Image, auto_id


class Search(forms.Form):
    var = forms.CharField(required=False, max_length=100)


class ItemForm(forms.ModelForm):
    category = forms.ChoiceField(choices=Categories.categories)
    id = forms.IntegerField(disabled=True)

    def __init__(self, *args, action, **kwargs):
        super().__init__(*args, **kwargs)
        if action == 'Add':
            self.fields['id'].disabled = True
            self.fields['id'].initial = auto_id()
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

    def __init__(self, *args, item=False, **kwargs):
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

    def __init__(self, email=False, kind='', edit_user=True, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if kind != 'Profile' and kind != 'User':
            self.fields['first_name'].widget = forms.HiddenInput()
            self.fields['last_name'].widget = forms.HiddenInput()
        if not email:
            self.fields['email'].widget = forms.HiddenInput()
        if kind == 'Password':
            self.fields['username'] = forms.ModelChoiceField(disabled=edit_user, initial=self.instance.username,
                                                             queryset=User.objects.all())
            self.fields['old_password'] = forms.CharField(widget=forms.PasswordInput, label='Old password')
            self.fields['new_password1'] = forms.CharField(widget=forms.PasswordInput, label='New password')
            self.fields['new_password2'] = forms.CharField(widget=forms.PasswordInput, label='New password confirmation')
        if kind == 'User':
            self.fields['username'] = forms.CharField(initial=self.instance.username)
            self.fields['first_name'] = forms.CharField(initial=self.instance.first_name)
            self.fields['last_name'] = forms.CharField(initial=self.instance.last_name)
            self.fields['email'] = forms.EmailField(initial=self.instance.email)
            self.fields['password'] = forms.CharField(widget=forms.PasswordInput)
            self.order_fields(field_order=['username', 'first_name', 'last_name', 'email', 'password'])

    class Meta:
        model = User
        exclude = ['last_login', 'is_superuser', 'groups','username',
                   'user_permissions', 'is_staff', 'password',
                   'is_active', 'date_joined']
        fields = '__all__'
