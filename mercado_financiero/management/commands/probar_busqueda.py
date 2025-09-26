from django.core.management.base import BaseCommand
from mercado_financiero.models import ActivoFinanciero
import json

class Command(BaseCommand):
    help = 'Prueba la funcionalidad de búsqueda de activos financieros'

    def add_arguments(self, parser):
        parser.add_argument(
            'termino',
            type=str,
            help='Término de búsqueda para probar'
        )

    def handle(self, *args, **options):
        termino = options['termino']
        
        self.stdout.write(f"🔍 Probando búsqueda con término: '{termino}'")
        
        # Simular la lógica del endpoint de búsqueda
        from django.db.models import Q
        from mercado_financiero.models import Accion, ETF, Divisa, TipoActivo
        
        # Búsqueda base
        q_objects = Q()
        q_objects |= Q(simbolo__iexact=termino)
        q_objects |= Q(simbolo__icontains=termino)
        q_objects |= Q(nombre__icontains=termino)
        
        queryset = ActivoFinanciero.objects.filter(q_objects, activo=True)
        
        # Búsqueda extendida
        if not queryset.exists() or len(termino) > 2:
            acciones_ids = Accion.objects.filter(
                Q(empresa__icontains=termino) | Q(sector__icontains=termino)
            ).values_list('activo_financiero_id', flat=True)
            
            etfs_ids = ETF.objects.filter(
                categoria__icontains=termino
            ).values_list('activo_financiero_id', flat=True)
            
            divisas_ids = Divisa.objects.filter(
                Q(moneda_base__icontains=termino) | Q(moneda_cotizacion__icontains=termino)
            ).values_list('activo_financiero_id', flat=True)
            
            extended_ids = list(acciones_ids) + list(etfs_ids) + list(divisas_ids)
            if extended_ids:
                extended_queryset = ActivoFinanciero.objects.filter(
                    Q(id__in=extended_ids), activo=True
                )
                queryset = queryset.union(extended_queryset)
        
        resultados = list(queryset)
        
        if resultados:
            self.stdout.write(f"✅ Encontrados {len(resultados)} resultados:")
            for activo in resultados:
                variacion = activo.variacion_porcentual
                color = "🟢" if variacion >= 0 else "🔴"
                
                info_extra = ""
                if activo.tipo == TipoActivo.ACCION and hasattr(activo, 'detalle_accion'):
                    info_extra = f" | {activo.detalle_accion.empresa} ({activo.detalle_accion.sector})"
                elif activo.tipo == TipoActivo.ETF and hasattr(activo, 'detalle_etf'):
                    info_extra = f" | {activo.detalle_etf.categoria}"
                elif activo.tipo == TipoActivo.DIVISA and hasattr(activo, 'detalle_divisa'):
                    info_extra = f" | {activo.detalle_divisa.moneda_base}/{activo.detalle_divisa.moneda_cotizacion}"
                
                self.stdout.write(
                    f"  {color} {activo.simbolo} - {activo.nombre} | "
                    f"${activo.precio_actual} ({variacion:+.2f}%) | "
                    f"{activo.get_tipo_display()}{info_extra}"
                )
        else:
            self.stdout.write("❌ No se encontraron resultados")
        
        # Mostrar ejemplos de búsqueda
        self.stdout.write("\n💡 Ejemplos de búsqueda que puedes probar:")
        ejemplos = ["AAPL", "Apple", "Microsoft", "Tecnología", "S&P", "USD", "EUR"]
        for ejemplo in ejemplos:
            self.stdout.write(f"   python manage.py probar_busqueda {ejemplo}")
        
        # Mostrar URLs de API
        self.stdout.write("\n🌐 URLs de API para probar:")
        self.stdout.write(f"   http://127.0.0.1:8000/api/mercado-financiero/buscar/?q={termino}")
        self.stdout.write(f"   http://127.0.0.1:8000/api/mercado-financiero/sugerencias/?q={termino[:2]}")
        self.stdout.write(f"   http://127.0.0.1:8000/api/mercado-financiero/buscar/?q={termino}&tipo=ACCION")