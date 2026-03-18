from django.urls import path

from .views import CreatePendingRequest, ListPendingRequests, ListMyOffers, HandlePendingRequest

urlpatterns = [
    path('create/', CreatePendingRequest.as_view(), name='pendingrequest_create'),
    path('list/', ListPendingRequests.as_view(), name='pendingrequest_list'),
    path('myoffers/', ListMyOffers.as_view(), name='pendingrequest_myoffers'),
    path('<int:pk>/action/', HandlePendingRequest.as_view(), name='pendingrequest_action')
]
