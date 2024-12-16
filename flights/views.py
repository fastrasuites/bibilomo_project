import datetime

from django.utils import timezone
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

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


class FlightPackageCreateUpdateDeleteView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = FlightPackageSerializer

    def post(self, request):
        serializer = FlightPackageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        try:
            package = FlightPackage.objects.get(pk=pk)
        except FlightPackage.DoesNotExist:
            return Response({'error': 'Flight package not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = FlightPackageSerializer(package, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            package = FlightPackage.objects.get(pk=pk)
            package.delete()
            return Response({'message': f'Flight package with id {pk} successfully deleted'}, status=status.HTTP_200_OK)
        except FlightPackage.DoesNotExist:
            return Response({'error': 'Flight package not found'}, status=status.HTTP_404_NOT_FOUND)


class FlightPackageRetrieveView(APIView):
    serializer_class = FlightPackageSerializer

    def get(self, request, pk=None):
        if pk:
            try:
                package = FlightPackage.objects.get(pk=pk)
                serializer = FlightPackageSerializer(package)
                return Response(serializer.data)
            except FlightPackage.DoesNotExist:
                return Response({'error': 'Flight package not found'}, status=status.HTTP_404_NOT_FOUND)
        else:
            packages = FlightPackage.objects.all()
            serializer = FlightPackageSerializer(packages, many=True)
            return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def count(self, request):
        # Get the total count of flight packages and the count of recent flight packages
        total_count = FlightPackage.objects.all().count()
        one_week_ago = timezone.now() - datetime.timedelta(days=7)
        recent_count = FlightPackage.objects.filter(date_created__gte=one_week_ago).count()
        return Response({'total_count': total_count, 'recent_count': recent_count})

    @staticmethod
    @action(detail=False, methods=['get'])
    def search(request):
        # Search for flight packages by different fields
        filters = {
            'destination__icontains': request.query_params.get('destination'),
            'origin__icontains': request.query_params.get('origin'),
            'flight_mode__icontains': request.query_params.get('flight_mode'),
            'flight_class__icontains': request.query_params.get('flight_class'),
            'airline__icontains': request.query_params.get('airline'),
            'departure_date': request.query_params.get('departure_date'),
            'return_date': request.query_params.get('return_date')
        }
        filters = {k: v for k, v in filters.items() if v is not None}
        if filters:
            packages = FlightPackage.objects.filter(**filters)
            serializer = FlightPackageSerializer(packages, many=True)
            return Response(serializer.data)
        return Response({'error': 'A query parameter is required'}, status=status.HTTP_400_BAD_REQUEST)

class BookingApplicationCreateView(APIView):
    serializer_class = BookingApplicationSerializer

    def post(self, request):
        serializer = BookingApplicationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BookingApplicationRetrieveUpdateDeleteView(APIView):
    serializer_class = BookingApplicationSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None):
        if pk:
            try:
                booking = BookingApplication.objects.get(pk=pk)
                serializer = BookingApplicationSerializer(booking)
                return Response(serializer.data)
            except BookingApplication.DoesNotExist:
                return Response({'error': 'Booking application not found'}, status=status.HTTP_404_NOT_FOUND)
        else:
            bookings = BookingApplication.objects.all()
            serializer = BookingApplicationSerializer(bookings, many=True)
            return Response(serializer.data)

    def put(self, request, pk):
        try:
            booking = BookingApplication.objects.get(pk=pk)
        except BookingApplication.DoesNotExist:
            return Response({'error': 'Booking application not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = BookingApplicationSerializer(booking, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            booking = BookingApplication.objects.get(pk=pk)
            booking.delete()
            return Response({'message': f'Booking application with id {pk} successfully deleted'},
                            status=status.HTTP_200_OK)
        except BookingApplication.DoesNotExist:
            return Response({'error': 'Booking application not found'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['get'])
    def count(self, request):
        # Get the total count of booking applications and the count of recent booking applications
        total_count = BookingApplication.objects.all().count()
        one_week_ago = timezone.now() - datetime.timedelta(days=7)
        recent_count = BookingApplication.objects.filter(date_booked__gte=one_week_ago).count()
        return Response({'total_count': total_count, 'recent_count': recent_count})


class ContactMessageCreateView(APIView):
    serializer_class = ContactMessageSerializer

    def post(self, request):
        serializer = ContactMessageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ContactMessageRetrieveUpdateDeleteView(APIView):
    serializer_class = ContactMessageSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None):
        if pk:
            try:
                message = ContactMessage.objects.get(pk=pk)
                serializer = ContactMessageSerializer(message)
                return Response(serializer.data)
            except ContactMessage.DoesNotExist:
                return Response({'error': 'Contact message not found'}, status=status.HTTP_404_NOT_FOUND)
        else:
            messages = ContactMessage.objects.all()
            serializer = ContactMessageSerializer(messages, many=True)
            return Response(serializer.data)

    def put(self, request, pk):
        try:
            message = ContactMessage.objects.get(pk=pk)
        except ContactMessage.DoesNotExist:
            return Response({'error': 'Contact message not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = ContactMessageSerializer(message, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            message = ContactMessage.objects.get(pk=pk)
            message.delete()
            return Response({'message': f'Contact message with id {pk} successfully deleted'},
                            status=status.HTTP_200_OK)
        except ContactMessage.DoesNotExist:
            return Response({'error': 'Contact message not found'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['get'])
    def count(self, request):
        # Get the total count of contact messages and the count of recent contact messages
        total_count = ContactMessage.objects.all().count()
        one_week_ago = timezone.now() - datetime.timedelta(days=7)
        recent_count = ContactMessage.objects.filter(date_sent__gte=one_week_ago).count()
        return Response({'total_count': total_count, 'recent_count': recent_count})
