from rest_framework import serializers
from datetime import datetime


class TimeSeriesDTOSerializer(serializers.Serializer):
    """
    Serializer for TimeSeriesDTO objects.
    Represents a simplified time series entry with only ticker, timestamp, and close price.
    """
    ticker = serializers.CharField()
    timestamp = serializers.DateTimeField()
    close_price = serializers.FloatField()
