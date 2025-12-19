from django.urls import path
from .views import LeaveReview,AccountReviewsList,ItemReviewsList

urlpatterns = [
    path('item/<int:item_id>/',ItemReviewsList.as_view()),
    path('account/<str:username>/',AccountReviewsList.as_view()),
    path('create/',LeaveReview.as_view())
]