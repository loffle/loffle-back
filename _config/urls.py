"""_config URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
from django.urls import path, include, re_path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.response import Response
from rest_framework.routers import DefaultRouter, APIRootView

import community.urls
import account.urls
import loffle.urls


class LoffleBackendAPIRootView(APIRootView):
    """
    로플의 백엔드 API Root
    """
    pass


router = DefaultRouter(trailing_slash=False)
router.APIRootView = LoffleBackendAPIRootView

router.registry.extend(community.urls.router.registry)
router.registry.extend(account.urls.router.registry)
router.registry.extend(loffle.urls.router.registry)

urlpatterns = [
    path('', include(router.urls)),
    # path('', include('community.urls'), name='community'),
    # path('', include('account.urls'), name='account'),
    # path('', include('loffle.urls'), name='loffle'),

    path('admin/', admin.site.urls),

    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    # path('api-token-auth', obtain_auth_token),
]

schema_view = get_schema_view(
    openapi.Info(
        title="Loffle API",
        default_version='v1',
        description="로플 백엔드의 REST API 문서",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="loffleback@gmail.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns += [
    re_path('swagger(?P<format>\\.json|\\.yaml)', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
