from decimal import Decimal
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.viewsets import ModelViewSet
from django.db.models import Avg, DecimalField
from django.db.models.functions import Coalesce
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser 
from django.db import transaction
import json
from django.db.models.query import Q
import operator
from functools import reduce
import re
import shlex
from .models import Item, Tag
from .models import Item
from .serializers import ItemImageUploadSerializer,ItemSerializer, ItemBasicSerializer
from drf_spectacular.utils import extend_schema,OpenApiParameter,OpenApiTypes

class MyItems(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class=ItemBasicSerializer
    def get(self, request):
        user = request.user
        items = Item.objects.filter(
            seller=user,
            stock__gt=0
        ).annotate(rating=Coalesce(Avg("reviews__rating"),-0.1,output_field=DecimalField()))

        return Response({"items": self.get_serializer(items,many=True).data}, status=status.HTTP_200_OK)


class CreateItem(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    @transaction.atomic
    def post(self, request):
        user = request.user
        data = request.data

        try:
            # Parse tag array (Svelte sends JSON string)
            tag_names = json.loads(data.get('tags', '[]'))

            # Create item first
            item = Item.objects.create(
                seller=user,
                title=data.get('title'),
                description=data.get('description'),
                price=data.get('price'),
                stock=data.get('stock'),
                negotiable=data.get('negotiable', False) == 'true',
                min_negotiable_price=data.get('min_negotiable_price')
            )

            # Add tags
            for name in tag_names:
                name = re.sub("[\s_]", "-", name.lower()) # lowercase and dashes as separators
                name = re.sub("[^a-z0-9-]", "", name) # keep only letters and numbers
                name = re.sub("^-*|-*$|-{2,}", "", name) # remove leading, trailing, duplicate dashes
                if len(name) == 0: continue

                tag, _ = Tag.objects.get_or_create(name=name)
                item.tags.add(tag)

            image_serializer = ItemImageUploadSerializer(data={'images': request.FILES.getlist('images')})

            if image_serializer.is_valid():
                image_serializer.save(item=item)
            else:
                return Response(image_serializer.errors, status=400)

            return Response({"detail": "Item created successfully!"}, status=201)

        except Exception as e:
            return Response({"detail": str(e)}, status=400)

class ItemPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'amount'
    max_page_size = 100

class ItemViewSet(ModelViewSet):
    queryset = Item.objects.annotate(rating=Coalesce(Avg("reviews__rating"),Decimal("-0.1"),output_field=DecimalField(max_digits=2,decimal_places=1))).all()
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

    @extend_schema(
            parameters=[
                OpenApiParameter(name="q",type=OpenApiTypes.STR,location=OpenApiParameter.QUERY,required=False),
                OpenApiParameter(name="t",type=OpenApiTypes.STR,location=OpenApiParameter.QUERY,required=False),
                OpenApiParameter(name="u",type=OpenApiTypes.STR,location=OpenApiParameter.QUERY,required=False),
                OpenApiParameter(name="e",type=OpenApiTypes.BOOL,location=OpenApiParameter.QUERY,required=False)
            ]
    )
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        creator_id = request.query_params.get("u", "").strip()
        expandSearch = request.query_params.get("e", "false").lower() in ['true','yes','1']

        if creator_id:
            try:
                creator_id = int(creator_id)
            except (TypeError, ValueError):
                creator_id = -1
            queryset = queryset.filter(seller__id=creator_id)

        name_sample = request.query_params.get("q", "").strip()
        name_parts = shlex.split(name_sample)

        tag_list = re.split(",", request.query_params.get("t", ""))
        tag_list = [tag.strip() for tag in tag_list if len(tag.strip()) > 0]
        print(tag_list)

        if name_sample:
            queries = []
            for part in name_parts:
                q = Q(title__icontains=part)
                if(expandSearch):
                    q |= Q(description__icontains=part)
                queries.append(q)
            condition = reduce(operator.or_, queries)
            queryset = queryset.filter(condition)

        for tag in tag_list:
            queryset = queryset.filter(Q(tags__name=tag))

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
