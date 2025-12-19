from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import generics

from pendingrequests.models import PendingRequest
from review.models import ItemReview,AccountReview
from .serializers import AccountReviewSerializerIncoming,ItemReviewSerializerIncoming,ItemReviewSerializer,AccountReviewSerializer
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED

class LeaveReview(APIView):
    def post(self,request):
        reviewType = request.data.get("about")
        if(reviewType=="item"):
           serializer = ItemReviewSerializerIncoming(data=request.data,context={"request":request}) #https://www.django-rest-framework.org/api-guide/serializers/#including-extra-context
        else:
            serializer = AccountReviewSerializerIncoming(data=request.data,context={"request":request})
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