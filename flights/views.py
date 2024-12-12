from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from django.contrib.auth import authenticate
from .models import FlightPackage
from .serializers import FlightPackageSerializer, UserSerializer, AdminLoginSerializer


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
            user = authenticate(request, username=username, password=password)
            if user is not None:
                refresh = RefreshToken.for_user(user)
                return Response({
                    "access_token": str(refresh.access_token),
                    "refresh_token": str(refresh),
                    "message": "Admin authenticated and logged in successfully"
                }, status=status.HTTP_200_OK)
            return Response({"detail": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class FlightPackageView(APIView):
    permission_classes = [IsAuthenticated]
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
