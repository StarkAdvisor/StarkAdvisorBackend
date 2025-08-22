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
    validate_username,
    login_view,
    logout_view,
    session_status,
    risk_profiles,
    update_risk_profile
)

app_name = 'user_admin'

urlpatterns = [
    # Autenticación
    path('register/', UserRegistrationView.as_view(), name='user-register'),
    path('login/', login_view, name='user-login'),
    path('logout/', logout_view, name='user-logout'),
    path('session-status/', session_status, name='session-status'),
    
    # CRUD de usuarios
    path('users/', UserListView.as_view(), name='user-list'),
    path('users/<int:pk>/', UserDetailView.as_view(), name='user-detail'),
    path('users/<int:pk>/update/', UserUpdateView.as_view(), name='user-update'),
    path('users/<int:pk>/delete/', UserDeleteView.as_view(), name='user-delete'),
    
    # Perfil y configuraciones
    path('profile/', profile, name='user-profile'),
    path('change-password/', change_password, name='change-password'),
    
    # Perfil de riesgo
    path('risk-profiles/', risk_profiles, name='risk-profiles'),
    path('update-risk-profile/', update_risk_profile, name='update-risk-profile'),
    
    # Validaciones
    path('validate-email/', validate_email, name='validate-email'),
    path('validate-username/', validate_username, name='validate-username'),
]
