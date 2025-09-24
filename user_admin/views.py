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
from datetime import date, datetime, timedelta

# Helper function para serializar fechas
def serialize_for_json(obj):
    """Convierte objetos Python a formatos serializables en JSON"""
    if isinstance(obj, (date, datetime)):
        return obj.isoformat()
    elif isinstance(obj, type):
        # Si es un tipo de clase, convertir a string
        return str(obj)
    elif hasattr(obj, '__dict__'):
        # Si es un objeto complejo, convertir a string
        return str(obj)
    elif obj is None:
        return None
    else:
        # Para tipos básicos (str, int, float, bool)
        return obj, timedelta
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
        # Debug: imprimir datos recibidos
        print("=" * 50)
        print("REGISTRO - DATOS RECIBIDOS EN EL BACKEND:")
        print(f"request.data: {request.data}")
        print(f"Content-Type: {request.content_type}")
        print(f"Request method: {request.method}")
        print(f"Request headers: {dict(request.headers)}")
        print("=" * 50)
        
        try:
            serializer = self.get_serializer(data=request.data)
            print(f"Serializer created: {type(serializer)}")
            
            if serializer.is_valid():
                print("✅ Serializer is valid, creating user...")
                user = serializer.save()
                print(f"✅ User created successfully: {user.username}")
                
                return Response({
                    'message': 'Usuario registrado exitosamente',
                    'user': UserSerializer(user).data
                }, status=status.HTTP_201_CREATED)
            else:
                # Debug: imprimir errores de validación
                print("❌ ERRORES DE VALIDACIÓN EN REGISTRO:")
                print(f"serializer.errors: {serializer.errors}")
                print("=" * 50)
                
                return Response({
                    'message': 'Error en el registro',
                    'errors': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            print(f"❌ Exception in registration: {str(e)}")
            import traceback
            traceback.print_exc()
            
            return Response({
                'message': 'Error interno del servidor',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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
    http_method_names = ['put', 'patch']  # Permitir PUT y PATCH

    def get_object(self):
        # Solo el propio usuario puede actualizar su informacion
        pk = self.kwargs.get('pk')
        user = get_object_or_404(CustomUser, pk=pk)
        
        if self.request.user == user or self.request.user.is_superuser:
            return user
        else:
            self.permission_denied(self.request)
    
    def update(self, request, *args, **kwargs):
        import logging
        logger = logging.getLogger(__name__)
        
        # Print directo para asegurar que se ejecute
        print("=" * 50)
        print("UserUpdateView - EJECUTANDO UPDATE:")
        print(f"User ID in URL: {kwargs.get('pk')}")
        print(f"Request user: {request.user}")
        print(f"Request data: {request.data}")
        print(f"Content-Type: {request.content_type}")
        print(f"Request method: {request.method}")
        print("=" * 50)
        
        logger.debug("=" * 50)
        logger.debug("UserUpdateView - DEBUGGING:")
        logger.debug(f"User ID in URL: {kwargs.get('pk')}")
        logger.debug(f"Request user: {request.user}")
        logger.debug(f"Request data: {request.data}")
        logger.debug(f"Content-Type: {request.content_type}")
        logger.debug(f"Request method: {request.method}")
        logger.debug("=" * 50)
        
        partial = kwargs.pop('partial', True)  # Siempre permitir partial updates
        instance = self.get_object()
        
        try:
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            
            if serializer.is_valid():
                print("✅ Serializer is valid, updating...")
                logger.debug("Serializer is valid, updating...")
                self.perform_update(serializer)
                print("✅ User updated successfully in database")
                
                # Intentar actualizar sesión en Redis (no crítico si falla)
                try:
                    session_data = get_user_session(instance.id)
                    if session_data:
                        # Actualizar datos relevantes en la sesión
                        updated_fields = request.data.keys()
                        print(f"Campos a actualizar: {list(updated_fields)}")
                        
                        for field in updated_fields:
                            if hasattr(instance, field):
                                value = getattr(instance, field)
                                print(f"Campo: {field}, Valor: {value}, Tipo: {type(value)}")
                                
                                try:
                                    # Usar helper function para serializar fechas
                                    serialized_value = serialize_for_json(value)
                                    session_data[field] = serialized_value
                                    print(f"✅ Campo {field} serializado correctamente")
                                except Exception as field_error:
                                    print(f"❌ Error serializando campo {field}: {field_error}")
                                    # Si hay error, usar string representation
                                    session_data[field] = str(value)
                        
                        try:
                            redis_client.setex(
                                f"user_session:{instance.id}",
                                86400,
                                json.dumps(session_data)
                            )
                            print(f"✅ Session updated in Redis for user {instance.id}")
                            logger.debug(f"Session updated in Redis for user {instance.id}")
                        except Exception as redis_error:
                            print(f"❌ Error guardando en Redis: {redis_error}")
                            print(f"Datos de sesión problemáticos: {session_data}")
                            # Continue sin actualizar Redis en caso de error
                            pass
                except Exception as session_error:
                    print(f"❌ Error general con Redis session: {session_error}")
                    # Continue sin problemas, la actualización del usuario ya funcionó
                    pass
                
                # Devolver el usuario actualizado usando UserSerializer
                user_serializer = UserSerializer(instance)
                logger.debug("Update successful")
                return Response({
                    'message': 'Perfil actualizado exitosamente',
                    'user': user_serializer.data
                }, status=status.HTTP_200_OK)
            else:
                logger.error(f"Serializer validation errors: {serializer.errors}")
                return Response({
                    'message': 'Error de validación',
                    'errors': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            logger.error(f"Exception in UserUpdateView: {str(e)}")
            return Response({
                'message': 'Error interno del servidor',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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
@csrf_exempt
def update_risk_profile(request):
    """
    Vista para actualizar solo el perfil de riesgo del usuario
    """
    import logging
    logger = logging.getLogger(__name__)
    
    logger.debug(f"Update risk profile called")
    logger.debug(f"Request data: {request.data}")
    logger.debug(f"Request method: {request.method}")
    logger.debug(f"User: {request.user}")
    logger.debug(f"Content type: {request.content_type}")
    logger.debug(f"Request body: {request.body}")
    
    # Verificar si el usuario está autenticado
    if not request.user.is_authenticated:
        logger.error("User not authenticated")
        return Response({
            'message': 'Usuario no autenticado'
        }, status=status.HTTP_401_UNAUTHORIZED)
    
    user = request.user
    new_risk_profile = request.data.get('risk_profile')
    
    logger.debug(f"Current risk profile: {user.risk_profile}")
    logger.debug(f"New risk profile: {new_risk_profile}")
    
    # Validar que el perfil de riesgo sea válido
    valid_profiles = [choice[0] for choice in CustomUser.RISK_PROFILE_CHOICES]
    if new_risk_profile not in valid_profiles:
        logger.error(f"Invalid risk profile: {new_risk_profile}. Valid options: {valid_profiles}")
        return Response({
            'message': 'Perfil de riesgo inválido',
            'valid_profiles': valid_profiles,
            'received_profile': new_risk_profile
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Actualizar el perfil de riesgo
        old_profile = user.risk_profile
        user.risk_profile = new_risk_profile
        user.save()
        
        logger.debug(f"User profile updated successfully from {old_profile} to {new_risk_profile}")
        
        # Actualizar sesión en Redis si existe
        session_data = get_user_session(user.id)
        if session_data:
            session_data['risk_profile'] = new_risk_profile
            redis_client.setex(
                f"user_session:{user.id}",
                86400,
                json.dumps(session_data)
            )
            logger.debug(f"Redis session updated for user {user.id}")
        
        return Response({
            'message': 'Perfil de riesgo actualizado exitosamente',
            'old_profile': old_profile,
            'new_profile': new_risk_profile,
            'user': UserSerializer(user).data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error updating risk profile: {str(e)}")
        return Response({
            'message': 'Error interno del servidor',
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
