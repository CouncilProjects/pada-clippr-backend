from django.urls import path
from .views import my_items, create_item

urlpatterns = [
    path('my-items/', my_items, name='my-items'),
     path('create/', create_item, name='create-item'),
]