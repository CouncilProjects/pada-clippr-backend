from .models import SiteAnalytics, SellerAnalytics
from .serializers import SiteAnalyticsSerializer, SellerAnalyticsSerializer
from rest_framework import serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from user.permissions import IsAdmin, IsVerifiedSeller
from django.utils import timezone
from drf_spectacular.utils import extend_schema, inline_serializer
from drf_spectacular.utils import OpenApiResponse, PolymorphicProxySerializer

class SiteAnalyticsView(APIView):
    permission_classes = [IsAdmin | IsVerifiedSeller]

    @extend_schema(responses={200: OpenApiResponse(
        description="Returns either site-wide or seller-specific analytics depending on the user role.",
        response=PolymorphicProxySerializer(
            serializers=[
                inline_serializer(name="SiteAnalyticsResponse", fields={
                    "requested_at": serializers.DateTimeField(),
                    "last_update": serializers.DateTimeField(allow_null=True),
                    "data": SiteAnalyticsSerializer(many=True),
                }),
                inline_serializer(name="SellerAnalyticsResponse", fields={
                    "requested_at": serializers.DateTimeField(),
                    "last_update": serializers.DateTimeField(allow_null=True),
                    "data": SellerAnalyticsSerializer(many=True),
                }),
            ],
            component_name="AnalyticsResponse",
            resource_type_field_name=None
        )
    )})
    def get(self, request, *args, **kwargs):
        if request.user.is_verified_seller:
            newest = SellerAnalytics.objects.order_by("created_at").reverse()[:48]
            return Response({
                "requested_at": timezone.now(),
                "last_update": newest[0].created_at if newest else None,
                "data": SellerAnalyticsSerializer(newest, many=True).data[::-1]
            })
        else:
            newest = SiteAnalytics.objects.order_by("created_at").reverse()[:48]
            return Response({
                "requested_at": timezone.now(),
                "last_update": newest[0].created_at if newest else None,
                "data": SiteAnalyticsSerializer(newest, many=True).data[::-1]
            })
