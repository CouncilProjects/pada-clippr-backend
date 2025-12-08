from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ItemViewSet,my_items, create_item

router = DefaultRouter()
router.register('', ItemViewSet)



urlpatterns = [
    path('',include(router.urls))
    path('my-items/', my_items, name='my-items'),
     path('create/', create_item, name='create-item'),
]