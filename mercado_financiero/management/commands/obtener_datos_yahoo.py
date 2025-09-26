from django.core.management.base import BaseCommand
from decimal import Decimal
import yfinance as yf
from mercado_financiero.models import ActivoFinanciero, Accion, ETF, Divisa, TipoActivo
import pandas as pd

class Command(BaseCommand):
    help = 'Obtiene datos reales de Yahoo Finance y los almacena en la base de datos'

    def add_arguments(self, parser):
        parser.add_argument(
            '--actualizar',
            action='store_true',
            help='Actualizar datos existentes en lugar de crear nuevos',
        )

    def handle(self, *args, **options):
        actualizar = options['actualizar']
        
        if not actualizar:
            # Limpiar datos existentes solo si no es actualización
            ActivoFinanciero.objects.all().delete()
            self.stdout.write("Datos anteriores eliminados correctamente")

        # Acciones populares para obtener
        acciones_simbolos = {
            'AAPL': {'empresa': 'Apple Inc.', 'sector': 'Tecnología'},
            'GOOGL': {'empresa': 'Alphabet Inc.', 'sector': 'Tecnología'},
            'MSFT': {'empresa': 'Microsoft Corporation', 'sector': 'Tecnología'},
            'TSLA': {'empresa': 'Tesla Inc.', 'sector': 'Automotriz'},
            'JPM': {'empresa': 'JPMorgan Chase & Co.', 'sector': 'Financiero'},
            'AMZN': {'empresa': 'Amazon.com Inc.', 'sector': 'E-commerce'},
            'NVDA': {'empresa': 'NVIDIA Corporation', 'sector': 'Tecnología'},
            'META': {'empresa': 'Meta Platforms Inc.', 'sector': 'Tecnología'},
        }

        # ETFs populares
        etfs_simbolos = {
            'SPY': {'categoria': 'S&P 500'},
            'QQQ': {'categoria': 'NASDAQ 100'},
            'VTI': {'categoria': 'Mercado Total'},
            'IWM': {'categoria': 'Russell 2000'},
            'VEA': {'categoria': 'Mercados Desarrollados'},
        }

        # Pares de divisas (Yahoo Finance format)
        divisas_simbolos = {
            'USDCOP=X': {'moneda_base': 'USD', 'moneda_cotizacion': 'COP', 'nombre': 'Dólar/Peso Colombiano'},
            'EURUSD=X': {'moneda_base': 'EUR', 'moneda_cotizacion': 'USD', 'nombre': 'Euro/Dólar'},
            'GBPUSD=X': {'moneda_base': 'GBP', 'moneda_cotizacion': 'USD', 'nombre': 'Libra/Dólar'},
            'USDJPY=X': {'moneda_base': 'USD', 'moneda_cotizacion': 'JPY', 'nombre': 'Dólar/Yen'},
        }

        # Procesar Acciones
        self.stdout.write(" Obteniendo datos de acciones")
        for simbolo, info in acciones_simbolos.items():
            try:
                ticker = yf.Ticker(simbolo)
                hist = ticker.history(period="2d")  # Últimos 2 días
                info_ticker = ticker.info
                
                if len(hist) >= 2:
                    precio_actual = Decimal(str(round(hist['Close'].iloc[-1], 4)))
                    precio_anterior = Decimal(str(round(hist['Close'].iloc[-2], 4)))
                    volumen = int(hist['Volume'].iloc[-1])
                    
                    # Obtener información adicional
                    nombre_completo = info_ticker.get('longName', f"{info['empresa']}")
                    mercado = info_ticker.get('exchange', 'NASDAQ')
                    cap_mercado = info_ticker.get('marketCap', 0)
                    
                    # Crear o actualizar ActivoFinanciero
                    activo, created = ActivoFinanciero.objects.update_or_create(
                        simbolo=simbolo,
                        defaults={
                            'nombre': nombre_completo,
                            'tipo': TipoActivo.ACCION,
                            'precio_actual': precio_actual,
                            'precio_anterior': precio_anterior,
                            'volumen': volumen,
                            'mercado': mercado,
                            'activo': True
                        }
                    )
                    
                    # Crear o actualizar Accion
                    Accion.objects.update_or_create(
                        activo_financiero=activo,
                        defaults={
                            'sector': info['sector'],
                            'empresa': info['empresa'],
                            'capitalizacion_mercado': cap_mercado if cap_mercado else None
                        }
                    )
                    
                    action = " Actualizado" if not created else " Creado"
                    self.stdout.write(f"{action}: {simbolo} - ${precio_actual}")
                    
            except Exception as e:
                self.stdout.write(f" Error con {simbolo}: {str(e)}")

        # Procesar ETFs
        self.stdout.write(" Obteniendo datos de ETFs")
        for simbolo, info in etfs_simbolos.items():
            try:
                ticker = yf.Ticker(simbolo)
                hist = ticker.history(period="2d")
                info_ticker = ticker.info
                
                if len(hist) >= 2:
                    precio_actual = Decimal(str(round(hist['Close'].iloc[-1], 4)))
                    precio_anterior = Decimal(str(round(hist['Close'].iloc[-2], 4)))
                    volumen = int(hist['Volume'].iloc[-1])
                    
                    nombre_completo = info_ticker.get('longName', f"ETF {info['categoria']}")
                    mercado = info_ticker.get('exchange', 'NYSE')
                    aum = info_ticker.get('totalAssets', 0)
                    expense_ratio = info_ticker.get('annualReportExpenseRatio', 0)
                    
                    # Crear o actualizar ActivoFinanciero
                    activo, created = ActivoFinanciero.objects.update_or_create(
                        simbolo=simbolo,
                        defaults={
                            'nombre': nombre_completo,
                            'tipo': TipoActivo.ETF,
                            'precio_actual': precio_actual,
                            'precio_anterior': precio_anterior,
                            'volumen': volumen,
                            'mercado': mercado,
                            'activo': True
                        }
                    )
                    
                    # Crear o actualizar ETF
                    ETF.objects.update_or_create(
                        activo_financiero=activo,
                        defaults={
                            'categoria': info['categoria'],
                            'activos_bajo_gestion': aum if aum else None,
                            'ratio_gastos': Decimal(str(expense_ratio * 100)) if expense_ratio else None
                        }
                    )
                    
                    action = " Actualizado" if not created else " Creado"
                    self.stdout.write(f"{action}: {simbolo} - ${precio_actual}")
                    
            except Exception as e:
                self.stdout.write(f" Error con {simbolo}: {str(e)}")

        # Procesar Divisas
        self.stdout.write(" Obteniendo datos de divisas...")
        for simbolo, info in divisas_simbolos.items():
            try:
                ticker = yf.Ticker(simbolo)
                hist = ticker.history(period="2d")
                
                if len(hist) >= 2:
                    precio_actual = Decimal(str(round(hist['Close'].iloc[-1], 6)))
                    precio_anterior = Decimal(str(round(hist['Close'].iloc[-2], 6)))
                    volumen = int(hist['Volume'].iloc[-1]) if hist['Volume'].iloc[-1] > 0 else 1000000
                    
                    # Crear símbolo limpio para mostrar
                    simbolo_display = simbolo.replace('=X', '').replace('USD', '/USD').replace('EUR', 'EUR/').replace('GBP', 'GBP/').replace('JPY', '/JPY')
                    if simbolo_display.startswith('/'):
                        simbolo_display = 'USD' + simbolo_display
                    
                    # Crear o actualizar ActivoFinanciero
                    activo, created = ActivoFinanciero.objects.update_or_create(
                        simbolo=simbolo_display,
                        defaults={
                            'nombre': info['nombre'],
                            'tipo': TipoActivo.DIVISA,
                            'precio_actual': precio_actual,
                            'precio_anterior': precio_anterior,
                            'volumen': volumen,
                            'mercado': 'FX',
                            'activo': True
                        }
                    )
                    
                    # Crear o actualizar Divisa
                    Divisa.objects.update_or_create(
                        activo_financiero=activo,
                        defaults={
                            'moneda_base': info['moneda_base'],
                            'moneda_cotizacion': info['moneda_cotizacion'],
                            'tipo_cambio_referencia': precio_actual
                        }
                    )
                    
                    action = " Actualizado" if not created else " Creado"
                    self.stdout.write(f"{action}: {simbolo_display} - {precio_actual}")
                    
            except Exception as e:
                self.stdout.write(f" Error con {simbolo}: {str(e)}")

        # Estadísticas finales
        total_activos = ActivoFinanciero.objects.count()
        total_acciones = ActivoFinanciero.objects.filter(tipo=TipoActivo.ACCION).count()
        total_etfs = ActivoFinanciero.objects.filter(tipo=TipoActivo.ETF).count()
        total_divisas = ActivoFinanciero.objects.filter(tipo=TipoActivo.DIVISA).count()

        self.stdout.write(
            self.style.SUCCESS(
                f'\n Datos de Yahoo Finance obtenidos exitosamente!\n'
                f'    {total_acciones} Acciones\n'
                f'    {total_etfs} ETFs\n'
                f'    {total_divisas} Divisas\n'
                f'    Total: {total_activos} activos financieros\n'
                f'\n Para actualizar datos: python manage.py obtener_datos_yahoo --actualizar'
            )
        )