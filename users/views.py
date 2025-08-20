from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import authenticate
from django.shortcuts import get_object_or_404
from .models import CustomUser
from .serializers import (
    UserRegistrationSerializer, 
    UserSerializer, 
    UserUpdateSerializer,
    PasswordChangeSerializer
)

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
