from django.core.cache import cache
from django.db.models import Q
from django.views.decorators.cache import cache_page
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import ItemSerializer, CommentSerializer
from ..models import Item, Categories, Shipment, ShipmentList, Comment, WishList
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


class GetUserWithToken(APIView):
    @classmethod
    def post(cls, request):
        return Response(
            Token.objects.get(key=request.data['token']).user.username
        )


class ItemAPI(APIView):
    @classmethod
    def get(cls, request):
        try:
            item_id = request.query_params.get('item_id')
            if item_id is None:
                return Response(ItemSerializer(Item.objects.all(), many=True).data)
            else:
                return Response(ItemSerializer(Item.objects.get(pk=item_id)).data)
        except Exception as e:
            return Response(f"Error: {e}")


class ItemPageAPI(APIView):
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


class ShipmentAPI(APIView):
    @classmethod
    def post(cls, request):
        data = request.data['data']
        shipment = Shipment(user=Token.objects.get(key=request.data['token']).user)
        shipment.save()
        for _id in [item['id'] for item in data]:
            ShipmentList(shipment=shipment, item=Item.objects.get(id=_id)).save()
        return Response('ok')


class ItemImageAPI(APIView):
    @classmethod
    def post(cls, request, num=None):
        data = request.data['data']
        if num is None:
            res = [f"items/{image.image}" for image in Item.objects.get(pk=data).Item_image.all()]
        else:
            res = f"items/{Item.objects.get(pk=data).Item_image.all()[num].image}"
        return Response(res)


class FilterAPI(APIView):
    @classmethod
    def post(cls, request, page_num, page_size):
        data = request.data['filters']
        if not data['category'] and data['price'] == 0 and data['name'] == '':
            return Response({
                'lst': [],
                'size': 0,
                'categories': cache.get('categories')
            })
        res = Categories.objects.none()
        current_place = page_num * page_size
        end_place = current_place + page_size

        if len(data['category']) != 0:
            for c in data['category']:
                res = res | Categories.objects.filter(
                    category=cache.get('category_CAT_dict')[c]
                )
        else:
            res = Categories.objects.filter()

        if int(data['price']) != 0:
            if data['priceType'] == '>':
                res = res.filter(item__price__gt=data['price'])
            if data['priceType'] == '<':
                res = res.filter(item__price__lt=data['price'])
            if data['priceType'] == '=':
                res = res.filter(item__price=data['price'])

        if data['name'] != '':
            res = res.filter(item__name=data['name'])

        res = [r.item for r in res]

        items = ItemSerializer(list(set(res))[current_place: end_place], many=True).data

        return Response(
            {
                'lst': items,
                'size': len(items),
                'categories': cache.get('categories')
            }
        )


def all_rating(item_id):
    rating = 0
    lst = Item.objects.get(id=item_id).Item_comment.filter()
    for i in lst:
        rating += i.rating
    return rating / len(lst)


class CommentsAPI(APIView):
    @classmethod
    def get(cls, request, page_num, page_size, item_id):
        rating = 0
        current_place = page_num * page_size
        end_place = current_place + page_size

        comments = CommentSerializer(Item.objects.get(id=item_id).Item_comment.filter()
                                     [current_place: end_place], many=True).data
        if Item.objects.get(id=item_id).Item_comment.count() == 0:
            return Response(
                {'comments': [],
                 'rating': 0,
                 'size': Item.objects.get(id=item_id).Item_comment.count()
                 }
            )
        else:
            for c in comments:
                c['user'] = User.objects.get(pk=c['user']).username
            return Response(
                {'comments': comments,
                 'rating': all_rating(item_id),
                 'size': Item.objects.get(id=item_id).Item_comment.count()
                 }
            )


class AddCommentAPI(APIView):
    @classmethod
    def post(cls, request):
        data = request.data['data']
        try:
            Comment(user=Token.objects.get(key=data['Token']).user,
                    comment_text=data['comment'], rating=data['commentRating'],
                    item=Item.objects.get(pk=data['item'])).save()
        except Exception as e:
            print(e)
            if str(e) == 'UNIQUE constraint failed: Shipping_app_comment.user_id, Shipping_app_comment.item_id':
                return Response({'msg': 'You cannot comment on this item more than once',
                                 'color': 'red'})
            else:
                return Response({'msg': str(e),
                                 'color': 'red'})
        return Response('')


class HomePageItemsAPI(APIView):
    @classmethod
    def get(cls, request):
        try:
            res = ItemSerializer(Item.objects.filter()[Item.objects.count() - 3:Item.objects.count()], many=True)
        except:
            res = ItemSerializer(Item.objects.filter()[0:Item.objects.count()], many=True)
        return Response(res.data)


class WishListAPI(APIView):
    @classmethod
    def get(cls, request, username, item_id):
        if User.objects.filter(username=username):
            return Response(bool(WishList.objects.filter(user__username=username, item__id=item_id)))

    @classmethod
    def post(cls, request, username, item_id):
        if User.objects.filter(username=username):
            wl = WishList.objects.filter(user__username=username, item__id=item_id)
            if wl and request.data['data']:
                wl.delete()
            else:
                WishList(user=User.objects.get(username=username), item=Item.objects.get(id=item_id)).save()
            return Response(bool(WishList.objects.filter(user__username=username, item__id=item_id)))


class SearchAPI(APIView):
    @classmethod
    def post(cls, request, page_num, page_size):
        data = request.data['param']
        if data:
            current_place = page_num * page_size
            end_place = current_place + page_size

            items = ItemSerializer(Item.objects.filter(
                Q(name__contains=data) |
                Q(description__contains=data)
            ), many=True).data
            return Response(
                {
                    'lst': items,
                    'size': len(items),
                }
            )
        else:
            return Response()
