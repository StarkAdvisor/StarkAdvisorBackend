# market/serializers.py
from rest_framework import serializers

class MetricDTOSerializer(serializers.Serializer):
    ticker = serializers.CharField()
    name = serializers.CharField()
    price = serializers.FloatField(allow_null=True)
    daily_change = serializers.FloatField(allow_null=True)
    extra_metrics = serializers.DictField()
