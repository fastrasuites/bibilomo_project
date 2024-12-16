from django.contrib.auth.models import User
from rest_framework import serializers
from .models import FlightPackage, BookingApplication, ContactMessage


class FlightPackageSerializer(serializers.ModelSerializer):
    count = serializers.SerializerMethodField(method_name='count')
    recent_count = serializers.SerializerMethodField(method_name='recent_count')

    class Meta:
        model = FlightPackage
        fields = ['id', 'name', 'destination', 'placeholder_image', 'flight_class', 'origin', 'price', 'airline', 'departure_date',
                  'return_date']
        read_only_fields = ['count', 'recent_count', 'date_created', 'date_updated']


class BookingApplicationSerializer(serializers.ModelSerializer):
    count = serializers.SerializerMethodField(method_name='count')
    recent_count = serializers.SerializerMethodField(method_name='recent_count')
    package = FlightPackageSerializer(many=True)

    class Meta:
        model = BookingApplication
        fields = ['id', 'package', 'full_name', 'email', 'number_of_passengers', 'phone_number', 'date_of_birth',
                  'gender', 'nationality']
        read_only_fields = ['count', 'recent_count', 'date_booked']


class ContactMessageSerializer(serializers.ModelSerializer):
    count = serializers.SerializerMethodField(method_name='count')
    recent_count = serializers.SerializerMethodField(method_name='recent_count')

    class Meta:
        model = ContactMessage
        fields = ['id', 'full_name', 'email', 'message']
        read_only_fields = ['count', 'recent_count']


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
