from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import generics

from pendingrequests.models import PendingRequest
from review.models import ItemReview,AccountReview
from .serializers import AccountReviewSerializerIncoming,ItemReviewSerializerIncoming,ItemReviewSerializer,AccountReviewSerializer
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED
from rest_framework.generics import GenericAPIView
from rest_framework import serializers
from drf_spectacular.utils import extend_schema, OpenApiTypes,inline_serializer

from rest_framework import serializers

def add_about_field(serializer_class):
    """
    Returns a new serializer class identical to `serializer_class`
    but with an extra `about` field.
    """
    class SerializerWithAbout(serializer_class):
        about = serializers.ChoiceField(
            choices=["item", "account"],
            help_text="Determines which serializer should process this review"
        )

        class Meta(serializer_class.Meta):
            # include all original fields + 'about'
            fields = list(serializer_class.Meta.fields) + ['about']
    
    return SerializerWithAbout


class LeaveReview(GenericAPIView):
    def get_serializer_class(self):
        if self.request.data.get("about") =="item":
            return ItemReviewSerializerIncoming
        else:
            return AccountReviewSerializerIncoming
    
    @extend_schema(
        summary="Leave a review",
        description=(
        "Create a review for either an item or a user account.\n\n"
        "- Set `about` to `item` to review an item\n"
        "- Set `about` to `account` to review a seller/buyer\n\n"
        "The request body changes depending on the value of `about`."
        ),
        request=add_about_field(AccountReviewSerializerIncoming)
    )
    def post(self,request):
        serializer = self.get_serializer(data=request.data,context={"request":request})  #https://www.django-rest-framework.org/api-guide/serializers/#including-extra-context
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=HTTP_201_CREATED)
        
class ItemReviewsList(generics.ListAPIView):
    #queryset=ItemReview.objects.all() needed something more specific
    serializer_class=ItemReviewSerializer
    def get_queryset(self):
        item_id = self.kwargs["item_id"]
        return ItemReview.objects.filter(item__id=item_id)

class AccountReviewsList(generics.ListAPIView):
    serializer_class=AccountReviewSerializer
    def get_queryset(self):
        username = self.kwargs["username"]
        return AccountReview.objects.filter(seller__username=username)