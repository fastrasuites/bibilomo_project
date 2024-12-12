from django.urls import path
from .views import AdminLoginView, AdminRegisterView, FlightPackageView, FlightPackageCreateUpdateDeleteView

urlpatterns = [
    path('admin/register', AdminRegisterView.as_view(), name='admin_register'),
    path('admin/login/', AdminLoginView.as_view(), name='admin_login'),
    path('flight/package/', FlightPackageCreateUpdateDeleteView.as_view(), name='create_package'),
    path('flight/package/<int:pk>/update/', FlightPackageCreateUpdateDeleteView.as_view(), name='update_package'),
    path('flight/package/<int:pk>/delete/', FlightPackageCreateUpdateDeleteView.as_view(), name='delete_package'),
    path('flight/packages/', FlightPackageView.as_view(), name='list_packages'),
    path('flight/package/<int:pk>/', FlightPackageView.as_view(), name='retrieve_package'),
]
