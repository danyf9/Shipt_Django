from django.urls import path
from . import views
urlpatterns = [
    path('Home', views.Home.as_view(), name='Home')
]
