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

class MeterByHouseSerializer(serializers.ModelSerializer):
  meter_type = serializers.PrimaryKeyRelatedField(queryset=MeterType.objects.all())
  apartment_id = serializers.SerializerMethodField()

  class Meta:
    model = Meter
    fields = ['id', 'apartment_id', 'meter_number', 'meter_type', 'readings']

  def get_apartment_id(self, obj):
    return obj.apartment.id

  def update(self, instance, validated_data):
    meter_type = validated_data.pop('meter_type', None)

    instance.meter_number = validated_data.get('meter_number', instance.meter_number)
    instance.readings = validated_data.get('readings', instance.readings)

    if meter_type:
      instance.meter_type = meter_type

    instance.save()
    return instance

class ApartmentSerializer(serializers.ModelSerializer):
    meters = MeterSerializer(many=True, read_only=True)

    class Meta:
      model = Apartment
      fields = ['id', 'number', 'area', 'meters']


class ApartmentWithHouseSerializer(serializers.ModelSerializer):
  house_id = serializers.SerializerMethodField()
  meters = MeterSerializer(many=True, read_only=True)

  class Meta:
    model = Apartment
    fields = ['id', 'number', 'area', 'house_id', 'meters']

  def get_house_id(self, obj):
    return obj.house.id

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
