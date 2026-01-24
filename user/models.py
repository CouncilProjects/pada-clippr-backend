from django.db import models
from django.contrib.auth.models import AbstractUser

from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

from django.contrib.contenttypes.fields import GenericRelation


## i need a function to make the path at runtime, also we change the file names so there is no collition.
def dynamic_image_upload_path(instance, filename):
    import os
    import uuid
    
    ext = os.path.splitext(filename)[1]
    unique_name = f"{uuid.uuid4().hex}{ext}"
    
    # Use the upload_to from the instance if set, otherwise use model name
    if hasattr(instance, 'upload_to') and instance.upload_to:
        custom_dir = instance.upload_to
    else:
        if instance.content_type:
            custom_dir = instance.content_type.model
        else:
            custom_dir = 'unknown'
    
    return f"{custom_dir}/{unique_name}"

# here we will create a generic image, so we can use it in other models as well. 
class Image(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    image=models.ImageField(upload_to=dynamic_image_upload_path) # the upload_to can take a callable.
    created_at = models.DateTimeField(auto_now_add=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering= ['order','created_at']
        indexes = [
            models.Index(fields=['content_type', 'object_id']),
        ]

class SocialLink(models.Model):

    SOCIAL_CHOICES = [
        ('facebook', 'Facebook'),
        ('youtube', 'YouTube'),
        ('instagram', 'Instagram'),
        ('whatsapp', 'WhatsApp'),
        ('twitter', 'X (Twitter)'),
        ('snapchat', 'Snapchat'),
        ('linkedin', 'LinkedIn'),
        ('pinterest', 'Pinterest'),
        ('email','Email')
    ]
        

    user = models.ForeignKey('User', on_delete=models.CASCADE,related_name='social_links')

    platform = models.CharField(max_length=30, choices=SOCIAL_CHOICES)
    url = models.URLField(blank=True)

    class Meta:
        unique_together = ('user', 'platform')

    def __str__(self):
        return f"{self.user.username} - {self.platform}"


class User(AbstractUser):
    # AbstractUser already includes: username, email, password, first_name, last_name
    phone = models.CharField(max_length=20, blank=True)
    is_verified_seller = models.BooleanField(default=False)

    avatar = GenericRelation(Image)

    def __str__(self):
        return self.username

    def get_role_name(self):
        
        if not self.is_authenticated:
            return 'ANONYMOUS'
        if self.is_staff or self.is_superuser:
            
            return 'ADMIN'
        if self.is_verified_seller:
            return 'SELLER'
        return 'MEMBER'

        

