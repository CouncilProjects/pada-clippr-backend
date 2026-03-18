from decimal import Decimal, InvalidOperation

from rest_framework import serializers

from item.models import Item
from .models import PendingRequest



class PendingRequestSerializer(serializers.ModelSerializer):
    item_id = serializers.IntegerField(source='item.id', read_only=True)
    item_title = serializers.CharField(source='item.title', read_only=True)
    buyer_username = serializers.CharField(source='buyer.username', read_only=True)
    seller_username = serializers.CharField(source='item.seller.username', read_only=True)

    class Meta:
        model = PendingRequest
        fields = [
            'id',
            'item_id',
            'item_title',
            'buyer_username',
            'seller_username',
            'quantity',
            'offer_price',
            'message',
            'created_at',
        ]


class PendingRequestCreateSerializer(serializers.Serializer):
    item_id = serializers.IntegerField()
    message = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    quantity = serializers.IntegerField(required=False, default=1, min_value=1)
    offer_price = serializers.DecimalField(
        max_digits=10, decimal_places=2, required=False, allow_null=True
    )

    def validate_item_id(self, value):
        try:
            return Item.objects.get(pk=value)
        except Item.DoesNotExist:
            raise serializers.ValidationError('Item not found.')

    def validate(self, data):
        item = data.get('item_id')
        offer_price = data.get('offer_price')

        if offer_price is not None and not item.negotiable:
            raise serializers.ValidationError('This item is not negotiable.')

        if offer_price is not None:
            try:
                # Ensure we can parse it as Decimal
                Decimal(offer_price)
            except (InvalidOperation, TypeError):
                raise serializers.ValidationError('Invalid offer price.')

        return data

    def create(self, validated_data):
        item = validated_data['item_id']
        return PendingRequest.objects.create(
            buyer=self.context['request'].user,
            item=item,
            message=validated_data.get('message', ''),
            quantity=validated_data.get('quantity', 1),
            offer_price=validated_data.get('offer_price'),
        )
    
    
