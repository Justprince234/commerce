from rest_framework import serializers
from accounts.models import User, Contact
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate

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
        fields = ('id', 'email','first_name', 'middle_name', 'surname', 'phone', 'sex', 'password', 'password2')
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
        user.middle_name = validated_data['middle_name']
        user.surname = validated_data['surname']
        user.phone = validated_data['phone']
        user.sex = validated_data['sex']
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
        fields = ('id', 'first_name', 'middle_name', 'surname', 'email', 'phone')


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = '__all__'
