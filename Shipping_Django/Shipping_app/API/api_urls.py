from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from . import api_views

urlpatterns = [
    path("item", api_views.ItemAPI.as_view(http_method_names=['get'])),
    path("item-page/<int:page_num>/<int:page_size>", api_views.ItemListAPI.as_view(http_method_names=['get'])),
    path("item-page/<int:page_num>/<int:page_size>/<str:category>", api_views.ItemListAPI.as_view(http_method_names=['get'])),
    path("item-filter/<int:page_num>/<int:page_size>", api_views.FilterAPI.as_view(http_method_names=['post'])),
    path("item-search/<int:page_num>/<int:page_size>", api_views.SearchAPI.as_view(http_method_names=['post'])),
    path("home-items", api_views.HomePageItemsAPI.as_view(http_method_names=['get'])),
    path("login", obtain_auth_token),
    path("signup", api_views.UserCreation.as_view(http_method_names=['post'])),
    path("user", api_views.GetUserWithToken.as_view(http_method_names=['post'])),
    path("profile", api_views.ProfileAPI.as_view(http_method_names=['get', 'post'])),
    path("password", api_views.PasswordAPI.as_view(http_method_names=['get', 'post'])),
    path("shipment", api_views.ShipmentAPI.as_view()),
    path("comments/<int:comment_id>", api_views.CommentsAPI.as_view()),
    path("comments/<int:page_num>/<int:page_size>/<int:item_id>", api_views.CommentsAPI.as_view()),
    path("comments/<int:page_num>/<int:page_size>/<int:item_id>/<str:username>", api_views.CommentsAPI.as_view()),
    path("comments", api_views.CommentsAPI.as_view()),
    path('reset', api_views.ResetCache.as_view()),
    path("image", api_views.ItemImageAPI.as_view()),
    path("image/<int:num>", api_views.ItemImageAPI.as_view()),
    path("WL/<str:token>/<int:item_id>", api_views.WishListAPI.as_view()),
    path("shipments/<int:page_num>/<int:page_size>", api_views.ShipmentListAPI.as_view()),
    path("shipments-items/<int:page_num>/<int:page_size>", api_views.ShipmentListItemsAPI.as_view()),
]