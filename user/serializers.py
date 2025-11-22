import os
import uuid
from rest_framework import serializers
from .models import User,SocialLink

from .models import Image

class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ['id', 'image', 'order']
        read_only_fields = ['id']


class UserSerializer(serializers.ModelSerializer):
    avatar = ImageSerializer(many=True, read_only=True)
    class Meta:
        model = User
        fields = '__all__'

class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, min_length=8)
    email = serializers.EmailField(required=True)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'first_name', 'last_name']

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

class ImageUploadMixin:
    """
    Mixin to handle image uploads for any model with a GenericRelation to Image
    """
    image_config = {
        'max_images': None,  # None = unlimited
        'upload_to': '',  # Subdirectory within MEDIA_ROOT/uploads
    }
    
    def get_image_config(self):
        # this is overriden in any serializer we use the mixin 
        return self.image_config
    
    def validate_images(self, images_data):
        """Validate number of images"""
        config = self.get_image_config()
        max_images = config.get('max_images')
        print(f"{max_images} and {len(images_data)} is such.")
        if max_images and len(images_data) > max_images:
            raise serializers.ValidationError(
                f"Maximum {max_images} image{'s' if max_images > 1 else ''} allowed."
            )
        
        return images_data
    
    def create_images(self, instance, images_data):
        config = self.get_image_config()
        upload_to = config.get('upload_to', '')
        
        created_images = []
        for idx, image_data in enumerate(images_data):
            # Create the Image
            image = Image(
                content_object=instance,
                order=image_data.get('order', idx)
            )
            
            # Set upload_to
            image.upload_to = upload_to
            
            # Now set the image file - this will trigger the upload_to callable
            image.image = image_data.get('image')
            image.save()
            created_images.append(image)
        
        return created_images
    
    def update_images(self, instance, images_data):
        """Helper to update Image objects - deletes old and creates new"""
        # Delete existing images
        instance.images.all().delete()
        
        # Create new ones
        return self.create_images(instance, images_data)


class AvatarUploadSerializer(ImageUploadMixin,serializers.Serializer):
    image = serializers.ImageField()

    #for multiple images 
    """ images = serializers.ListField(
        child=serializers.ImageField()
    )"""

    # here we set how many images can be uploaded. and where.
    image_config={
        'max_images':1,
        'upload_to':'avatars/'
    }

    def save(self, user):
        # Convert the 1 image into mixin's multi-image format:

        images_data = [{
            'image': self.validated_data['image']
        }]

        # Validate: checks max_images = 1
        self.validate_images(images_data)

        # Remove old avatars
        user.avatar.all().delete()

        # Create new avatar using mixin's standardized logic
        self.create_images(user, images_data)
        return user

class UserBasicSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','username', 'first_name', 'last_name']

class SocialLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model=SocialLink
        fields="__all__"