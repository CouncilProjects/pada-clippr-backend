from rest_framework.pagination import PageNumberPagination
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response

from user.permissions import IsMember
from .models import Item
from .serializers import ItemSerializer, ItemBasicSerializer

class ItemPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'amount'
    max_page_size = 100

class ItemViewSet(ModelViewSet):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    list_serializer_class = ItemBasicSerializer
    pagination_class = ItemPagination
    permission_classes = [IsMember]

    def perform_create(self, serializer):
        serializer.save(seller=self.request.user)

    def get_serializer_class(self):
        if self.action == 'list':
            return self.list_serializer_class
        return super().get_serializer_class()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        search = request.query_params.get("q", "").strip()
        if search:
            queryset = queryset.filter(title__icontains=search)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
