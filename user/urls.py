from django.urls import path
from .views import Register, Login, Logout, Refresh,AvatarUpload,UserBasicListView,UserViewSet
from django.urls import include
from rest_framework.routers import DefaultRouter


router = DefaultRouter()

router.register('',UserViewSet) #loads all the routes that the viewSet produces (custon and default ones)
urlpatterns = [
    path('register/', Register.as_view(), name='user_register'),
    path('login/', Login.as_view(), name='user_login'),
    path('logout/', Logout.as_view(), name='user_logout'),
    path('refresh/', Refresh.as_view(), name='user_refresh'),

    path("avatar/",AvatarUpload.as_view(),name="user_upload"),
    path("list/",UserBasicListView.as_view(),name="user_upload"),
    path('',include(router.urls))
]
