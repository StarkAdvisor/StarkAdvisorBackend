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
        regex=r'^\+\d{1,3}\d{10}$', 
        message="El número debe tener el formato: código de país (+1 a +999) seguido de 10 dígitos (ej: +573001234567, +12025551234)"
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
    
    # Choices para perfil de riesgo
    RISK_PROFILE_CHOICES = [
        ('conservative', 'Conservador'),
        ('moderate', 'Moderado'),
        ('aggressive', 'Arriesgado'),
    ]
    
    # Campos adicionales
    is_verified = models.BooleanField(default=False, verbose_name='Verificado')
    risk_profile = models.CharField(
        max_length=12,
        choices=RISK_PROFILE_CHOICES,
        default='moderate',
        verbose_name='Perfil de Riesgo',
        help_text='Selecciona tu perfil de inversión según tu tolerancia al riesgo'
    )
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
    
    def get_risk_profile_display_info(self):
        """Retorna información detallada del perfil de riesgo"""
        risk_info = {
            'conservative': {
                'name': 'Conservador',
                'description': 'Prefiere inversiones seguras con bajo riesgo y retornos estables.',
                'characteristics': ['Bajo riesgo', 'Retornos estables', 'Capital protegido']
            },
            'moderate': {
                'name': 'Moderado', 
                'description': 'Busca un equilibrio entre riesgo y retorno.',
                'characteristics': ['Riesgo medio', 'Diversificación', 'Crecimiento moderado']
            },
            'aggressive': {
                'name': 'Arriesgado',
                'description': 'Busca altos retornos y está dispuesto a asumir mayores riesgos.',
                'characteristics': ['Alto riesgo', 'Altos retornos potenciales', 'Volatilidad']
            }
        }
        return risk_info.get(self.risk_profile, risk_info['moderate'])
