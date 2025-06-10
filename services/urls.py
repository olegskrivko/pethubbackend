# services/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ServiceViewSet,  ReviewListCreateView # ServiceDetailView,

router = DefaultRouter()
router.register(r'', ServiceViewSet)  # Register ServiceViewSet for the list of services

urlpatterns = [
    path('', include(router.urls)),  # Register the ServiceViewSet URLs under `/api/services/`
    # path('<int:id>/', ServiceDetailView.as_view(), name='service-detail'),  # Individual service detail view
    path('<int:service_id>/reviews/', ReviewListCreateView.as_view(), name='service-reviews'),


]