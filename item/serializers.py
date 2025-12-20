from rest_framework import serializers
from user.serializers import UserBasicSerializer, SellerUserSerializer
from .models import Item
from user.serializers import ImageUploadMixin, ImageSerializer

class ItemSerializer(serializers.ModelSerializer):
    seller = UserBasicSerializer(read_only=True)

    class Meta:
        model = Item
        fields = '__all__'
        read_only_fields = ['seller', 'created_at', 'updated_at']

class ItemBasicSerializer(serializers.ModelSerializer):
    seller = SellerUserSerializer()
    rating = serializers.DecimalField(decimal_places=1,max_digits=2,read_only=True)
    class Meta:
        model = Item
        fields = [
            'id', 'title', 'price', 'stock',
            'negotiable', 'seller','rating'
        ]

class ItemImageUploadSerializer(ImageUploadMixin, serializers.Serializer):
    images = serializers.ListField(
        child=serializers.ImageField(),
        required=False
    )

    # This controls the mixin behavior
    image_config = {
        'max_images': 3,
        'upload_to': 'items/'
    }

    def save(self, item):
        images_data = [
            {
                'image': img,
                'order': idx
            }
            for idx, img in enumerate(self.validated_data.get('images', []))
        ]

        if images_data:
            self.validate_images(images_data)
            self.create_images(item, images_data)

        return item
    
