from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from . import api_views

urlpatterns = [
    path("items", api_views.ItemAPI.as_view()),
    path("items/<str:action>", api_views.ItemAPI.as_view()),
    path("login", obtain_auth_token)
]