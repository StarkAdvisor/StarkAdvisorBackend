from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal

class TipoActivo(models.TextChoices):
    """Enum para los tipos de activos financieros"""
    ACCION = 'ACCION', 'Acción'
    ETF = 'ETF', 'ETF'
    DIVISA = 'DIVISA', 'Divisa'

class ActivoFinanciero(models.Model):
    """
    Modelo base para todos los activos financieros
    Incluye información común para Acciones, ETFs y Divisas
    """
    simbolo = models.CharField(
        max_length=20, 
        unique=True,
        help_text="Símbolo del activo (ej: AAPL, USD/COP)"
    )
    nombre = models.CharField(
        max_length=200,
        help_text="Nombre completo del activo"
    )
    tipo = models.CharField(
        max_length=10,
        choices=TipoActivo.choices,
        help_text="Tipo de activo financiero"
    )
    precio_actual = models.DecimalField(
        max_digits=15,
        decimal_places=4,
        validators=[MinValueValidator(Decimal('0.0001'))],
        help_text="Precio actual del activo"
    )
    precio_anterior = models.DecimalField(
        max_digits=15,
        decimal_places=4,
        validators=[MinValueValidator(Decimal('0.0001'))],
        help_text="Precio del cierre anterior"
    )
    volumen = models.BigIntegerField(
        validators=[MinValueValidator(0)],
        help_text="Volumen de transacciones"
    )
    mercado = models.CharField(
        max_length=100,
        help_text="Mercado donde se cotiza (ej: NYSE, NASDAQ, FX)"
    )
    moneda = models.CharField(
        max_length=10,
        default='USD',
        help_text="Moneda de cotización"
    )
    
    # Campos de auditoría
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    activo = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Activo Financiero"
        verbose_name_plural = "Activos Financieros"
        ordering = ['tipo', 'simbolo']
        indexes = [
            models.Index(fields=['tipo']),
            models.Index(fields=['simbolo']),
            models.Index(fields=['fecha_actualizacion']),
        ]
    
    def __str__(self):
        return f"{self.simbolo} - {self.nombre}"
    
    @property
    def variacion_porcentual(self):
        """Calcula la variación porcentual diaria"""
        if self.precio_anterior and self.precio_anterior > 0:
            return ((self.precio_actual - self.precio_anterior) / self.precio_anterior) * 100
        return 0
    
    @property
    def variacion_absoluta(self):
        """Calcula la variación absoluta diaria"""
        return self.precio_actual - self.precio_anterior
    
    @property
    def es_ganancia(self):
        """Indica si la variación es positiva"""
        return self.variacion_absoluta >= 0

class Accion(models.Model):
    """
    Información específica para acciones
    """
    activo_financiero = models.OneToOneField(
        ActivoFinanciero,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='detalle_accion'
    )
    sector = models.CharField(
        max_length=100,
        help_text="Sector económico (ej: Tecnología, Salud, Financiero)"
    )
    empresa = models.CharField(
        max_length=200,
        help_text="Nombre de la empresa"
    )
    capitalizacion_mercado = models.BigIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        help_text="Capitalización de mercado en USD"
    )
    
    class Meta:
        verbose_name = "Acción"
        verbose_name_plural = "Acciones"
    
    def __str__(self):
        return f"{self.activo_financiero.simbolo} - {self.empresa}"

class ETF(models.Model):
    """
    Información específica para ETFs
    """
    activo_financiero = models.OneToOneField(
        ActivoFinanciero,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='detalle_etf'
    )
    categoria = models.CharField(
        max_length=100,
        help_text="Categoría del ETF (ej: S&P 500, Commodities, Bonds)"
    )
    ratio_gastos = models.DecimalField(
        max_digits=5,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="Ratio de gastos del ETF (%)"
    )
    activos_bajo_gestion = models.BigIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        help_text="Activos bajo gestión en USD"
    )
    
    class Meta:
        verbose_name = "ETF"
        verbose_name_plural = "ETFs"
    
    def __str__(self):
        return f"{self.activo_financiero.simbolo} - {self.categoria}"

class Divisa(models.Model):
    """
    Información específica para divisas
    """
    activo_financiero = models.OneToOneField(
        ActivoFinanciero,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='detalle_divisa'
    )
    moneda_base = models.CharField(
        max_length=10,
        help_text="Moneda base del par (ej: USD en USD/COP)"
    )
    moneda_cotizacion = models.CharField(
        max_length=10,
        help_text="Moneda de cotización del par (ej: COP en USD/COP)"
    )
    tipo_cambio_referencia = models.DecimalField(
        max_digits=15,
        decimal_places=6,
        null=True,
        blank=True,
        help_text="Tipo de cambio de referencia del banco central"
    )
    
    class Meta:
        verbose_name = "Divisa"
        verbose_name_plural = "Divisas"
    
    def __str__(self):
        return f"{self.moneda_base}/{self.moneda_cotizacion}"
