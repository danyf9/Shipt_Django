from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from . import api_views
from django.conf import settings
from django.conf.urls.static import static
from django.views.decorators.cache import cache_page

urlpatterns = [
    path("items", api_views.ItemAPI.as_view()),
    path("item-page/<int:page_num>/<int:page_size>", api_views.ItemPageAPI.as_view()),
    path("item-page/<int:page_num>/<int:page_size>/<str:category>", api_views.ItemPageAPI.as_view()),
    path("item-filter/<int:page_num>/<int:page_size>", api_views.FilterAPI.as_view()),
    path("item-search/<int:page_num>/<int:page_size>", api_views.SearchAPI.as_view()),
    path("home-items", api_views.HomePageItemsAPI.as_view()),
    path("login", obtain_auth_token),
    path("signup", api_views.UserCreation.as_view()),
    path("user", api_views.GetUserWithToken.as_view()),
    path("shipment", api_views.ShipmentAPI.as_view()),
    path("comments/<int:page_num>/<int:page_size>/<int:item_id>", api_views.CommentsAPI.as_view()),
    path("user-comment", api_views.AddCommentAPI.as_view()),
    path('reset', api_views.ResetCache.as_view()),
    path("image", api_views.ItemImageAPI.as_view()),
    path("image/<int:num>", api_views.ItemImageAPI.as_view()),
    path("WL/<str:username>/<int:item_id>", api_views.WishListAPI.as_view()),
]