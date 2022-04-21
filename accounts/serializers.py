from rest_framework import serializers
from accounts.models import User
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed

from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_str, force_str, smart_bytes, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from rest_framework.fields import CurrentUserDefault

# Register Serializer
class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    password = serializers.CharField(write_only=True, max_length=35, min_length=6, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, max_length=35, min_length=6, required=True)
    
    class Meta:
        model = User
        fields = ('id', 'email','first_name', 'surname', 'password', 'password2')
        extra_kwargs = {
            'email': {'required': True},
            }
    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match!."})

        return attrs

    def create(self, validated_data):
        user = User.objects.create_user(
            validated_data['email'],
            )
        user.first_name = validated_data['first_name']
        user.surname = validated_data['surname']
        user.set_password(validated_data['password'])
        user.save()

        return user

class EmailVerificationSerializer(serializers.ModelSerializer):
    token = serializers.CharField(max_length=555)

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, data):
        user = authenticate(**data)
        if user and user.is_active:
            return user
        raise serializers.ValidationError("Incorrect Credentials")

# User Serializer
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id','first_name',  'surname', 'email')