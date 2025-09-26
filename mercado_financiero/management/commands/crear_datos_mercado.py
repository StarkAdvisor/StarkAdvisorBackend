from django.core.management.base import BaseCommand
from decimal import Decimal
from mercado_financiero.models import ActivoFinanciero, Accion, ETF, Divisa, TipoActivo

class Command(BaseCommand):
    help = 'Crea datos de prueba para el mercado financiero'

    def handle(self, *args, **options):
        # Limpiar datos existentes
        ActivoFinanciero.objects.all().delete()
        
        # Crear acciones de prueba
        acciones_data = [
            {
                'simbolo': 'AAPL',
                'nombre': 'Apple Inc.',
                'precio_actual': Decimal('150.25'),
                'precio_anterior': Decimal('148.50'),
                'volumen': 45000000,
                'mercado': 'NASDAQ',
                'sector': 'Tecnología',
                'empresa': 'Apple Inc.',
                'capitalizacion_mercado': 2400000000000
            },
            {
                'simbolo': 'GOOGL',
                'nombre': 'Alphabet Inc.',
                'precio_actual': Decimal('125.80'),
                'precio_anterior': Decimal('127.20'),
                'volumen': 32000000,
                'mercado': 'NASDAQ',
                'sector': 'Tecnología',
                'empresa': 'Alphabet Inc.',
                'capitalizacion_mercado': 1600000000000
            },
            {
                'simbolo': 'MSFT',
                'nombre': 'Microsoft Corporation',
                'precio_actual': Decimal('332.50'),
                'precio_anterior': Decimal('330.75'),
                'volumen': 28000000,
                'mercado': 'NASDAQ',
                'sector': 'Tecnología',
                'empresa': 'Microsoft Corporation',
                'capitalizacion_mercado': 2500000000000
            },
            {
                'simbolo': 'TSLA',
                'nombre': 'Tesla Inc.',
                'precio_actual': Decimal('245.75'),
                'precio_anterior': Decimal('250.20'),
                'volumen': 55000000,
                'mercado': 'NASDAQ',
                'sector': 'Automotriz',
                'empresa': 'Tesla Inc.',
                'capitalizacion_mercado': 780000000000
            },
            {
                'simbolo': 'JPM',
                'nombre': 'JPMorgan Chase & Co.',
                'precio_actual': Decimal('145.60'),
                'precio_anterior': Decimal('143.80'),
                'volumen': 15000000,
                'mercado': 'NYSE',
                'sector': 'Financiero',
                'empresa': 'JPMorgan Chase & Co.',
                'capitalizacion_mercado': 430000000000
            }
        ]
        
        for data in acciones_data:
            activo = ActivoFinanciero.objects.create(
                simbolo=data['simbolo'],
                nombre=data['nombre'],
                tipo=TipoActivo.ACCION,
                precio_actual=data['precio_actual'],
                precio_anterior=data['precio_anterior'],
                volumen=data['volumen'],
                mercado=data['mercado']
            )
            
            Accion.objects.create(
                activo_financiero=activo,
                sector=data['sector'],
                empresa=data['empresa'],
                capitalizacion_mercado=data['capitalizacion_mercado']
            )
        
        # Crear ETFs de prueba
        etfs_data = [
            {
                'simbolo': 'SPY',
                'nombre': 'SPDR S&P 500 ETF Trust',
                'precio_actual': Decimal('425.80'),
                'precio_anterior': Decimal('423.15'),
                'volumen': 85000000,
                'mercado': 'NYSE',
                'categoria': 'S&P 500',
                'ratio_gastos': Decimal('0.0945'),
                'activos_bajo_gestion': 350000000000
            },
            {
                'simbolo': 'QQQ',
                'nombre': 'Invesco QQQ Trust',
                'precio_actual': Decimal('315.25'),
                'precio_anterior': Decimal('318.90'),
                'volumen': 42000000,
                'mercado': 'NASDAQ',
                'categoria': 'NASDAQ 100',
                'ratio_gastos': Decimal('0.2000'),
                'activos_bajo_gestion': 180000000000
            },
            {
                'simbolo': 'VTI',
                'nombre': 'Vanguard Total Stock Market ETF',
                'precio_actual': Decimal('210.45'),
                'precio_anterior': Decimal('208.75'),
                'volumen': 35000000,
                'mercado': 'NYSE',
                'categoria': 'Mercado Total',
                'ratio_gastos': Decimal('0.0300'),
                'activos_bajo_gestion': 290000000000
            }
        ]
        
        for data in etfs_data:
            activo = ActivoFinanciero.objects.create(
                simbolo=data['simbolo'],
                nombre=data['nombre'],
                tipo=TipoActivo.ETF,
                precio_actual=data['precio_actual'],
                precio_anterior=data['precio_anterior'],
                volumen=data['volumen'],
                mercado=data['mercado']
            )
            
            ETF.objects.create(
                activo_financiero=activo,
                categoria=data['categoria'],
                ratio_gastos=data['ratio_gastos'],
                activos_bajo_gestion=data['activos_bajo_gestion']
            )
        
        # Crear divisas de prueba
        divisas_data = [
            {
                'simbolo': 'USD/COP',
                'nombre': 'Dólar Estadounidense / Peso Colombiano',
                'precio_actual': Decimal('4150.75'),
                'precio_anterior': Decimal('4135.20'),
                'volumen': 125000000,
                'mercado': 'FX',
                'moneda_base': 'USD',
                'moneda_cotizacion': 'COP',
                'tipo_cambio_referencia': Decimal('4142.50')
            },
            {
                'simbolo': 'EUR/USD',
                'nombre': 'Euro / Dólar Estadounidense',
                'precio_actual': Decimal('1.0875'),
                'precio_anterior': Decimal('1.0920'),
                'volumen': 2500000000,
                'mercado': 'FX',
                'moneda_base': 'EUR',
                'moneda_cotizacion': 'USD',
                'tipo_cambio_referencia': Decimal('1.0895')
            },
            {
                'simbolo': 'GBP/USD',
                'nombre': 'Libra Esterlina / Dólar Estadounidense',
                'precio_actual': Decimal('1.2645'),
                'precio_anterior': Decimal('1.2680'),
                'volumen': 1800000000,
                'mercado': 'FX',
                'moneda_base': 'GBP',
                'moneda_cotizacion': 'USD',
                'tipo_cambio_referencia': Decimal('1.2662')
            },
            {
                'simbolo': 'USD/JPY',
                'nombre': 'Dólar Estadounidense / Yen Japonés',
                'precio_actual': Decimal('148.25'),
                'precio_anterior': Decimal('147.80'),
                'volumen': 2200000000,
                'mercado': 'FX',
                'moneda_base': 'USD',
                'moneda_cotizacion': 'JPY',
                'tipo_cambio_referencia': Decimal('148.05')
            }
        ]
        
        for data in divisas_data:
            activo = ActivoFinanciero.objects.create(
                simbolo=data['simbolo'],
                nombre=data['nombre'],
                tipo=TipoActivo.DIVISA,
                precio_actual=data['precio_actual'],
                precio_anterior=data['precio_anterior'],
                volumen=data['volumen'],
                mercado=data['mercado']
            )
            
            Divisa.objects.create(
                activo_financiero=activo,
                moneda_base=data['moneda_base'],
                moneda_cotizacion=data['moneda_cotizacion'],
                tipo_cambio_referencia=data['tipo_cambio_referencia']
            )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'✅ Datos de prueba creados exitosamente:\n'
                f'   • {len(acciones_data)} Acciones\n'
                f'   • {len(etfs_data)} ETFs\n'
                f'   • {len(divisas_data)} Divisas\n'
                f'   Total: {len(acciones_data) + len(etfs_data) + len(divisas_data)} activos financieros'
            )
        )