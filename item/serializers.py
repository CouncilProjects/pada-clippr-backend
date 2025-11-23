from rest_framework import serializers
from user.serializers import UserBasicSerializer
from .models import Item

class ItemSerializer(serializers.ModelSerializer):
    seller = UserBasicSerializer(read_only=True)

    class Meta:
        model = Item
        fields = '__all__'
        read_only_fields = ['seller', 'created_at', 'updated_at']

class ItemBasicSerializer(serializers.ModelSerializer):
    seller = UserBasicSerializer()

    class Meta:
        model = Item
        fields = [
            'id', 'seller', 'updated_at',
            'title', 'description',
            'price', 'negotiable'
        ]
