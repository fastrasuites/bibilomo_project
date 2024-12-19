from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import AdminLoginView, AdminRegisterView, FlightPackageRetrieveViewSet, \
    FlightPackageCreateViewSet, FlightPackageUpdateDeleteViewSet, BookingApplicationCreateViewSet, \
    BookingApplicationRetrieveUpdateDeleteViewSet, ContactMessageCreateViewSet, \
    ContactMessageRetrieveUpdateDeleteViewSet

router = DefaultRouter()
router.register(r'flight/packages', FlightPackageRetrieveViewSet, basename='r_package')
router.register(r'flight/package', FlightPackageCreateViewSet, basename='c_package')
router.register(r'flight/packages', FlightPackageUpdateDeleteViewSet, basename='ud_package')
router.register(r'flight/booking-applications', BookingApplicationRetrieveUpdateDeleteViewSet, basename='rud_booking')
router.register(r'flight/booking-application', BookingApplicationCreateViewSet, basename='c_booking')
router.register(r'flight/contact-messages', ContactMessageRetrieveUpdateDeleteViewSet, basename='rud_message')
router.register(r'flight/contact-message', ContactMessageCreateViewSet, basename='c_message')

urlpatterns = [
    path('admin/register', AdminRegisterView.as_view(), name='admin_register'),
    path('admin/login/', AdminLoginView.as_view(), name='admin_login'),
    path('', include(router.urls)),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
