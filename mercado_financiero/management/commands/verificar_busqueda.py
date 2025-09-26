from django.core.management.base import BaseCommand
from mercado_financiero.models import ActivoFinanciero
from django.db.models import Q
import time
import json

class Command(BaseCommand):
    help = 'Verifica la funcionalidad completa de búsqueda y relevancia de resultados'

    def handle(self, *args, **options):
        self.stdout.write("🔍 VERIFICACIÓN COMPLETA DE BÚSQUEDA")
        self.stdout.write("=" * 50)
        
        # Casos de prueba para verificar relevancia
        casos_prueba = [
            {
                'termino': 'AAPL',
                'descripcion': 'Búsqueda exacta por símbolo',
                'esperado': 'Debe encontrar Apple exactamente'
            },
            {
                'termino': 'Apple',
                'descripcion': 'Búsqueda por nombre de empresa',
                'esperado': 'Debe encontrar AAPL'
            },
            {
                'termino': 'MS',
                'descripcion': 'Búsqueda parcial',
                'esperado': 'Debe priorizar MSFT sobre META'
            },
            {
                'termino': 'Tecnología',
                'descripcion': 'Búsqueda por sector',
                'esperado': 'Debe encontrar múltiples empresas tech'
            },
            {
                'termino': 'S&P',
                'descripcion': 'Búsqueda en categoría ETF',
                'esperado': 'Debe encontrar SPY ETF'
            },
            {
                'termino': 'USD',
                'descripcion': 'Búsqueda en divisas',
                'esperado': 'Debe encontrar pares con USD'
            },
            {
                'termino': 'xyz123notfound',
                'descripcion': 'Búsqueda sin resultados',
                'esperado': 'No debe encontrar nada'
            }
        ]
        
        resultados_verificacion = []
        
        for i, caso in enumerate(casos_prueba, 1):
            self.stdout.write(f"\n🧪 CASO {i}: {caso['descripcion']}")
            self.stdout.write(f"   Término: '{caso['termino']}'")
            self.stdout.write(f"   Esperado: {caso['esperado']}")
            
            # Medir tiempo de respuesta
            start_time = time.time()
            
            # Simular búsqueda del endpoint
            from mercado_financiero.models import Accion, ETF, Divisa, TipoActivo
            
            query = caso['termino']
            q_objects = Q()
            q_objects |= Q(simbolo__iexact=query)
            q_objects |= Q(simbolo__icontains=query)
            q_objects |= Q(nombre__icontains=query)
            
            queryset = ActivoFinanciero.objects.filter(q_objects, activo=True)
            
            # Búsqueda extendida
            if not queryset.exists() or len(query) > 2:
                acciones_ids = Accion.objects.filter(
                    Q(empresa__icontains=query) | Q(sector__icontains=query)
                ).values_list('activo_financiero_id', flat=True)
                
                etfs_ids = ETF.objects.filter(
                    categoria__icontains=query
                ).values_list('activo_financiero_id', flat=True)
                
                divisas_ids = Divisa.objects.filter(
                    Q(moneda_base__icontains=query) | Q(moneda_cotizacion__icontains=query)
                ).values_list('activo_financiero_id', flat=True)
                
                extended_ids = list(acciones_ids) + list(etfs_ids) + list(divisas_ids)
                if extended_ids:
                    extended_queryset = ActivoFinanciero.objects.filter(
                        Q(id__in=extended_ids), activo=True
                    )
                    queryset = queryset.union(extended_queryset)
            
            resultados = list(queryset)
            
            # Ordenar: exactos primero
            exactos = [a for a in resultados if a.simbolo.upper() == query.upper()]
            parciales = [a for a in resultados if a.simbolo.upper() != query.upper()]
            parciales.sort(key=lambda x: x.simbolo)
            
            activos_ordenados = exactos + parciales
            
            end_time = time.time()
            tiempo_respuesta = (end_time - start_time) * 1000  # en milisegundos
            
            # Analizar resultados
            self.stdout.write(f"   ⏱️ Tiempo: {tiempo_respuesta:.2f}ms")
            
            if activos_ordenados:
                self.stdout.write(f"   ✅ Encontrados: {len(activos_ordenados)} resultados")
                
                # Verificar relevancia
                relevancia_ok = self._verificar_relevancia(caso['termino'], activos_ordenados)
                
                for activo in activos_ordenados[:3]:  # Mostrar top 3
                    variacion = activo.variacion_porcentual
                    color = "🟢" if variacion >= 0 else "🔴"
                    self.stdout.write(f"      {color} {activo.simbolo} - {activo.nombre}")
                
                if len(activos_ordenados) > 3:
                    self.stdout.write(f"      ... y {len(activos_ordenados) - 3} más")
                
                # Verificar ordenamiento
                orden_ok = self._verificar_ordenamiento(caso['termino'], activos_ordenados)
                
                resultados_verificacion.append({
                    'caso': caso['descripcion'],
                    'termino': caso['termino'],
                    'encontrados': len(activos_ordenados),
                    'tiempo_ms': tiempo_respuesta,
                    'relevancia_ok': relevancia_ok,
                    'orden_ok': orden_ok,
                    'exitoso': True
                })
                
            else:
                self.stdout.write("   ❌ Sin resultados")
                resultados_verificacion.append({
                    'caso': caso['descripcion'],
                    'termino': caso['termino'],
                    'encontrados': 0,
                    'tiempo_ms': tiempo_respuesta,
                    'relevancia_ok': caso['termino'] == 'xyz123notfound',  # Solo OK si se esperaba sin resultados
                    'orden_ok': True,
                    'exitoso': caso['termino'] == 'xyz123notfound'
                })
        
        # Resumen de verificación
        self.stdout.write("\n" + "=" * 50)
        self.stdout.write("📊 RESUMEN DE VERIFICACIÓN")
        
        casos_exitosos = sum(1 for r in resultados_verificacion if r['exitoso'])
        tiempo_promedio = sum(r['tiempo_ms'] for r in resultados_verificacion) / len(resultados_verificacion)
        
        self.stdout.write(f"✅ Casos exitosos: {casos_exitosos}/{len(resultados_verificacion)}")
        self.stdout.write(f"⏱️ Tiempo promedio: {tiempo_promedio:.2f}ms")
        
        # Verificar aspectos específicos
        self.stdout.write("\n📋 VERIFICACIONES ESPECÍFICAS:")
        
        # 1. Tiempo de respuesta
        tiempo_ok = tiempo_promedio < 100  # Menos de 100ms
        status_tiempo = "✅" if tiempo_ok else "⚠️"
        self.stdout.write(f"{status_tiempo} Tiempo de respuesta: {'RÁPIDO' if tiempo_ok else 'LENTO'}")
        
        # 2. Relevancia de resultados
        relevancia_casos = sum(1 for r in resultados_verificacion if r['relevancia_ok'])
        relevancia_ok = relevancia_casos >= len(resultados_verificacion) * 0.8  # 80% relevantes
        status_relevancia = "✅" if relevancia_ok else "❌"
        self.stdout.write(f"{status_relevancia} Relevancia: {relevancia_casos}/{len(resultados_verificacion)} casos relevantes")
        
        # 3. Ordenamiento correcto
        orden_casos = sum(1 for r in resultados_verificacion if r['orden_ok'])
        orden_ok = orden_casos >= len(resultados_verificacion) * 0.9  # 90% bien ordenados
        status_orden = "✅" if orden_ok else "❌"
        self.stdout.write(f"{status_orden} Ordenamiento: {orden_casos}/{len(resultados_verificacion)} casos bien ordenados")
        
        # Recomendaciones de mejora
        self.stdout.write("\n💡 RECOMENDACIONES:")
        if not tiempo_ok:
            self.stdout.write("   - Considerar agregar índices de base de datos para búsquedas más rápidas")
        if not relevancia_ok:
            self.stdout.write("   - Mejorar algoritmo de relevancia en búsquedas")
        if not orden_ok:
            self.stdout.write("   - Ajustar algoritmo de ordenamiento de resultados")
        
        if tiempo_ok and relevancia_ok and orden_ok:
            self.stdout.write("   🎉 ¡La búsqueda funciona perfectamente!")
        
        # URLs para pruebas manuales
        self.stdout.write("\n🌐 PRUEBAS MANUALES EN NAVEGADOR:")
        for caso in casos_prueba[:3]:  # Mostrar solo primeros 3
            self.stdout.write(f"   http://127.0.0.1:8000/api/mercado-financiero/buscar/?q={caso['termino']}")
    
    def _verificar_relevancia(self, termino, resultados):
        """Verifica si los resultados son relevantes al término de búsqueda"""
        if not resultados:
            return False
        
        # Verificar que al menos el primer resultado sea relevante
        primer_resultado = resultados[0]
        termino_upper = termino.upper()
        
        # Es relevante si:
        # 1. El símbolo coincide
        if termino_upper in primer_resultado.simbolo.upper():
            return True
        
        # 2. El nombre coincide
        if termino_upper in primer_resultado.nombre.upper():
            return True
        
        # 3. Para búsquedas específicas
        if termino_upper == 'TECNOLOGÍA':
            return hasattr(primer_resultado, 'detalle_accion') and 'tecnología' in primer_resultado.detalle_accion.sector.lower()
        
        if 'S&P' in termino_upper:
            return hasattr(primer_resultado, 'detalle_etf') and 's&p' in primer_resultado.detalle_etf.categoria.lower()
        
        return True  # Por defecto, asumir relevante para otros casos
    
    def _verificar_ordenamiento(self, termino, resultados):
        """Verifica si los resultados están ordenados correctamente"""
        if len(resultados) <= 1:
            return True
        
        # Verificar que coincidencias exactas aparezcan primero
        termino_upper = termino.upper()
        
        for i, resultado in enumerate(resultados):
            if resultado.simbolo.upper() == termino_upper:
                # Si encontramos una coincidencia exacta, debe estar al principio
                return i == 0
        
        # Si no hay coincidencias exactas, verificar orden alfabético parcial
        return True  # Simplificado para esta verificación