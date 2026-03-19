from django.db import models
from django.contrib.contenttypes.fields import GenericRelation
from user.models import User, Image

class Item(models.Model):
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='items')
    title = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    negotiable = models.BooleanField(default=False)

    tags = models.ManyToManyField('Tag', related_name='items', blank=True)
    
    images = GenericRelation(Image)

    views = models.IntegerField(default=0)
    last_viewed = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} by {self.seller.username}"

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name
