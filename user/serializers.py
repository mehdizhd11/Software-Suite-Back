from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for a User model (read operations).
    """
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    
    class Meta:
        model = User
        fields = (
            'id', 'username', 'email', 'first_name', 'last_name', 'full_name',
            'role', 'phone_number', 'bio', 'avatar', 'is_active', 'is_staff',
            'is_email_verified', 'date_joined', 'updated_at', 'last_login', 'last_activity'
        )
        read_only_fields = ('id', 'is_staff', 'date_joined', 'updated_at', 'last_login', 'last_activity')


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.
    """
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True, label='Confirm Password')

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password2', 'first_name', 'last_name', 'role', 'phone_number', 'bio')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        
        # Convert empty string to None for optional fields
        email = validated_data.get('email') or None
        phone_number = validated_data.get('phone_number') or None
        bio = validated_data.get('bio') or None
        
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            email=email,
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            role=validated_data.get('role', 'software_engineer'),
            phone_number=phone_number,
            bio=bio,
        )
        return user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom token serializer that includes user data in the response.
    """
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Add custom claims
        token['username'] = user.username
        token['role'] = user.role
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        # Add user data to response
        data['user'] = UserSerializer(self.user).data
        return data
