from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from .models import CustomUser

class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer para registro de usuarios con validaciones
    """
    password = serializers.CharField(
        write_only=True, 
        min_length=8,
        style={'input_type': 'password'},
        help_text='La contraseña debe tener al menos 8 caracteres'
    )
    password_confirm = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'},
        help_text='Confirma tu contraseña'
    )

    class Meta:
        model = CustomUser
        fields = (
            'id', 'username', 'email', 'first_name', 'last_name',
            'phone_number', 'date_of_birth', 'risk_profile', 'password', 'password_confirm'
        )
        extra_kwargs = {
            'email': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
            'risk_profile': {'required': True},
        }

    def validate_email(self, value):
        """Validar que el email sea único"""
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("Este correo electrónico ya está registrado.")
        return value

    def validate_username(self, value):
        """Validar que el username sea único"""
        if CustomUser.objects.filter(username=value).exists():
            raise serializers.ValidationError("Este nombre de usuario ya está en uso.")
        return value

    def validate_password(self, value):
        """Validar la fortaleza de la contraseña"""
        try:
            validate_password(value)
        except ValidationError as e:
            raise serializers.ValidationError(e.messages)
        return value

    def validate(self, attrs):
        """Validar que las contraseñas coincidan"""
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({
                'password_confirm': 'Las contraseñas no coinciden.'
            })
        return attrs

    def create(self, validated_data):
        """Crear usuario con contraseña encriptada"""
        validated_data.pop('password_confirm')
        user = CustomUser.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            phone_number=validated_data.get('phone_number', ''),
            date_of_birth=validated_data.get('date_of_birth', None),
            risk_profile=validated_data['risk_profile'],
        )
        return user

class LoginSerializer(serializers.Serializer):
    """
    Serializer para inicio de sesión
    """
    email = serializers.EmailField(required=True)
    password = serializers.CharField(
        required=True,
        style={'input_type': 'password'},
        trim_whitespace=False
    )

    def validate(self, attrs):
        """Validar credenciales de usuario"""
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            # Intentar autenticar con email
            user = authenticate(
                request=self.context.get('request'),
                username=email,  # Django usará email como username
                password=password
            )

            if not user:
                # Verificar si el usuario existe
                try:
                    user_exists = CustomUser.objects.get(email=email)
                    if not user_exists.is_active:
                        raise serializers.ValidationError(
                            'La cuenta de usuario está deshabilitada.'
                        )
                    else:
                        raise serializers.ValidationError(
                            'Credenciales incorrectas.'
                        )
                except CustomUser.DoesNotExist:
                    raise serializers.ValidationError(
                        'No existe una cuenta con este correo electrónico.'
                    )

            if not user.is_active:
                raise serializers.ValidationError(
                    'La cuenta de usuario está deshabilitada.'
                )

            attrs['user'] = user
            return attrs
        else:
            raise serializers.ValidationError(
                'Debe proporcionar email y contraseña.'
            )

class UserSerializer(serializers.ModelSerializer):
    """
    Serializer para mostrar información del usuario
    """
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    risk_profile_info = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = (
            'id', 'username', 'email', 'first_name', 'last_name', 'full_name',
            'phone_number', 'date_of_birth', 'profile_picture', 'is_verified',
            'risk_profile', 'risk_profile_info', 'is_active', 'date_joined', 
            'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'date_joined', 'created_at', 'updated_at')
    
    def get_risk_profile_info(self, obj):
        """Obtener información detallada del perfil de riesgo"""
        return obj.get_risk_profile_display_info()

class UserUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer para actualizar información del usuario
    """
    class Meta:
        model = CustomUser
        fields = (
            'first_name', 'last_name', 'phone_number', 
            'date_of_birth', 'profile_picture', 'risk_profile'
        )

class PasswordChangeSerializer(serializers.Serializer):
    """
    Serializer para cambio de contraseña
    """
    old_password = serializers.CharField(required=True, style={'input_type': 'password'})
    new_password = serializers.CharField(required=True, min_length=8, style={'input_type': 'password'})
    new_password_confirm = serializers.CharField(required=True, style={'input_type': 'password'})

    def validate_new_password(self, value):
        """Validar la nueva contraseña"""
        try:
            validate_password(value)
        except ValidationError as e:
            raise serializers.ValidationError(e.messages)
        return value

    def validate(self, attrs):
        """Validar que las nuevas contraseñas coincidan"""
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({
                'new_password_confirm': 'Las contraseñas no coinciden.'
            })
        return attrs

    def validate_old_password(self, value):
        """Validar la contraseña actual"""
        if not self.context['request'].user.check_password(value):
            raise serializers.ValidationError('La contraseña actual es incorrecta.')
        return value
