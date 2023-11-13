from rest_framework import serializers
from ..models import Item, Comment, Shipment, CategoryOptions


class ItemSerializer(serializers.ModelSerializer):

    class Meta:
        model = Item
        fields = '__all__'


class CommentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Comment
        fields = '__all__'


class ShipmentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Shipment
        fields = ['id', 'order_date']


class CategoryOptionsSerializer(serializers.ModelSerializer):

    class Meta:
        model = CategoryOptions
        fields = ['category']
