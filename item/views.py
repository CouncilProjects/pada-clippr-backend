from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response

from user.permissions import IsMember
from .models import Item
from .serializers import ItemSerializer, ItemBasicSerializer

class ItemViewSet(ModelViewSet):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    list_serializer_class = ItemBasicSerializer
    permission_classes = [IsMember]

    def perform_create(self, serializer):
        print(self.request.user)
        serializer.save(seller=self.request.user)

    def get_serializer_class(self):
        if self.action == 'list':
            return self.list_serializer_class
        return super().get_serializer_class()
