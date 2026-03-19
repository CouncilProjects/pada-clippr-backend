from django.urls import path
from .views import SiteAnalyticsView

urlpatterns = [
    path('', SiteAnalyticsView.as_view(), name='site-analytics'),
]
