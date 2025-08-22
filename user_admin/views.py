from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import get_object_or_404
from django.core.cache import cache
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import redis
import json
from datetime import datetime, timedelta
from .models import CustomUser
from .serializers import (
    UserRegistrationSerializer, 
    UserSerializer, 
    UserUpdateSerializer,
    PasswordChangeSerializer,
    LoginSerializer
)

# Configuración de Redis para sesiones
try:
    redis_client = redis.Redis(
        host=getattr(settings, 'REDIS_HOST', 'localhost'),
        port=getattr(settings, 'REDIS_PORT', 6379),
        db=getattr(settings, 'REDIS_DB', 0),
        decode_responses=True
    )
    # Probar la conexión
    redis_client.ping()
    print(" Redis conectado correctamente")
except Exception as e:
    print(f" Redis no disponible: {e}")
    redis_client = None

def cache_user_session(user, token):
    """
    Guarda la sesión del usuario en Redis
    """
    if redis_client:
        session_data = {
            'user_id': user.id,
            'email': user.email,
            'full_name': user.get_full_name(),
            'risk_profile': user.risk_profile,
            'login_time': datetime.now().isoformat(),
            'token': str(token)
        }
        
        # Guardar en Redis con expiración de 24 horas (usando el prefijo correcto)
        redis_client.setex(
            f"starkadvisor_local:user_session_{user.id}",
            86400,  # 24 horas en segundos
            json.dumps(session_data)
        )
        print(f" Sesión guardada en Redis para usuario {user.id}")

def get_user_session(user_id):
    """
    Obtiene la sesión del usuario desde Redis
    """
    if redis_client:
        session_data = redis_client.get(f"starkadvisor_local:user_session_{user_id}")
        if session_data:
            return json.loads(session_data)
    return None

def clear_user_session(user_id):
    """
    Elimina la sesión del usuario de Redis
    """
    if redis_client:
        redis_client.delete(f"starkadvisor_local:user_session_{user_id}")
        print(f"Sesión eliminada de Redis para usuario {user_id}")
        redis_client.delete(f"user_session:{user_id}")

