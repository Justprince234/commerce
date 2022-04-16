from django.urls import path

from knox import views as knox_views
from . import views
from .views import RegisterAPI, LoginAPIView, UserAPI, UserAPII

urlpatterns = [
    path('register/', RegisterAPI.as_view(), name='register'),
    path('login/', LoginAPIView.as_view(), name='login'),
    path('logout/', knox_views.LogoutView.as_view(), name='logout'),
    path('logoutall/', knox_views.LogoutAllView.as_view(), name='logoutall'),
    path('user/', UserAPI.as_view(), name='user'),
    path('userI/', UserAPII.as_view(), name='userI')
]