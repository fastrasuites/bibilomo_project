import datetime

from django.utils import timezone
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet, ReadOnlyModelViewSet
from rest_framework.response import Response
from rest_framework import status, mixins
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import extend_schema, OpenApiParameter

from django.contrib.auth import authenticate
from .models import FlightPackage, BookingApplication, ContactMessage
from .serializers import FlightPackageSerializer, UserSerializer, AdminLoginSerializer, BookingApplicationSerializer, \
    ContactMessageSerializer


class AdminRegisterView(APIView):
    serializer_class = UserSerializer

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Admin registered successfully'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AdminLoginView(APIView):
    serializer_class = AdminLoginSerializer

    def post(self, request):
        serializer = AdminLoginSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']
            user = authenticate(request, username=username, password=password, is_staff=True)
            if user is not None:
                refresh = RefreshToken.for_user(user)
                return Response({
                    "access_token": str(refresh.access_token),
                    "refresh_token": str(refresh),
                    "message": "Admin authenticated and logged in successfully"
                }, status=status.HTTP_200_OK)
            return Response({"detail": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ArchiveRestoreListDetailViewSet(mixins.DestroyModelMixin, GenericViewSet):

    def destroy(self, request, pk=None, *args, **kwargs):
        try:
            instance = self.queryset.get(pk=pk, is_hidden=False)
            instance.is_hidden = True
            instance.save()
            return Response({'message': 'Successfully Archived'}, status=status.HTTP_200_OK)
        except self.queryset.model.DoesNotExist:
            return Response({'error': 'Object not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @extend_schema(
        responses={'200': None},
        description="List all archived instances"
    )
    @action(detail=False, methods=['get'])
    def archived_list(self, request, *args, **kwargs):
        queryset = self.queryset.filter(is_hidden=True)
        try:
            if queryset:
                archived_count = queryset.count()
                serializer = self.serializer_class(queryset, many=True)
                return Response(
                    {'archived_count': archived_count, 'message': 'List of Successfully Retrieved Archived Models',
                     'data': serializer.data})
            return Response({'archived_count': 0, 'error': 'No archived models found'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @extend_schema(
        responses={'200': None},
        parameters=[
            OpenApiParameter(name='id', type=int, location='path', required=True, description="Retrieve by Id"),
        ],
        description="Retrieve a specific archived instance by ID."
    )
    @action(detail=True, methods=['get'])
    def archived_retrieve(self, request, pk=None, *args, **kwargs):
        queryset = self.queryset.filter(is_hidden=True)
        queryset = queryset.filter(pk=pk)
        try:
            if queryset:
                serializer = self.serializer_class(queryset.first())
                return Response({'message': 'Successfully Retrieved Archived Models', 'data': serializer.data})
            return Response({'error': 'Object not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @extend_schema(
        responses={'200': None},
        parameters=[
            OpenApiParameter(name='id', type=int, location='path', required=True, description="Restore by Id"),
        ],
        description="Restore a specific instance by ID."
    )
    @action(detail=True, methods=['patch'])
    def restore(self, request, pk=None, *args, **kwargs):
        try:
            instance = self.queryset.get(pk=pk, is_hidden=True)
            instance.is_hidden = False
            instance.save()
            return Response({'message': 'Successfully Restored'}, status=status.HTTP_200_OK)
        except self.queryset.model.DoesNotExist:
            return Response({'error': 'Object not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# for anonymous users
class FlightPackageReadViewSet(ReadOnlyModelViewSet):
    serializer_class = FlightPackageSerializer
    queryset = FlightPackage.objects.filter(is_hidden=False)
    permission_classes = [AllowAny]


class NotAdminFlightPackageAdditionalViewSet(GenericViewSet):
    serializer_class = FlightPackageSerializer
    queryset = FlightPackage.objects.filter(is_hidden=False)
    permission_classes = [AllowAny]

    @extend_schema(
        responses=FlightPackageSerializer(many=True),
        parameters=[
            OpenApiParameter(name='destination', type=str, required=False, description="Search by destination"),
            OpenApiParameter(name='origin', type=str, required=False, description="Search by origin"),
            OpenApiParameter(name='flight_mode', type=str, required=False, description="Search by flight mode"),
            OpenApiParameter(name='flight_class', type=str, required=False, description="Search by flight class"),
            OpenApiParameter(name='airline', type=str, required=False, description="Search by airline"),
            OpenApiParameter(name='departure_date', type=str, required=False,
                             description="Search by departure date"),
            OpenApiParameter(name='return_date', type=str, required=False, description="Search by return date"),
        ],
        description="Search for flight packages by various fields."
    )
    @action(detail=False, methods=['get'])
    def search(self, request, *args, **kwargs):
        filters = {
            'destination__icontains': request.query_params.get('destination'),
            'origin__icontains': request.query_params.get('origin'),
            'flight_mode__icontains': request.query_params.get('flight_mode'),
            'flight_class__icontains': request.query_params.get('flight_class'),
            'airline__icontains': request.query_params.get('airline'),
            'departure_date': request.query_params.get('departure_date'),
            'return_date': request.query_params.get('return_date'),
        }
        filters = {k: v for k, v in filters.items() if v}
        if filters:
            packages = self.queryset.filter(is_hidden=False).filter(**filters)
            serializer = self.serializer_class(packages, many=True)
            return Response(serializer.data)
        return Response({'error': 'A query parameter is required'}, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        responses={'200': None},
        description="Get the total count of active flight packages and the count of recent ones."
    )
    @action(detail=False, methods=['get'])
    def count(self, request):
        """Get the total count of flight packages and recent packages created in the last 7 days."""
        total_active_count = self.queryset.filter(is_hidden=False).count()
        one_week_ago = timezone.now() - datetime.timedelta(days=7)
        recent_count = self.queryset.filter(date_created__gte=one_week_ago).count()
        return Response(
            {'total_active_count': total_active_count, 'recent_count': recent_count})


# for admin users
class FlightPackageCreateUpdateViewSet(mixins.CreateModelMixin, mixins.UpdateModelMixin,
                                       GenericViewSet):
    serializer_class = FlightPackageSerializer
    queryset = FlightPackage.objects.all()
    permission_classes = [IsAuthenticated]


class FlightPackageArchiveRestoreListDetailViewSet(ArchiveRestoreListDetailViewSet):
    queryset = FlightPackage.objects.all()
    serializer_class = FlightPackageSerializer
    permission_classes = [IsAuthenticated]


class BookingApplicationCreateViewSet(mixins.CreateModelMixin, GenericViewSet):
    queryset = BookingApplication.objects.all()
    serializer_class = BookingApplicationSerializer
    permission_classes = [AllowAny]


class AdminBookingApplicationAdditionalViewSet(GenericViewSet):
    serializer_class = BookingApplicationSerializer
    queryset = BookingApplication.objects.filter(is_hidden=False)
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={'200': None},
        description="Get the total count of active flight packages and the count of recent ones."
    )
    @action(detail=False, methods=['get'])
    def count(self, request):
        """Get the total count of flight packages and recent packages created in the last 7 days."""
        total_active_count = self.queryset.filter(is_hidden=False).count()
        one_week_ago = timezone.now() - datetime.timedelta(days=7)
        recent_count = self.queryset.filter(date_created__gte=one_week_ago).count()
        return Response(
            {'total_active_count': total_active_count, 'recent_count': recent_count})


class BookingApplicationListRetrieveViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin,
                                            GenericViewSet):
    serializer_class = BookingApplicationSerializer
    queryset = BookingApplication.objects.filter(is_hidden=False)
    permission_classes = [IsAuthenticated]


class BookingApplicationUpdateViewSet(mixins.UpdateModelMixin, GenericViewSet):
    serializer_class = BookingApplicationSerializer
    queryset = BookingApplication.objects.filter(is_hidden=False)
    permission_classes = [IsAuthenticated]


class BookingApplicationArchiveRestoreListDetailViewSet(ArchiveRestoreListDetailViewSet):
    queryset = BookingApplication.objects.all()
    serializer_class = BookingApplicationSerializer
    permission_classes = [IsAuthenticated]


class ContactMessageCreateViewSet(mixins.CreateModelMixin, GenericViewSet):
    queryset = ContactMessage.objects.all()
    serializer_class = ContactMessageSerializer
    permission_classes = [AllowAny]


class AdminContactMessageAdditionalViewSet(GenericViewSet):
    serializer_class = ContactMessageSerializer
    queryset = ContactMessage.objects.filter(is_hidden=False)
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={'200': None},
        description="Get the total count of active flight packages and the count of recent ones."
    )
    @action(detail=False, methods=['get'])
    def count(self, request):
        """Get the total count of flight packages and recent packages created in the last 7 days."""
        total_active_count = self.queryset.filter(is_hidden=False).count()
        one_week_ago = timezone.now() - datetime.timedelta(days=7)
        recent_count = self.queryset.filter(date_created__gte=one_week_ago).count()
        return Response(
            {'total_active_count': total_active_count, 'recent_count': recent_count})


class ContactMessageListRetrieveViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin,
                                        GenericViewSet):
    serializer_class = ContactMessageSerializer
    queryset = ContactMessage.objects.filter(is_hidden=False)
    permission_classes = [IsAuthenticated]


class ContactMessageUpdateViewSet(mixins.UpdateModelMixin, GenericViewSet):
    serializer_class = ContactMessageSerializer
    queryset = ContactMessage.objects.filter(is_hidden=False)
    permission_classes = [IsAuthenticated]


class ContactMessageArchiveRestoreListDetailViewSet(ArchiveRestoreListDetailViewSet):
    queryset = ContactMessage.objects.all()
    serializer_class = ContactMessageSerializer
    permission_classes = [IsAuthenticated]
