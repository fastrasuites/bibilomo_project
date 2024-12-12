from django.urls import path
from .views import AdminLoginView, AdminRegisterView, FlightPackageView

urlpatterns = [
    path('admin/register', AdminRegisterView.as_view(), name='admin_register'),
    path('admin/login/', AdminLoginView.as_view(), name='admin_login'),
    path('flight/packages/', FlightPackageView.as_view(), name='list_create_packages'),
    path('flight/package/<int:pk>/', FlightPackageView.as_view(), name='retrieve_update_delete_package'),
]
