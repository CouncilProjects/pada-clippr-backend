from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.viewsets import ModelViewSet
from rest_framework import status
from django.db import transaction

from .models import Item, Tag
from user.permissions import IsMember
from .models import Item
from .serializers import ItemSerializer, ItemBasicSerializer


class MyItems(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        items = Item.objects.filter(
            seller=user,
            stock__gt=0
        ).values('id', 'title', 'price')

        return Response({"items": list(items)}, status=status.HTTP_200_OK)


class CreateItem(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        user = request.user
        data = request.data

        try:
            item = Item.objects.create(
                seller=user,
                title=data.get('title'),
                description=data.get('description'),
                price=data.get('price'),
                stock=data.get('stock'),
                negotiable=data.get('negotiable', False),
                min_negotiable_price=data.get('min_negotiable_price')
            )

            # Create or attach tags
            tag_names = data.get('tags', [])
            for name in tag_names:
                tag, _ = Tag.objects.get_or_create(name=name)
                item.tags.add(tag)

            return Response(
                {"detail": "Item created successfully!"},
                status=status.HTTP_201_CREATED
            )

        except Exception as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
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
