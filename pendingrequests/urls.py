from django.urls import path

from .views import CreatePendingRequest, ListPendingRequests, ListMyOffers

urlpatterns = [
    path('create/', CreatePendingRequest.as_view(), name='pendingrequest_create'),
    path('list/', ListPendingRequests.as_view(), name='pendingrequest_list'),
    path('myoffers/', ListMyOffers.as_view(), name='pendingrequest_myoffers')
]
