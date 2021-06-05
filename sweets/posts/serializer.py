from rest_framework import serializers

from .models import *


class CouriersSerializer(serializers.ModelSerializer):
    # courier_id = serializers.IntegerField(read_only=True)
    regions = serializers.ListField(child=serializers.IntegerField(min_value=1), allow_empty=False)
    working_hours = serializers.ListField(child=serializers.CharField(max_length=255), allow_empty=True)

    class Meta:
        model = Couriers
        fields = ['courier_id', 'courier_type', 'regions', 'working_hours']


class OrderSerializer(serializers.ModelSerializer):
    # order_id = models.IntegerField(auto_created=True, primary_key=True)
    weight = serializers.FloatField(min_value=0.01, max_value=50)
    # region = serializers.ListField(child=serializers.IntegerField(min_value=1), allow_empty=False)
    delivery_hours = serializers.ListField(child=serializers.CharField(max_length=255), allow_empty=True)

    class Meta:
        model = Orders
        fields = ['order_id', 'weight', 'region', 'delivery_hours']
