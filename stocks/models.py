from django.db import models


class FinancialAsset(models.Model):
    name = models.CharField(max_length=100)
    ticker = models.CharField(max_length=10, unique=True)  # Example: AAPL, EURUSD=X
    asset_type = models.CharField(
        max_length=20,
        choices=[
            ('stock', 'Stock'),
            ('etf', 'ETF'),
            ('currency', 'Currency')
        ]
    )

    def __str__(self):
        return f"{self.name} ({self.ticker})"


class TimeSeries(models.Model):
    asset = models.ForeignKey(FinancialAsset, on_delete=models.CASCADE, related_name="time_series")
    date = models.DateField()
    open_price = models.DecimalField(max_digits=20, decimal_places=6)
    high_price = models.DecimalField(max_digits=20, decimal_places=6)
    low_price = models.DecimalField(max_digits=20, decimal_places=6)
    close_price = models.DecimalField(max_digits=20, decimal_places=6)
    volume = models.BigIntegerField()

    class Meta:
        unique_together = ('asset', 'date')  # Prevent duplicates
        ordering = ['-date']  # Most recent first

    def __str__(self):
        return f"{self.asset.ticker} - {self.date}"
    
    

class StockMetrics(models.Model):
    """
    Stores the latest metrics for an Stock.
    Each Stock will have only one entry that is updated regularly.
    """
    asset = models.OneToOneField(
        'FinancialAsset',
        on_delete=models.CASCADE,
        related_name="metrics"
    )
    price = models.FloatField(null=True, blank=True)
    daily_change = models.FloatField(null=True, blank=True)       # Daily % change
    change_5d_percent = models.FloatField(null=True, blank=True)          # 5 days % change
    change_1m_percent = models.FloatField(null=True, blank=True)          # 1 month % change
    change_ytd_percent = models.FloatField(null=True, blank=True)         # Year-to-date % change
    change_5y_percent = models.FloatField(null=True, blank=True)          # 5 years % change
    high = models.FloatField(null=True, blank=True)               # Today's high
    low = models.FloatField(null=True, blank=True)                # Today's low
    volume = models.BigIntegerField(null=True, blank=True)        # Trading volume
    pe_ratio = models.FloatField(null=True, blank=True)           # Price-to-Earnings ratio
    eps = models.FloatField(null=True, blank=True)                # Earnings per Share
    dividend_yield = models.FloatField(null=True, blank=True)     # Dividend Yield
    market_cap = models.BigIntegerField(null=True, blank=True)    # Market Capitalization
    sector = models.CharField(max_length=100, null=True, blank=True)

    updated_at = models.DateTimeField(auto_now=True)              # Last time updated

    def __str__(self):
        return f"Metrics for {self.asset.ticker}"



class ETFMetrics(models.Model):
    """
    Stores the latest metrics for an ETF.
    Each ETF will have only one entry that is updated regularly.
    """
    asset = models.OneToOneField(FinancialAsset, on_delete=models.CASCADE, related_name="etf_metrics")

    # Core metrics
    current_price = models.FloatField(null=True, blank=True)  # Last market price
    daily_change_percent = models.FloatField(null=True, blank=True)  # % change in 1 day
    change_5d_percent = models.FloatField(null=True, blank=True)  # % change in 5 days
    change_1m_percent = models.FloatField(null=True, blank=True)  # % change in 1 month
    change_ytd_percent = models.FloatField(null=True, blank=True)  # % change year-to-date
    change_5y_percent = models.FloatField(null=True, blank=True)  # % change in 5 years

    # Price range
    day_high = models.FloatField(null=True, blank=True)  # Highest price today
    day_low = models.FloatField(null=True, blank=True)  # Lowest price today
    week52_high = models.FloatField(null=True, blank=True)  # 52-week high
    week52_low = models.FloatField(null=True, blank=True)  # 52-week low

    # Financial indicators
    volume = models.BigIntegerField(null=True, blank=True)  # Trading volume
    dividend_yield = models.FloatField(null=True, blank=True)  # Dividend yield (%)
    market_cap = models.BigIntegerField(null=True, blank=True)  # Market capitalization
    nav = models.FloatField(null=True, blank=True)  # Net Asset Value (if available)

    last_updated = models.DateTimeField(auto_now=True)  # Auto-updated timestamp

    def __str__(self):
        return f"ETF Metrics for {self.asset.ticker}"
    

 
class CurrencyMetrics(models.Model):
    asset = models.OneToOneField(FinancialAsset, on_delete=models.CASCADE, related_name="currency_metrics")

    # Current price and variation metrics
    exchange_rate = models.FloatField(null=True, blank=True)
    daily_change_percent = models.FloatField(null=True, blank=True)
    change_5d_percent = models.FloatField(null=True, blank=True)
    change_1m_percent = models.FloatField(null=True, blank=True)
    change_ytd_percent = models.FloatField(null=True, blank=True)
    change_5y_percent = models.FloatField(null=True, blank=True)

    # Daily and historical highs/lows
    day_high = models.FloatField(null=True, blank=True)
    day_low = models.FloatField(null=True, blank=True)
    fifty_two_week_high = models.FloatField(null=True, blank=True)
    fifty_two_week_low = models.FloatField(null=True, blank=True)

    # Forex-specific metrics
    bid = models.FloatField(null=True, blank=True)  # Best buying price
    ask = models.FloatField(null=True, blank=True)  # Best selling price

    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Currency Metrics - {self.asset.ticker}"
