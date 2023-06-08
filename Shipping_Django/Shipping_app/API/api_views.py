from django.core.cache import cache
from django.views.decorators.cache import cache_page
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import ItemSerializer
from ..models import Item, Categories
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from django.utils.decorators import method_decorator


class UserCreation(APIView):

    @classmethod
    def post(cls, request):
        try:
            username = request.data.get("username")
            password = request.data.get("password")
            email = request.data.get("email", None)

            user = User.objects.create_user(username=username,
                                            password=password, email=email)
            token = Token.objects.create(user=user)
            return Response({"status": "success",
                             "msg": f"new user created. id: {user.id}",
                             "token": str(token)})
        except Exception as e:
            return Response({"status": "failed", "msg": f"Error:{e}"})


class ItemAPI(APIView):
    @classmethod
    def get(cls, request, action=None):
        if action is None:
            try:
                item_id = request.query_params.get('item_id')
                if item_id is None:
                    return Response(ItemSerializer(Item.objects.all(), many=True).data)
                else:
                    return Response(ItemSerializer(Item.objects.get(pk=item_id)).data)
            except Exception as e:
                return Response(f"Error: {e}")
        else:
            return Response(f"Cannot use the '{action}' action with the current method."
                            f" try removing the '/{action}'")

    @classmethod
    def post(cls, request, action=None):
        if action == "add":
            try:
                item = ItemSerializer(data=request.data)
                if item.is_valid():
                    item.save()
                    return Response("Item saved successfully")
                else:
                    return Response({"Error": item.errors})
            except Exception as e:
                return Response(f"Unknown error: {e}")
        else:
            return Response(f"Cannot use the '{action}' action with the current method."
                            f" try replacing the '/{action}' with '/add'")


@method_decorator(cache_page(60*15), name='dispatch')
class ItemPage(APIView):
    @classmethod
    def get(cls, request, page_num, page_size, category=None):
        items = []
        current_place = page_num * page_size
        end_place = current_place + page_size
        if category is not None and category != 'All':
            items = [category.item for category in Categories.objects.filter(
                category=cache.get('category_CAT_dict')[category])]
        else:
            items = Item.objects.filter()[current_place: end_place]

        if end_place > Item.objects.count():
            items = ItemSerializer(items, many=True).data
        else:
            items = ItemSerializer(items[current_place: Item.objects.count()], many=True).data

        return Response(
            {
                'lst': items,
                'size': len(items),
                'categories': cache.get('categories')
            }
        )


class ResetCache(APIView):
    @classmethod
    def get(cls, request):
        try:
            cache.set('category_CAT_dict', {c[1]: c[0] for c in Categories.categories}, timeout=None)
            cache.set('categories', [c[1] for c in Categories.categories], timeout=None)
            return Response('Cache reset complete')
        except Exception as e:
            print(e)
