from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path
from . import views
urlpatterns = [

    path('Home', login_required(views.Home.as_view()), name='Home'),
    path('Login', LoginView.as_view(), name='Login'),
    path('Logout', LogoutView.as_view(), name='Logout'),
    path('Welcome', views.Base.as_view(), name='Welcome'),
]
