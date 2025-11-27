from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction

from .models import Item, Tag


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
