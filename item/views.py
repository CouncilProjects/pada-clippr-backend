from rest_framework.viewsets import ModelViewSet

from user.permissions import IsMember
from .models import Item
from .serializers import ItemSerializer

class ItemViewSet(ModelViewSet):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    permission_classes = [IsMember]

    def perform_create(self, serializer):
        print(self.request.user)
        serializer.save(seller=self.request.user)
