from rest_framework.pagination import PageNumberPagination
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response

from rest_framework.permissions import IsAuthenticated
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
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(seller=self.request.user)

    def get_serializer_class(self):
        if self.action == 'list':
            return self.list_serializer_class
        return super().get_serializer_class()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        creator_id = request.query_params.get("u", "").strip()
        if creator_id:
            try:
                creator_id = int(creator_id)
            except (TypeError, ValueError):
                creator_id = -1
            queryset = queryset.filter(seller__id=creator_id)

        name_sample = request.query_params.get("q", "").strip()
        if name_sample:
            queryset = queryset.filter(title__icontains=name_sample)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
