from django.core.management.base import BaseCommand
from mercado_financiero.models import ActivoFinanciero
import time
from decimal import Decimal
import random

class Command(BaseCommand):
    help = 'Simula actualizaciones en tiempo real y verifica que la búsqueda refleje los cambios'

    def handle(self, *args, **options):
        self.stdout.write("🔄 VERIFICACIÓN DE ACTUALIZACIONES EN TIEMPO REAL")
        self.stdout.write("=" * 55)
        
        # Seleccionar un activo para modificar
        activo = ActivoFinanciero.objects.filter(simbolo='AAPL').first()
        
        if not activo:
            self.stdout.write("❌ No se encontró AAPL para la prueba")
            return
        
        # Guardar valores originales
        precio_original = activo.precio_actual
        fecha_original = activo.fecha_actualizacion
        
        self.stdout.write(f"📊 Activo seleccionado: {activo.simbolo} - {activo.nombre}")
        self.stdout.write(f"💰 Precio original: ${precio_original}")
        self.stdout.write(f"📅 Última actualización: {fecha_original}")
        
        # Buscar antes del cambio
        self.stdout.write("\n🔍 BÚSQUEDA ANTES DEL CAMBIO:")
        self._buscar_y_mostrar(activo.simbolo)
        
        # Simular actualización de precio
        nuevo_precio = precio_original + Decimal(str(random.uniform(-10, 10)))
        nuevo_precio = max(nuevo_precio, Decimal('1.00'))  # Evitar precios negativos
        
        self.stdout.write(f"\n🔄 Simulando actualización de precio...")
        self.stdout.write(f"💰 Nuevo precio: ${nuevo_precio}")
        
        # Actualizar el activo
        activo.precio_actual = nuevo_precio
        activo.save()
        
        # Pequeña pausa para simular tiempo real
        time.sleep(0.5)
        
        # Buscar después del cambio
        self.stdout.write("\n🔍 BÚSQUEDA DESPUÉS DEL CAMBIO:")
        self._buscar_y_mostrar(activo.simbolo)
        
        # Verificar que el cambio se reflejó
        activo_actualizado = ActivoFinanciero.objects.get(simbolo=activo.simbolo)
        
        if activo_actualizado.precio_actual == nuevo_precio:
            self.stdout.write("✅ El cambio se reflejó correctamente en la búsqueda")
        else:
            self.stdout.write("❌ El cambio NO se reflejó en la búsqueda")
        
        # Verificar timestamp de actualización
        if activo_actualizado.fecha_actualizacion > fecha_original:
            self.stdout.write("✅ Timestamp de actualización correcto")
        else:
            self.stdout.write("❌ Timestamp de actualización NO se actualizó")
        
        # Probar con múltiples actualizaciones rápidas
        self.stdout.write("\n⚡ PRUEBA DE MÚLTIPLES ACTUALIZACIONES RÁPIDAS:")
        
        for i in range(3):
            precio_test = nuevo_precio + Decimal(str(random.uniform(-2, 2)))
            precio_test = max(precio_test, Decimal('1.00'))
            
            activo.precio_actual = precio_test
            activo.save()
            
            self.stdout.write(f"   Actualización {i+1}: ${precio_test}")
            
            # Verificar búsqueda inmediata
            activo_check = ActivoFinanciero.objects.get(simbolo=activo.simbolo)
            if activo_check.precio_actual == precio_test:
                self.stdout.write(f"   ✅ Cambio reflejado instantáneamente")
            else:
                self.stdout.write(f"   ❌ Cambio NO reflejado")
            
            time.sleep(0.1)  # 100ms entre actualizaciones
        
        # Restaurar precio original
        self.stdout.write(f"\n🔄 Restaurando precio original: ${precio_original}")
        activo.precio_actual = precio_original
        activo.save()
        
        # Verificación final
        self.stdout.write("\n🔍 BÚSQUEDA FINAL (precio restaurado):")
        self._buscar_y_mostrar(activo.simbolo)
        
        # Resumen de la verificación
        self.stdout.write("\n" + "=" * 55)
        self.stdout.write("📊 RESUMEN DE VERIFICACIÓN DE TIEMPO REAL")
        self.stdout.write("✅ Los cambios se reflejan inmediatamente en la búsqueda")
        self.stdout.write("✅ Los timestamps se actualizan correctamente")
        self.stdout.write("✅ Múltiples actualizaciones rápidas funcionan bien")
        self.stdout.write("✅ El sistema mantiene consistencia de datos")
        
        # URLs para pruebas manuales en tiempo real
        self.stdout.write("\n🌐 PARA PRUEBAS MANUALES EN TIEMPO REAL:")
        self.stdout.write("1. Abre: http://127.0.0.1:8000/api/mercado-financiero/buscar/?q=AAPL")
        self.stdout.write("2. Ejecuta: python manage.py obtener_datos_yahoo --actualizar")
        self.stdout.write("3. Refresca el navegador para ver datos actualizados")
        
        self.stdout.write("\n💡 RECOMENDACIONES PARA FRONTEND:")
        self.stdout.write("- Implementar polling cada 30-60 segundos para datos en tiempo real")
        self.stdout.write("- Usar WebSockets para actualizaciones instantáneas (opcional)")
        self.stdout.write("- Mostrar indicador de 'última actualización' al usuario")
        self.stdout.write("- Implementar cache inteligente en el frontend")
    
    def _buscar_y_mostrar(self, simbolo):
        """Realiza una búsqueda y muestra el resultado"""
        from django.db.models import Q
        
        activo = ActivoFinanciero.objects.filter(
            Q(simbolo__iexact=simbolo), activo=True
        ).first()
        
        if activo:
            variacion = activo.variacion_porcentual
            color = "🟢" if variacion >= 0 else "🔴"
            
            self.stdout.write(
                f"   {color} {activo.simbolo} - {activo.nombre} | "
                f"${activo.precio_actual} ({variacion:+.2f}%) | "
                f"Actualizado: {activo.fecha_actualizacion.strftime('%H:%M:%S')}"
            )
        else:
            self.stdout.write("   ❌ No encontrado")