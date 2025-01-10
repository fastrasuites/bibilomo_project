from django.contrib.auth.models import User
from rest_framework import serializers
from .models import FlightPackage, BookingApplication, ContactMessage


class FlightPackageSerializer(serializers.ModelSerializer):

    class Meta:
        model = FlightPackage
        fields = ['id', 'name', 'destination', 'placeholder_image', 'flight_mode', 'flight_class', 'origin', 'price',
                  'airline', 'departure_date', 'return_date']
        read_only_fields = ['date_created', 'date_updated', 'is_hidden']

def validate_return_date(self, return_date):
    if 'departure_date' in self.initial_data:
        departure_date = self.initial_data['departure_date']
        if return_date <= departure_date:
            raise serializers.ValidationError("Return date must be later than departure date.")
    return return_date

class BookingApplicationSerializer(serializers.ModelSerializer):
    package = serializers.PrimaryKeyRelatedField(queryset=FlightPackage.objects.filter(is_hidden=False))

    class Meta:
        model = BookingApplication
        fields = ['id', 'package', 'first_name', 'last_name', 'email', 'number_of_passengers', 'phone_number', 'date_of_birth',
                  'gender', 'nationality',]
        read_only_fields = ['date_booked', 'is_hidden']


class ContactMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactMessage
        fields = ['id', 'full_name', 'email', 'message']
        read_only_fields = ['date_sent', 'is_hidden']


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
