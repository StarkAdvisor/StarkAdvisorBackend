from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count, Q, F
from django.utils import timezone
from .models import ActivoFinanciero, Accion, ETF, Divisa, TipoActivo
from .serializers import (
    ActivoFinancieroListSerializer,
    AccionListSerializer,
    ETFListSerializer,
    DivisaListSerializer,
    ResumenMercadoSerializer
)

class MercadoFinancieroViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para gestionar los datos del mercado financiero
    Proporciona endpoints para listar activos por categoría
    """
    queryset = ActivoFinanciero.objects.filter(activo=True)
    serializer_class = ActivoFinancieroListSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filtrar activos por tipo si se especifica"""
        queryset = super().get_queryset()
        tipo = self.request.query_params.get('tipo', None)
        
        if tipo and tipo in [choice[0] for choice in TipoActivo.choices]:
            queryset = queryset.filter(tipo=tipo)
        
        return queryset.order_by('simbolo')
    
    @action(detail=False, methods=['get'])
    def acciones(self, request):
        """
        Endpoint específico para obtener todas las acciones
        GET /api/mercado-financiero/acciones/
        """
        acciones = Accion.objects.select_related('activo_financiero').filter(
            activo_financiero__activo=True
        ).order_by('activo_financiero__simbolo')
        
        serializer = AccionListSerializer(acciones, many=True)
        return Response({
            'success': True,
            'data': serializer.data,
            'total': acciones.count(),
            'tipo': 'acciones'
        })
    
    @action(detail=False, methods=['get'])
    def etfs(self, request):
        """
        Endpoint específico para obtener todos los ETFs
        GET /api/mercado-financiero/etfs/
        """
        etfs = ETF.objects.select_related('activo_financiero').filter(
            activo_financiero__activo=True
        ).order_by('activo_financiero__simbolo')
        
        serializer = ETFListSerializer(etfs, many=True)
        return Response({
            'success': True,
            'data': serializer.data,
            'total': etfs.count(),
            'tipo': 'etfs'
        })
    
    @action(detail=False, methods=['get'])
    def divisas(self, request):
        """
        Endpoint específico para obtener todas las divisas
        GET /api/mercado-financiero/divisas/
        """
        divisas = Divisa.objects.select_related('activo_financiero').filter(
            activo_financiero__activo=True
        ).order_by('activo_financiero__simbolo')
        
        serializer = DivisaListSerializer(divisas, many=True)
        return Response({
            'success': True,
            'data': serializer.data,
            'total': divisas.count(),
            'tipo': 'divisas'
        })
    
    @action(detail=False, methods=['get'])
    def resumen(self, request):
        """
        Endpoint para obtener resumen general del mercado
        GET /api/mercado-financiero/resumen/
        """
        activos_totales = ActivoFinanciero.objects.filter(activo=True)
        
        # Conteos por tipo
        stats = activos_totales.aggregate(
            total_activos=Count('id'),
            total_acciones=Count('id', filter=Q(tipo=TipoActivo.ACCION)),
            total_etfs=Count('id', filter=Q(tipo=TipoActivo.ETF)),
            total_divisas=Count('id', filter=Q(tipo=TipoActivo.DIVISA))
        )
        
        # Activos en alza/baja
        activos_en_alza = activos_totales.filter(
            precio_actual__gt=F('precio_anterior')
        ).count()
        
        activos_en_baja = activos_totales.filter(
            precio_actual__lt=F('precio_anterior')
        ).count()
        
        # Último update
        ultimo_update = activos_totales.order_by('-fecha_actualizacion').first()
        ultimo_update_time = ultimo_update.fecha_actualizacion if ultimo_update else timezone.now()
        
        resumen_data = {
            **stats,
            'activos_en_alza': activos_en_alza,
            'activos_en_baja': activos_en_baja,
            'ultimo_update': ultimo_update_time
        }
        
        serializer = ResumenMercadoSerializer(resumen_data)
        return Response({
            'success': True,
            'data': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def buscar(self, request):
        """
        Endpoint mejorado para buscar activos por símbolo, nombre o empresa
        GET /api/mercado-financiero/buscar/?q=AAPL&tipo=ACCION&limit=10
        
        Parámetros:
        - q: Término de búsqueda (símbolo, nombre, empresa)
        - tipo: Filtrar por tipo (ACCION, ETF, DIVISA) - opcional
        - limit: Límite de resultados (default: 10, max: 50)
        """
        query = request.query_params.get('q', '').strip()
        tipo_filtro = request.query_params.get('tipo', '').strip().upper()
        limit = min(int(request.query_params.get('limit', 10)), 50)
        
        if not query:
            return Response({
                'success': False,
                'error': 'Parámetro de búsqueda requerido',
                'message': 'Ingresa un símbolo o nombre para buscar'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Búsqueda base en ActivoFinanciero
        q_objects = Q()
        
        # Búsqueda por símbolo (exacta y parcial)
        q_objects |= Q(simbolo__iexact=query)  # Coincidencia exacta (prioridad)
        q_objects |= Q(simbolo__icontains=query)  # Coincidencia parcial
        
        # Búsqueda por nombre
        q_objects |= Q(nombre__icontains=query)
        
        # Filtro base
        queryset = ActivoFinanciero.objects.filter(q_objects, activo=True)
        
        # Filtrar por tipo si se especifica
        if tipo_filtro and tipo_filtro in [choice[0] for choice in TipoActivo.choices]:
            queryset = queryset.filter(tipo=tipo_filtro)
        
        # Búsqueda extendida en tablas relacionadas
        if not queryset.exists() or len(query) > 2:
            # Buscar en detalles de acciones (empresa, sector)
            acciones_ids = Accion.objects.filter(
                Q(empresa__icontains=query) | Q(sector__icontains=query)
            ).values_list('activo_financiero_id', flat=True)
            
            # Buscar en detalles de ETFs (categoría)
            etfs_ids = ETF.objects.filter(
                categoria__icontains=query
            ).values_list('activo_financiero_id', flat=True)
            
            # Buscar en detalles de divisas (monedas)
            divisas_ids = Divisa.objects.filter(
                Q(moneda_base__icontains=query) | Q(moneda_cotizacion__icontains=query)
            ).values_list('activo_financiero_id', flat=True)
            
            # Combinar resultados
            extended_ids = list(acciones_ids) + list(etfs_ids) + list(divisas_ids)
            if extended_ids:
                extended_q = Q(id__in=extended_ids)
                if tipo_filtro and tipo_filtro in [choice[0] for choice in TipoActivo.choices]:
                    extended_q &= Q(tipo=tipo_filtro)
                
                extended_queryset = ActivoFinanciero.objects.filter(extended_q, activo=True)
                queryset = queryset.union(extended_queryset)
        
        # Ordenar resultados: exactos primero, luego por símbolo
        resultados = list(queryset)
        
        # Priorizar coincidencias exactas de símbolo
        exactos = [a for a in resultados if a.simbolo.upper() == query.upper()]
        parciales = [a for a in resultados if a.simbolo.upper() != query.upper()]
        
        # Ordenar parciales por símbolo
        parciales.sort(key=lambda x: x.simbolo)
        
        # Combinar y limitar
        activos_ordenados = (exactos + parciales)[:limit]
        
        # Serializar resultados
        serializer = ActivoFinancieroListSerializer(activos_ordenados, many=True)
        
        # Preparar información adicional para cada resultado
        resultados_enriquecidos = []
        for activo_data in serializer.data:
            resultado = activo_data.copy()
            
            # Agregar información específica según el tipo
            activo_obj = next(a for a in activos_ordenados if a.id == activo_data['id'])
            
            if activo_obj.tipo == TipoActivo.ACCION and hasattr(activo_obj, 'detalle_accion'):
                resultado['empresa'] = activo_obj.detalle_accion.empresa
                resultado['sector'] = activo_obj.detalle_accion.sector
            elif activo_obj.tipo == TipoActivo.ETF and hasattr(activo_obj, 'detalle_etf'):
                resultado['categoria'] = activo_obj.detalle_etf.categoria
            elif activo_obj.tipo == TipoActivo.DIVISA and hasattr(activo_obj, 'detalle_divisa'):
                resultado['par_divisas'] = f"{activo_obj.detalle_divisa.moneda_base}/{activo_obj.detalle_divisa.moneda_cotizacion}"
            
            resultados_enriquecidos.append(resultado)
        
        return Response({
            'success': True,
            'data': resultados_enriquecidos,
            'total': len(resultados_enriquecidos),
            'total_found': len(resultados),
            'query': query,
            'tipo_filtro': tipo_filtro if tipo_filtro else None,
            'limit_aplicado': limit,
            'message': f"Se encontraron {len(resultados)} resultados" if resultados else "No se encontraron resultados"
        })
    
    @action(detail=False, methods=['get'])
    def sugerencias(self, request):
        """
        Endpoint para autocompletado de búsqueda
        GET /api/mercado-financiero/sugerencias/?q=AA&limit=5
        """
        query = request.query_params.get('q', '').strip()
        limit = min(int(request.query_params.get('limit', 5)), 10)
        
        if len(query) < 1:
            return Response({
                'success': True,
                'data': [],
                'message': 'Ingresa al menos 1 carácter'
            })
        
        # Buscar sugerencias rápidas
        activos = ActivoFinanciero.objects.filter(
            Q(simbolo__istartswith=query) | Q(nombre__icontains=query),
            activo=True
        ).order_by('simbolo')[:limit]
        
        sugerencias = []
        for activo in activos:
            sugerencias.append({
                'simbolo': activo.simbolo,
                'nombre': activo.nombre,
                'tipo': activo.get_tipo_display(),
                'precio': float(activo.precio_actual)
            })
        
        return Response({
            'success': True,
            'data': sugerencias,
            'total': len(sugerencias)
        })
