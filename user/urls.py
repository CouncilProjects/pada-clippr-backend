from django.urls import path
from .views import Register, Login, Logout, Refresh,AvatarUpload

urlpatterns = [
    path('register/', Register.as_view(), name='user_register'),
    path('login/', Login.as_view(), name='user_login'),
    path('logout/', Logout.as_view(), name='user_logout'),
    path('refresh/', Refresh.as_view(), name='user_refresh'),

    path("avatar/",AvatarUpload.as_view(),name="user_upload")
]
