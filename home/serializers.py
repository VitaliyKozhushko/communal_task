from rest_framework import serializers
from .models import House, Apartment, Meter, MeterType, Tariff
from rest_framework.exceptions import ValidationError
from datetime import datetime
from dateutil.relativedelta import relativedelta

class MeterTypeSerializer(serializers.ModelSerializer):
  class Meta:
    model = MeterType
    fields = ['id', 'name', 'unit']

class MeterSerializer(serializers.ModelSerializer):
  meter_type = MeterTypeSerializer(read_only=True)
  apartment = serializers.PrimaryKeyRelatedField(queryset=Apartment.objects.all())

  class Meta:
    model = Meter
    fields = ['id', 'meter_number', 'meter_type', 'readings', 'apartment']

  def to_representation(self, instance):
    representation = super().to_representation(instance)
    request = self.context.get('request')
    if request and request.method != 'POST':
      representation.pop('apartment', None)
    return representation

  def validate_readings(self, value):
    if value:
      if len(value) != 1:
        raise serializers.ValidationError("Можно передать показания только за один месяц.")

      current_month = datetime.now().strftime('%Y-%m')
      previous_month = (datetime.now() - relativedelta(months=1)).strftime('%Y-%m')

      for month, reading in value.items():
        # Проверка на отрицательное значение
        if float(reading) < 0:
          raise serializers.ValidationError(f"Показания за {month} не могут быть отрицательными.")

        # Проверка на месяц (текущий / предыдущий)
        if month != current_month and month != previous_month:
          raise serializers.ValidationError(
            f"Показания могут быть только за текущий ({current_month}) или предыдущий месяц ({previous_month})."
          )

    return value

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
    new_readings = validated_data.get('readings')

    if new_readings is not None:
      if len(new_readings) != 1:
        raise ValidationError("Передаваться могут показания только за один месяц за раз.")

      new_month, new_value = list(new_readings.items())[0]

      if float(new_value) < 0:
        raise ValidationError("Показания не могут быть отрицательными.")

      current_month = datetime.now().strftime('%Y-%m')
      previous_month = (datetime.now() - relativedelta(months=1)).strftime('%Y-%m')

      # Показаний нет, месяц текущий или предыдущий
      if not instance.readings:
        if new_month != current_month and new_month != previous_month:
          raise ValidationError(
            f"Показания могут быть только за текущий ({current_month}) или предыдущий месяц ({previous_month}).")
      else:
        # Показания есть, новый месяц не меньше самого раннего
        earliest_month = min(instance.readings.keys())
        if new_month < earliest_month:
          raise ValidationError(
            f"Новый месяц ({new_month}) не может быть меньше самого раннего ({earliest_month}) в существующих показаниях.")

      # Наличие показаний за указанный месяц
      if new_month in instance.readings:
        raise ValidationError(f"Показания за {new_month} уже существуют.")

      instance.readings[new_month] = new_value

    instance.meter_number = validated_data.get('meter_number', instance.meter_number)

    if meter_type:
      instance.meter_type = meter_type

    instance.save()
    return instance

class ApartmentSerializer(serializers.ModelSerializer):
    meters = MeterSerializer(many=True, read_only=True)
    house = serializers.PrimaryKeyRelatedField(queryset=House.objects.all())

    class Meta:
      model = Apartment
      fields = ['id', 'house', 'number', 'area', 'meters']

    def to_representation(self, instance):
      representation = super().to_representation(instance)
      request = self.context.get('request')
      if request and request.method != 'POST':
        representation.pop('house', None)
      return representation


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
