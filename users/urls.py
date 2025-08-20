from django.urls import path
from .views import (
    UserRegistrationView,
    UserListView,
    UserDetailView,
    UserUpdateView,
    UserDeleteView,
    change_password,
    profile,
    validate_email,
    validate_username
)

app_name = 'user_admin'

urlpatterns = [
    # Registro y autenticación
    path('register/', UserRegistrationView.as_view(), name='user-register'),
    
    # CRUD de usuarios
    path('users/', UserListView.as_view(), name='user-list'),
    path('users/<int:pk>/', UserDetailView.as_view(), name='user-detail'),
    path('users/<int:pk>/update/', UserUpdateView.as_view(), name='user-update'),
    path('users/<int:pk>/delete/', UserDeleteView.as_view(), name='user-delete'),
    
    # Perfil y configuraciones
    path('profile/', profile, name='user-profile'),
    path('change-password/', change_password, name='change-password'),
    
    # Validaciones
    path('validate-email/', validate_email, name='validate-email'),
    path('validate-username/', validate_username, name='validate-username'),
]
