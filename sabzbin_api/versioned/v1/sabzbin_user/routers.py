"""
V1 api routers
"""
from rest_framework import routers

from .views import *
from django.urls import path
from rest_framework import routers

from . import views

ROUTER = routers.SimpleRouter()
ROUTER.register(r'profile', views.ProfileAPIViewSet, basename="profile")
ROUTER.register(r'address', views.AddressAPIViewSet, basename="address")
ROUTER.register(r'verification', views.VerificationViewSet, basename="verification")

api_user_urlpatterns = [

]
api_user_urlpatterns += ROUTER.urls