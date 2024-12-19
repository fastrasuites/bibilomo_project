import datetime

from django.utils import timezone
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
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


class FlightPackageCreateViewSet(ViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = FlightPackageSerializer

    @extend_schema(
        request=FlightPackageSerializer,
        responses={201: FlightPackageSerializer},
        description="Create a new flight package."
    )
    def create(self, request):
        serializer = FlightPackageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class FlightPackageUpdateDeleteViewSet(ViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = FlightPackageSerializer

    @extend_schema(
        request=FlightPackageSerializer,
        responses={200: FlightPackageSerializer},
        parameters=[
            OpenApiParameter(name='id', type=int, location='path', required=True, description="Update by Id"),
        ],
        description="Update a specific flight package by ID."
    )
    def update(self, request, pk):
        try:
            package = FlightPackage.objects.get(pk=pk)
        except FlightPackage.DoesNotExist:
            return Response({'error': 'Flight package not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = FlightPackageSerializer(package, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        responses={'200': None},
        parameters=[
            OpenApiParameter(name='id', type=int, location='path', required=True, description="Destroy by Id"),
        ],
        description="Delete a specific flight package by ID."
    )
    def destroy(self, request, pk):
        try:
            package = FlightPackage.objects.get(pk=pk)
            package.delete()
            return Response({'message': f'Flight package with id {pk} successfully deleted'}, status=status.HTTP_200_OK)
        except FlightPackage.DoesNotExist:
            return Response({'error': 'Flight package not found'}, status=status.HTTP_404_NOT_FOUND)


class FlightPackageRetrieveViewSet(ViewSet):
    serializer_class = FlightPackageSerializer

    @extend_schema(
        responses=FlightPackageSerializer,
        parameters=[

            OpenApiParameter(name='id', type=int, required=True, location='path', description="Retrieve by Id"),
        ],
        description="Retrieve a specific flight package by ID.",
    )
    def retrieve(self, request, id: int):
        """Retrieve a single flight package by ID."""
        try:
            package = FlightPackage.objects.get(pk=id)
            serializer = FlightPackageSerializer(package)
            return Response(serializer.data)
        except FlightPackage.DoesNotExist:
            return Response({'error': 'Flight package not found'}, status=status.HTTP_404_NOT_FOUND)

    @extend_schema(
        responses=FlightPackageSerializer(many=True),
        description="List all flight packages.",
    )
    def list(self, request):
        """List all flight packages."""
        packages = FlightPackage.objects.all()
        serializer = FlightPackageSerializer(packages, many=True)
        return Response(serializer.data)

    @extend_schema(
        responses={'200': None},
        description="Get the total count of flight packages and the count of recent ones."
    )
    @action(detail=False, methods=['get'])
    def count(self, request):
        """Get the total count of flight packages and recent packages created in the last 7 days."""
        total_count = FlightPackage.objects.all().count()
        one_week_ago = timezone.now() - datetime.timedelta(days=7)
        recent_count = FlightPackage.objects.filter(date_created__gte=one_week_ago).count()
        return Response({'total_count': total_count, 'recent_count': recent_count})


    @extend_schema(
        responses=FlightPackageSerializer(many=True),
        parameters=[
            OpenApiParameter(name='destination', type=str, required=False, description="Search by destination"),
            OpenApiParameter(name='origin', type=str, required=False, description="Search by origin"),
            OpenApiParameter(name='flight_mode', type=str, required=False, description="Search by flight mode"),
            OpenApiParameter(name='flight_class', type=str, required=False, description="Search by flight class"),
            OpenApiParameter(name='airline', type=str, required=False, description="Search by airline"),
            OpenApiParameter(name='departure_date', type=str, required=False, description="Search by departure date"),
            OpenApiParameter(name='return_date', type=str, required=False, description="Search by return date"),
        ],
        description="Search for flight packages by various fields."
    )
    @action(detail=False, methods=['get'])
    def search(self, request):
        """Search for flight packages by various fields."""
        filters = {
            'destination__icontains': request.query_params.get('destination'),
            'origin__icontains': request.query_params.get('origin'),
            'flight_mode__icontains': request.query_params.get('flight_mode'),
            'flight_class__icontains': request.query_params.get('flight_class'),
            'airline__icontains': request.query_params.get('airline'),
            'departure_date': request.query_params.get('departure_date'),
            'return_date': request.query_params.get('return_date'),
        }
        filters = {k: v for k, v in filters.items() if v}  # Remove None values
        if filters:
            packages = FlightPackage.objects.filter(**filters)
            serializer = FlightPackageSerializer(packages, many=True)
            return Response(serializer.data)
        return Response({'error': 'A query parameter is required'}, status=status.HTTP_400_BAD_REQUEST)


class BookingApplicationCreateViewSet(ViewSet):
    serializer_class = BookingApplicationSerializer

    @extend_schema(
        request=BookingApplicationSerializer,
        responses={201: BookingApplicationSerializer},
        description="Create a new flight package."
    )
    def create(self, request):
        serializer = BookingApplicationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BookingApplicationRetrieveUpdateDeleteViewSet(ViewSet):
    serializer_class = BookingApplicationSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={200: BookingApplicationSerializer},
        parameters=[
            OpenApiParameter(name='id', type=int, location='path', required=True, description="Retrieve by Id"),
        ],
        description="Retrieve a specific booking application by ID."
    )
    def retrieve(self, request, pk=None):
        """ Retrieve a specific booking application by ID"""
        try:
            booking = BookingApplication.objects.get(pk=pk)
            serializer = BookingApplicationSerializer(booking)
            return Response(serializer.data)
        except BookingApplication.DoesNotExist:
            return Response({'error': 'Booking application not found'}, status=status.HTTP_404_NOT_FOUND)

    @extend_schema(
        responses=BookingApplicationSerializer(many=True),
        description="List all Booking Applications."
    )
    def list(self, request):
        """ List all Booking Applications"""
        bookings = BookingApplication.objects.all()
        serializer = BookingApplicationSerializer(bookings, many=True)
        return Response(serializer.data)

    @extend_schema(
        request=BookingApplicationSerializer,
        responses={200: ContactMessageSerializer},
        parameters=[
            OpenApiParameter(name='id', type=int, location='path', required=True, description="Update by Id"),
        ],
        description="Update a specific booking application by ID."
    )
    def update(self, request, pk):
        try:
            booking = BookingApplication.objects.get(pk=pk)
        except BookingApplication.DoesNotExist:
            return Response({'error': 'Booking application not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = BookingApplicationSerializer(booking, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        responses={'200': None},
        parameters=[
            OpenApiParameter(name='id', type=int, location='path', required=True, description="Destroy by Id"),
        ],
        description="Delete a specific booking application by ID."
    )
    def destroy(self, request, pk):
        try:
            booking = BookingApplication.objects.get(pk=pk)
            booking.delete()
            return Response({'message': f'Booking application with id {pk} successfully deleted'},
                            status=status.HTTP_200_OK)
        except BookingApplication.DoesNotExist:
            return Response({'error': 'Booking application not found'}, status=status.HTTP_404_NOT_FOUND)

    @extend_schema(
        responses={'200': None},
        description="Get the total count of booking applications and the count of recent booking applications."
    )
    @action(detail=False, methods=['get'])
    def count(self, request):
        # Get the total count of booking applications and the count of recent booking applications
        total_count = BookingApplication.objects.all().count()
        one_week_ago = timezone.now() - datetime.timedelta(days=7)
        recent_count = BookingApplication.objects.filter(date_booked__gte=one_week_ago).count()
        return Response({'total_count': total_count, 'recent_count': recent_count})


class ContactMessageCreateViewSet(ViewSet):
    serializer_class = ContactMessageSerializer

    @extend_schema(
        request=ContactMessageSerializer,
        responses={201: ContactMessageSerializer},
        description="Create a new contact message."
    )
    def create(self, request):
        serializer = ContactMessageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ContactMessageRetrieveUpdateDeleteViewSet(ViewSet):
    serializer_class = ContactMessageSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={200: ContactMessageSerializer},
        parameters=[
            OpenApiParameter(name='id', type=int, location='path', required=True, description="Retrieve by Id"),
        ],
        description="Retrieve a specific contact message by ID."
    )
    def retrieve(self, request, pk=None):
        try:
            message = ContactMessage.objects.get(pk=pk)
            serializer = ContactMessageSerializer(message)
            return Response(serializer.data)
        except ContactMessage.DoesNotExist:
            return Response({'error': 'Contact message not found'}, status=status.HTTP_404_NOT_FOUND)

    @extend_schema(
        responses=ContactMessageSerializer(many=True),
        description="List all contact messages."
    )
    def list(self, request):
        messages = ContactMessage.objects.all()
        serializer = ContactMessageSerializer(messages, many=True)
        return Response(serializer.data)

    @extend_schema(
        request=ContactMessageSerializer,
        responses={200: ContactMessageSerializer},
        parameters=[
            OpenApiParameter(name='id', type=int, location='path', required=True, description="Update by Id"),
        ],
        description="Update a specific contact message by ID."
    )
    def update(self, request, pk):
        try:
            message = ContactMessage.objects.get(pk=pk)
        except ContactMessage.DoesNotExist:
            return Response({'error': 'Contact message not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = ContactMessageSerializer(message, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        responses={'200': None},
        parameters=[
            OpenApiParameter(name='id', type=int, location='path', required=True, description="Destroy by Id"),
        ],
        description="Delete a specific contact message by ID."
    )
    def destroy(self, request, pk):
        try:
            message = ContactMessage.objects.get(pk=pk)
            message.delete()
            return Response({'message': f'Contact message with id {pk} successfully deleted'},
                            status=status.HTTP_200_OK)
        except ContactMessage.DoesNotExist:
            return Response({'error': 'Contact message not found'}, status=status.HTTP_404_NOT_FOUND)

    @extend_schema(
        responses={'200': None},
        description="Get the total count of contact messages and the count of recent contact messages."
    )
    @action(detail=False, methods=['get'])
    def count(self, request):
        # Get the total count of contact messages and the count of recent contact messages
        total_count = ContactMessage.objects.all().count()
        one_week_ago = timezone.now() - datetime.timedelta(days=7)
        recent_count = ContactMessage.objects.filter(date_sent__gte=one_week_ago).count()
        return Response({'total_count': total_count, 'recent_count': recent_count})
