from rest_framework import serializers
from .models import ActivoFinanciero, Accion, ETF, Divisa, TipoActivo

class ActivoFinancieroListSerializer(serializers.ModelSerializer):
    """
    Serializer para listar activos financieros con información básica
    Usado para las tablas del mercado financiero
    """
    variacion_porcentual = serializers.ReadOnlyField()
    variacion_absoluta = serializers.ReadOnlyField()
    es_ganancia = serializers.ReadOnlyField()
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)
    
    class Meta:
        model = ActivoFinanciero
        fields = [
            'id',
            'simbolo',
            'nombre',
            'tipo',
            'tipo_display',
            'precio_actual',
            'precio_anterior',
            'variacion_porcentual',
            'variacion_absoluta',
            'es_ganancia',
            'volumen',
            'mercado',
            'moneda',
            'fecha_actualizacion'
        ]

class AccionListSerializer(serializers.ModelSerializer):
    """
    Serializer para acciones con información básica más sector y empresa
    """
    activo_financiero = ActivoFinancieroListSerializer(read_only=True)
    
    class Meta:
        model = Accion
        fields = [
            'activo_financiero',
            'sector',
            'empresa',
            'capitalizacion_mercado'
        ]

class ETFListSerializer(serializers.ModelSerializer):
    """
    Serializer para ETFs con información básica más categoría
    """
    activo_financiero = ActivoFinancieroListSerializer(read_only=True)
    
    class Meta:
        model = ETF
        fields = [
            'activo_financiero',
            'categoria',
            'ratio_gastos',
            'activos_bajo_gestion'
        ]

class DivisaListSerializer(serializers.ModelSerializer):
    """
    Serializer para divisas con información básica más pares de monedas
    """
    activo_financiero = ActivoFinancieroListSerializer(read_only=True)
    
    class Meta:
        model = Divisa
        fields = [
            'activo_financiero',
            'moneda_base',
            'moneda_cotizacion',
            'tipo_cambio_referencia'
        ]

class ResumenMercadoSerializer(serializers.Serializer):
    """
    Serializer para el resumen general del mercado
    """
    total_activos = serializers.IntegerField()
    total_acciones = serializers.IntegerField()
    total_etfs = serializers.IntegerField()
    total_divisas = serializers.IntegerField()
    activos_en_alza = serializers.IntegerField()
    activos_en_baja = serializers.IntegerField()
    ultimo_update = serializers.DateTimeField()