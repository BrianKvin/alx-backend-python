from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from chats.auth import CustomTokenObtainPairView

urlpatterns = [
    path('', admin.site.urls),  # Make admin the default page
    path('admin/', admin.site.urls),  # Keep the admin URL for explicit access
    path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/', include('chats.urls')), 
]