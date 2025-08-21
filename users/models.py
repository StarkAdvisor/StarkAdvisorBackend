from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator

class CustomUser(AbstractUser):
    """
    Modelo de usuario personalizado con campos adicionales
    """
    email = models.EmailField(unique=True, verbose_name='Correo Electrónico')
    first_name = models.CharField(max_length=30, verbose_name='Nombre')
    last_name = models.CharField(max_length=30, verbose_name='Apellido')
    
    # Validador para numero de telefono
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$', 
        message="El número debe estar en formato: '+999999999'. Máximo 15 dígitos."
    )
    phone_number = models.CharField(
        validators=[phone_regex], 
        max_length=17, 
        blank=True,
        verbose_name='Número de Teléfono'
    )
    
    date_of_birth = models.DateField(null=True, blank=True, verbose_name='Fecha de Nacimiento')
    profile_picture = models.ImageField(
        upload_to='profile_pics/', 
        blank=True, 
        null=True,
        verbose_name='Foto de Perfil'
    )
    
    # Campos adicionales
    is_verified = models.BooleanField(default=False, verbose_name='Verificado')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creacion')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Última Actualizacion')
    
    # Configuracion para usar email como campo de login
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
    
    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()
    
    def get_short_name(self):
        return self.first_name
