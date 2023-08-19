from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path
from . import views
urlpatterns = [

    path('home', login_required(views.Home.as_view()), name='Home'),
    path('login', LoginView.as_view(), name='Login'),
    path('logout', LogoutView.as_view(), name='Logout'),
    path('list/<str:kind>', login_required(views.List.as_view()), name='List'),
    path('list/<str:kind>/<str:category>', login_required(views.List.as_view()), name='CategoryList'),
    path('add/<str:kind>', login_required(views.Add.as_view()), name='Add'),
    path('edit/<str:kind>/<int:pk>', login_required(views.Edit.as_view()), name='Edit'),
    path('delete/<str:kind>/<int:pk>', login_required(views.Delete.as_view()), name='Delete'),
    path('full/<str:kind>/<int:pk>', login_required(views.Full.as_view()), name='Full'),
    path('search/<str:var>', login_required(views.SearchView.as_view()), name='Search'),
    path('ws', login_required(views.WS.as_view()), name='WS'),
]
