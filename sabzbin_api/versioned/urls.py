from django.urls import path, include

from sabzbin_api.versioned.v1.sabzbin_user.urls import urlpatterns as v1_urlpatterns

urlpatterns = [
    path('v1/', include(v1_urlpatterns))
]
