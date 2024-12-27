from django.contrib.auth.models import User
from rest_framework import serializers
from .models import FlightPackage, BookingApplication, ContactMessage


class FlightPackageSerializer(serializers.ModelSerializer):

    class Meta:
        model = FlightPackage
        fields = ['id', 'name', 'destination', 'placeholder_image', 'flight_mode', 'flight_class', 'origin', 'price',
                  'airline', 'departure_date', 'return_date', 'is_hidden']
        read_only_fields = ['date_created', 'date_updated']

    def validate_return_date(self, value):
        if value < self.context['view'].request.GET.get('departure_date'):
            raise serializers.ValidationError('Return date cannot be earlier than departure date.')
        return value

class BookingApplicationSerializer(serializers.ModelSerializer):
    package = serializers.PrimaryKeyRelatedField(queryset=FlightPackage.objects.all())

    class Meta:
        model = BookingApplication
        fields = ['id', 'package', 'full_name', 'email', 'number_of_passengers', 'phone_number', 'date_of_birth',
                  'gender', 'nationality', 'is_hidden']
        read_only_fields = ['date_booked']


class ContactMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactMessage
        fields = ['id', 'full_name', 'email', 'message', 'is_hidden']
        read_only_fields = ['date_sent']


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'password', 'email', 'first_name', 'last_name']

    def create(self, validated_data):
        user = User.objects.create_superuser(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        return user


class AdminLoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ['username', 'password']
