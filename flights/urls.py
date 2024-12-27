from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from rest_framework.routers import DefaultRouter

# from .views import AdminLoginView, AdminRegisterView, FlightPackageRetrieveViewSet, \
#     FlightPackageCreateViewSet, FlightPackageUpdateDeleteViewSet, BookingApplicationViewSet, \
#     ContactMessageCreateViewSet, ContactMessageRetrieveUpdateDeleteViewSet

from .views import AdminLoginView, AdminRegisterView

# from .views import FlightPackageModelViewset, FlightPackageReadViewset, BookingApplicationModelViewSet, \
#     BookingApplicationCreateViewset, ContactMessageModelViewset, ContactMessageCreateViewset

# for FlightPackage
from .views import FlightPackageReadViewSet, NotAdminFlightPackageAdditionalViewSet, FlightPackageCreateUpdateViewSet, \
    FlightPackageArchiveRestoreListDetailViewSet

# for BookingApplication
from .views import BookingApplicationCreateViewSet, AdminBookingApplicationAdditionalViewSet, \
    BookingApplicationListRetrieveViewSet, BookingApplicationUpdateViewSet, \
    BookingApplicationArchiveRestoreListDetailViewSet

# for ContactMessage
from .views import ContactMessageCreateViewSet, AdminContactMessageAdditionalViewSet, \
    ContactMessageListRetrieveViewSet, ContactMessageUpdateViewSet, ContactMessageArchiveRestoreListDetailViewSet

router = DefaultRouter()
# for FlightPackage
router.register(r'flight/package/list', FlightPackageReadViewSet, basename='r_package')
router.register(r'flight/packages', NotAdminFlightPackageAdditionalViewSet, basename='not_admin_package')
router.register(r'flight/package', FlightPackageCreateUpdateViewSet, basename='cu_package')
router.register(r'flight/package/archive', FlightPackageArchiveRestoreListDetailViewSet, basename='arld_package')

# for BookingApplication
router.register(r'flight/booking-application', BookingApplicationCreateViewSet, basename='c_booking')
router.register(r'flight/booking-applications', AdminBookingApplicationAdditionalViewSet, basename='admin_booking')
router.register(r'flight/booking-application/list', BookingApplicationListRetrieveViewSet,
                basename='lru_booking')
router.register(r'flight/booking-application/update', BookingApplicationUpdateViewSet, basename='u_booking')
router.register(r'flight/booking-application/archive', BookingApplicationArchiveRestoreListDetailViewSet,
                basename='arld_booking')

# for ContactMessage
router.register(r'flight/contact-message', ContactMessageCreateViewSet, basename='c_message')
router.register(r'flight/contact-messages', AdminContactMessageAdditionalViewSet, basename='admin_message')
router.register(r'flight/contact-message/check', ContactMessageListRetrieveViewSet,
                basename='lru_message')
router.register(r'flight/contact-message/update', ContactMessageUpdateViewSet, basename='u_message')
router.register(r'flight/contact-message/archive', ContactMessageArchiveRestoreListDetailViewSet,
                basename='arld_message')

urlpatterns = [
                  path('admin/register', AdminRegisterView.as_view(), name='admin_register'),
                  path('admin/login/', AdminLoginView.as_view(), name='admin_login'),
                  path('', include(router.urls)),

              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
