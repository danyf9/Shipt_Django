from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from . import api_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("items", api_views.ItemAPI.as_view()),
    path("items/<str:action>", api_views.ItemAPI.as_view()),
    path("item-page/<int:page_num>/<int:page_size>", api_views.ItemPage.as_view()),
    path("item-page/<int:page_num>/<int:page_size>/<str:category>", api_views.ItemPage.as_view()),
    path("login", obtain_auth_token)
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
