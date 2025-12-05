from rest_framework import serializers
from user.serializers import UserBasicSerializer, SellerUserSerializer
from .models import Item

class ItemSerializer(serializers.ModelSerializer):
    seller = UserBasicSerializer(read_only=True)

    class Meta:
        model = Item
        fields = '__all__'
        read_only_fields = ['seller', 'created_at', 'updated_at']

class ItemBasicSerializer(serializers.ModelSerializer):
    seller = SellerUserSerializer()

    class Meta:
        model = Item
        fields = [
            'id', 'title', 'price', 'stock',
            'negotiable', 'seller'
        ]