@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """
    Vista para inicio de sesión con Redis
    """
    serializer = LoginSerializer(data=request.data, context={'request': request})
    
    if serializer.is_valid():
        user = serializer.validated_data['user']
        
        # Crear o obtener token
        token, created = Token.objects.get_or_create(user=user)
        
        # Guardar sesión en Redis
        cache_user_session(user, token)
        
        # Login en Django
        login(request, user)
        
        return Response({
            'message': 'Inicio de sesión exitoso',
            'token': token.key,
            'user': UserSerializer(user).data,
            'session_cached': redis_client is not None
        }, status=status.HTTP_200_OK)
    
    return Response({
        'message': 'Credenciales incorrectas',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """
    Vista para cerrar sesión
    """
    user = request.user
    
    # Limpiar sesión de Redis
    clear_user_session(user.id)
    
    # Eliminar token
    try:
        request.user.auth_token.delete()
    except:
        pass
    
    # Logout de Django
    logout(request)
    
    return Response({
        'message': 'Sesión cerrada exitosamente'
    }, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def session_status(request):
    """
    Vista para verificar el estado de la sesión
    """
    user = request.user
    session_data = get_user_session(user.id)
    
    return Response({
        'authenticated': True,
        'user': UserSerializer(user).data,
        'session_data': session_data,
        'redis_available': redis_client is not None
    }, status=status.HTTP_200_OK)

@method_decorator(csrf_exempt, name='dispatch')
class UserRegistrationView(generics.CreateAPIView):
    """
    Vista para registro de nuevos usuarios
    """
    queryset = CustomUser.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                'message': 'Usuario registrado exitosamente',
                'user': UserSerializer(user).data
            }, status=status.HTTP_201_CREATED)
        return Response({
            'message': 'Error en el registro',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

class UserListView(generics.ListAPIView):
    """
    Vista para listar todos los usuarios (solo para administradores)
    """
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Solo superusuarios pueden ver todos los usuarios
        if self.request.user.is_superuser:
            return CustomUser.objects.all()
        # Usuarios normales solo ven su propio perfil
        return CustomUser.objects.filter(id=self.request.user.id)

class UserDetailView(generics.RetrieveAPIView):
    """
    Vista para obtener detalles de un usuario específico
    """
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        # Solo el propio usuario o superusuario puede ver los detalles
        pk = self.kwargs.get('pk')
        user = get_object_or_404(CustomUser, pk=pk)
        
        if self.request.user == user or self.request.user.is_superuser:
            return user
        else:
            self.permission_denied(self.request)

class UserUpdateView(generics.UpdateAPIView):
    """
    Vista para actualizar información del usuario
    """
    queryset = CustomUser.objects.all()
    serializer_class = UserUpdateSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        # Solo el propio usuario puede actualizar su informacion
        pk = self.kwargs.get('pk')
        user = get_object_or_404(CustomUser, pk=pk)
        
        if self.request.user == user or self.request.user.is_superuser:
            return user
        else:
            self.permission_denied(self.request)

class UserDeleteView(generics.DestroyAPIView):
    """
    Vista para eliminar un usuario (solo superusuarios)
    """
    queryset = CustomUser.objects.all()
    permission_classes = [IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return Response(
                {'message': 'No tienes permisos para eliminar usuarios'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        user = self.get_object()
        user.delete()
        return Response(
            {'message': 'Usuario eliminado exitosamente'},
            status=status.HTTP_204_NO_CONTENT
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    """
    Vista para cambiar la contraseña del usuario
    """
    serializer = PasswordChangeSerializer(data=request.data, context={'request': request})
    
    if serializer.is_valid():
        user = request.user
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        
        return Response({
            'message': 'Contraseña cambiada exitosamente'
        }, status=status.HTTP_200_OK)
    
    return Response({
        'message': 'Error al cambiar la contraseña',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile(request):
    """
    Vista para obtener el perfil del usuario actual
    """
    serializer = UserSerializer(request.user)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([AllowAny])
def validate_email(request):
    """
    Vista para validar si un email ya existe
    """
    email = request.data.get('email', '')
    exists = CustomUser.objects.filter(email=email).exists()
    
    return Response({
        'exists': exists,
        'message': 'Email ya registrado' if exists else 'Email disponible'
    })

@api_view(['POST'])
@permission_classes([AllowAny])
def validate_username(request):
    """
    Vista para validar si un username ya existe
    """
    username = request.data.get('username', '')
    exists = CustomUser.objects.filter(username=username).exists()
    
    return Response({
        'exists': exists,
        'message': 'Nombre de usuario ya existe' if exists else 'Nombre de usuario disponible'
    })

@api_view(['GET'])
@permission_classes([AllowAny])
def risk_profiles(request):
    """
    Vista para obtener todos los perfiles de riesgo disponibles
    """
    profiles = []
    for choice in CustomUser.RISK_PROFILE_CHOICES:
        # Crear un objeto temporal para obtener la información
        temp_user = CustomUser(risk_profile=choice[0])
        profile_info = temp_user.get_risk_profile_display_info()
        profiles.append({
            'value': choice[0],
            'label': choice[1],
            'info': profile_info
        })
    
    return Response({
        'risk_profiles': profiles,
        'message': 'Perfiles de riesgo obtenidos exitosamente'
    }, status=status.HTTP_200_OK)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_risk_profile(request):
    """
    Vista para actualizar solo el perfil de riesgo del usuario
    """
    user = request.user
    new_risk_profile = request.data.get('risk_profile')
    
    # Validar que el perfil de riesgo sea válido
    valid_profiles = [choice[0] for choice in CustomUser.RISK_PROFILE_CHOICES]
    if new_risk_profile not in valid_profiles:
        return Response({
            'message': 'Perfil de riesgo inválido',
            'valid_profiles': valid_profiles
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Actualizar el perfil de riesgo
    old_profile = user.risk_profile
    user.risk_profile = new_risk_profile
    user.save()
    
    # Actualizar sesión en Redis si existe
    session_data = get_user_session(user.id)
    if session_data:
        session_data['risk_profile'] = new_risk_profile
        redis_client.setex(
            f"user_session:{user.id}",
            86400,
            json.dumps(session_data)
        )
    
    return Response({
        'message': 'Perfil de riesgo actualizado exitosamente',
        'old_profile': old_profile,
        'new_profile': new_risk_profile,
        'user': UserSerializer(user).data
    }, status=status.HTTP_200_OK)
