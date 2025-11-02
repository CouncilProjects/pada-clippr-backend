from django.urls import path
from .views import Register, Login, Refresh

urlpatterns = [
    path('register/', Register.as_view(), name='user_register'),
    path('login/', Login.as_view(), name='user_login'),
    path('refresh/', Refresh.as_view(), name='user_refresh'),
]
