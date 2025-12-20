from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ItemViewSet,MyItems, CreateItem

router = DefaultRouter()
router.register('', ItemViewSet)



urlpatterns = [
    path('my-clippings/', MyItems.as_view(), name='my-items'),
    path('my-clippings/create/', CreateItem.as_view(), name='create-item'),
    path('',include(router.urls))
]
