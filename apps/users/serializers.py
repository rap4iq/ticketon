from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from .models import CustomUser

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'password', 'password_confirm', 'role', 'phone']

        extra_kwargs = {
            'email': {'required': True},
        }

    def validate(self, attrs):
        """Проверка совпадения паролей"""
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password": "Passwords don't match"})
        return attrs

    def validate_email(self, value):
        """Проверка уникальности email"""
        if CustomUser.objects.filter(email=value.lower()).exists():
            raise serializers.ValidationError("User with this email already exists")
        return value.lower()

    def create(self, validated_data):
        """Создание пользователя"""
        validated_data.pop('password_confirm')
        
        user = CustomUser.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            role=validated_data.get('role', CustomUser.Role.CLIENT),
            phone=validated_data.get('phone', '')
        )
        return user

class UserLoginSerializer(serializers.Serializer):
    """Сериализатор для входа пользователя"""
    email = serializers.EmailField(required=True)
    password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )

    def validate(self, attrs):
        """Проверка credentials"""
        email = attrs.get('email', '').lower()
        password = attrs.get('password', '')

        if not email or not password:
            raise serializers.ValidationError("Email and password are required")

        # Найти пользователя по email
        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError("Invalid credentials")

        # Проверить пароль
        if not user.check_password(password):
            raise serializers.ValidationError("Invalid credentials")

        if not user.is_active:
            raise serializers.ValidationError("User account is disabled")

        attrs['user'] = user
        return attrs


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения информации о пользователе"""
    
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'role', 'phone', 'email_verified', 'created_at']
        read_only_fields = ['id', 'email_verified', 'created_at']


class UserUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор для обновления профиля"""
    
    class Meta:
        model = CustomUser
        fields = ['username', 'phone']

    def validate_username(self, value):
        """Проверка уникальности username (кроме текущего пользователя)"""
        user = self.context['request'].user
        if CustomUser.objects.exclude(pk=user.pk).filter(username=value).exists():
            raise serializers.ValidationError("This username is already taken")
        return value


class ChangePasswordSerializer(serializers.Serializer):
    """Сериализатор для смены пароля"""
    old_password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )
    new_password = serializers.CharField(
        required=True,
        write_only=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    new_password_confirm = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )

    def validate(self, attrs):
        """Проверка совпадения новых паролей"""
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({"new_password": "New passwords don't match"})
        return attrs

    def validate_old_password(self, value):
        """Проверка старого пароля"""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect")
        return value