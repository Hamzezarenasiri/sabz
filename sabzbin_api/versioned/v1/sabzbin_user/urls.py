from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

from .routers import ROUTER

urlpatterns = [path('verification/token_refresh/', TokenRefreshView.as_view(), name='token-refresh'),
               path('verification/token_verify', TokenVerifyView.as_view(), name='token-verify'), ] + ROUTER.urls
