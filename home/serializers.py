from rest_framework import serializers
from .models import House, Apartment, Meter, MeterType, Tariff

class MeterTypeSerializer(serializers.ModelSerializer):
  class Meta:
    model = MeterType
    fields = ['id', 'name', 'unit']

class MeterSerializer(serializers.ModelSerializer):
  meter_type = MeterTypeSerializer(read_only=True)

  class Meta:
    model = Meter
    fields = ['id', 'meter_number', 'meter_type', 'readings']

class ApartmentSerializer(serializers.ModelSerializer):
  meters = MeterSerializer(many=True, read_only=True)

  class Meta:
    model = Apartment
    fields = ['id', 'number', 'area', 'meters']

class HouseListSerializer(serializers.ModelSerializer):
  class Meta:
    model = House
    fields = ['id', 'address']

class HouseSerializer(serializers.ModelSerializer):
  apartments = ApartmentSerializer(many=True, read_only=True)

  class Meta:
    model = House
    fields = ['id', 'address', 'apartments']

class TariffSerializer(serializers.ModelSerializer):
  meter_type = MeterTypeSerializer(read_only=True)

  class Meta:
    model = Tariff
    fields = ['id', 'meter_type', 'custom_name', 'unit', 'price_per_unit']
