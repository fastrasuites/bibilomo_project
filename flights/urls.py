from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import AdminLoginView, AdminRegisterView, FlightPackageRetrieveViewSet, \
    FlightPackageCreateUpdateDeleteViewSet, BookingApplicationCreateViewSet, \
    BookingApplicationRetrieveUpdateDeleteViewSet, ContactMessageCreateViewSet, \
    ContactMessageRetrieveUpdateDeleteViewSet

router = DefaultRouter()
router.register(r'flight/packages', FlightPackageRetrieveViewSet, basename='r_package')
router.register(r'flight/packages', FlightPackageCreateUpdateDeleteViewSet, basename='cud_package')
router.register(r'flight/booking-applications', BookingApplicationRetrieveUpdateDeleteViewSet, basename='rud_booking')
router.register(r'flight/booking-application', BookingApplicationCreateViewSet, basename='c_booking')
router.register(r'flight/contact-messages', ContactMessageRetrieveUpdateDeleteViewSet, basename='rud_message')
router.register(r'flight/contact-message', ContactMessageCreateViewSet, basename='c_message')

urlpatterns = [
    path('admin/register', AdminRegisterView.as_view(), name='admin_register'),
    path('admin/login/', AdminLoginView.as_view(), name='admin_login'),
    path('', include(router.urls)),

    # # for flight packages
    # path('flight/package/', FlightPackageCreateUpdateDeleteView.as_view(), name='create_package'),
    # path('flight/packages/', FlightPackageRetrieveView.as_view(), name='list_packages'),
    # path('flight/packages/count/', FlightPackageRetrieveView.as_view(), name='count_packages'),
    # path('flight/packages/search/', FlightPackageRetrieveView.as_view({'get': 'search'}), name='search_packages'),
    # path('flight/package/<int:pk>/', FlightPackageRetrieveView.as_view(), name='retrieve_package'),
    # path('flight/package/<int:pk>/update/', FlightPackageCreateUpdateDeleteView.as_view(), name='update_package'),
    # path('flight/package/<int:pk>/delete/', FlightPackageCreateUpdateDeleteView.as_view(), name='delete_package'),
    #
    # # for booking applications
    # path('flight/booking-application/', BookingApplicationCreateView.as_view(), name='create_booking'),
    # path('flight/booking-applications/', BookingApplicationRetrieveUpdateDeleteView.as_view(), name='list_bookings'),
    # path('flight/booking-applications/count/', BookingApplicationRetrieveUpdateDeleteView.as_view({'get': 'count'}),
    #      name='count_bookings'),
    # path('flight/booking-application/<int:pk>/', BookingApplicationRetrieveUpdateDeleteView.as_view(),
    #      name='retrieve_booking'),
    # path('flight/booking-application/<int:pk>/update/', BookingApplicationRetrieveUpdateDeleteView.as_view(),
    #      name='update_booking'),
    # path('flight/booking-application/<int:pk>/delete/', BookingApplicationRetrieveUpdateDeleteView.as_view(),
    #      name='delete_booking'),
    #
    # # for contact messages
    # path('flight/contact-message/', ContactMessageCreateView.as_view(), name='create_message'),
    # path('flight/contact-messages/', ContactMessageRetrieveUpdateDeleteView.as_view(), name='list_messages'),
    # path('flight/contact-messages/count/', FlightPackageRetrieveView.as_view({'get': 'search'}), name='search_package'),
    # path('flight/contact-message/<int:pk>/', ContactMessageRetrieveUpdateDeleteView.as_view(), name='retrieve_message'),
    # path('flight/contact-message/<int:pk>/update/', ContactMessageRetrieveUpdateDeleteView.as_view(),
    #      name='update_message'),
    # path('flight/contact-message/<int:pk>/delete/', ContactMessageRetrieveUpdateDeleteView.as_view(),
    #      name='delete_message'),

]
