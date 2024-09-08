"""
URL configuration for communal_task project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from rest_framework.routers import DefaultRouter
from home.views import (ApartmentDetailView,
                        UtilityBillCalculationView,
                        ApartmentCreateView,
                        MeterDetailView,
                        MeterViewSet,
                        MeterTypeViewSet,
                        HouseListViewSet,
                        HouseDetailView,
                        MetersByHouseView,
                        TaskResultView)
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from drf_yasg import openapi

schema_view = get_schema_view(
   openapi.Info(
      title="Your API",
      default_version='v1',
      description="API documentation",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="contact@yourapi.com"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=[permissions.AllowAny],
)

router = DefaultRouter()
router.register(r'houses', HouseListViewSet)
router.register(r'meters', MeterViewSet)
router.register(r'meter-types', MeterTypeViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/house/<int:id>/', HouseDetailView.as_view(), name = 'house-detail'),
    path('api/house/<int:house_id>/calculate_bills/', UtilityBillCalculationView.as_view(), name='calculate_bills'),
    path('api/apartments/', ApartmentCreateView.as_view(), name='apartment-create'),
    path('api/apartment/<int:id>/', ApartmentDetailView.as_view(), name='apartment-detail'),
    path('api/meters/house/<int:house_id>/', MetersByHouseView.as_view(), name='meters-by-house'),
    path('api/meter/<int:id>/', MeterDetailView.as_view(), name='meter-detail'),
    path('api/tasks/<str:task_id>/result/', TaskResultView.as_view(), name='task_status'),
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
