from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """
    Administrador personalizado para el modelo CustomUser
    """
    list_display = (
        'username', 'email', 'first_name', 'last_name', 
        'is_verified', 'is_active', 'is_staff', 'created_at'
    )
    list_filter = (
        'is_active', 'is_staff', 'is_superuser', 'is_verified', 'created_at'
    )
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('-created_at',)
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Información Personal', {
            'fields': (
                'first_name', 'last_name', 'email', 
                'phone_number', 'date_of_birth', 'profile_picture'
            )
        }),
        ('Permisos', {
            'fields': (
                'is_active', 'is_staff', 'is_superuser', 
                'is_verified', 'groups', 'user_permissions'
            ),
        }),
        ('Fechas Importantes', {
            'fields': ('last_login', 'date_joined', 'created_at', 'updated_at')
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username', 'email', 'first_name', 'last_name',
                'password1', 'password2'
            ),
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at', 'date_joined', 'last_login')
