from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from .serializers import ItemSerializer
from ..models import Item, Categories


class ItemAPI(APIView):
    @classmethod
    def get(cls, request, action=None):
        if action is None:
            try:
                item_id = request.query_params.get('item_id')
                if item_id is None:
                    return Response(ItemSerializer(Item.objects.all(), many=True).data)
                else:
                    return Response({"": ItemSerializer(Item.objects.get(pk=item_id)).data})
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


class ItemPage(APIView):
    @classmethod
    def get(cls, request, page_num, page_size, category):
        current_place = page_num * page_size
        items = [category.item for category in Categories.objects.filter(category=category)]
        return Response(
            {
                'lst':
                    ItemSerializer(items[current_place: current_place + page_size], many=True).data,
                'size': len(Item.objects.all())
            }
        )