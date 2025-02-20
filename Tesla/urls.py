"""
URL configuration for Tesla project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from rest_framework_jwt.views import obtain_jwt_token
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from beifan import views
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView


from rest_framework import routers


# router = routers.DefaultRouter()
# router.register('feedback', views.FeedBackViewsSet)

urlpatterns = [
    # path("", TemplateView.as_view(template_name="admin/index.html")),
    path('api/schema.openapi.json', SpectacularAPIView.as_view(), name="schema"),
    path('api/schema/swagger/', SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    # path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path("admin/", admin.site.urls),
    path("", include("beifan.urls")),
    path("beifan/", include("beifan.urls")),
    path('api/account/', include('account.urls')),
    path("api/system/", include("system.urls")),
    path("api/project/", include("project.urls")),
    path("api/case_api/", include("case_api.urls")),
    path("", include("snippet.urls")),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]