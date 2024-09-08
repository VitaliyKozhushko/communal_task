from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from django.db import transaction
from home.models import House, Tariff, UtilityBill

def round_decimal(value, places):
    return value.quantize(Decimal(10) ** -places, rounding=ROUND_HALF_UP)

def get_average_consumption(meter, current_period, last_n=3):
    readings = meter.readings or {}
    year, month = map(int, current_period.split('-'))

    consumptions = []

    for _ in range(last_n):
        month -= 1
        if month == 0:
            year -= 1
            month = 12
        period = f"{year}-{str(month).zfill(2)}"

        current_reading = readings.get(period)
        if current_reading is not None:
            if len(consumptions) == 0:
                previous_reading = 0
            else:
                previous_reading = readings.get(f"{year}-{str(month + 1).zfill(2)}", 0)
            consumptions.append(current_reading - previous_reading)

    if consumptions:
        return sum(consumptions) / len(consumptions)
    else:
        return Decimal(0)

@transaction.atomic
def calculate_utility_bills_for_house(house_id, year, month):
    current_period = f"{year}-{str(month).zfill(2)}"
    previous_period = f"{year}-{str(month - 1).zfill(2)}" if month > 1 else f"{year-1}-12"

    house = House.objects.get(id=house_id)

    tariffs_with_meter_type = {tariff.meter_type.id: tariff for tariff in Tariff.objects.filter(meter_type__isnull=False)}
    tariffs_not_meter_type = {tariff.custom_name: tariff for tariff in Tariff.objects.filter(meter_type__isnull=True)}

    result = []

    for apartment in house.apartments.all():
        calc_rent = []  # расчет по тарифам каждой квартиры
        absent_meters = []  # счетчики, у которых нет данных за запрашиваемый период

        # Расчет тарифов без счетчиков, по площади
        for custom_name, tariff in tariffs_not_meter_type.items():
            cost = round_decimal(tariff.price_per_unit * apartment.area, 2)
            calc_rent.append({
                "id": tariff.id,
                "name": custom_name,
                "consumption": float(apartment.area),
                "unit": tariff.unit or "m²",
                "cost": float(cost)
            })

        # Расчет тарифов по счетчикам
        for meter in apartment.meters.all():
            meter_type = meter.meter_type
            tariff = tariffs_with_meter_type.get(meter_type.id)
            if not tariff:
                continue

            readings = meter.readings or {}

            if previous_period not in readings and current_period not in readings:
                absent_meters.append({
                    "id": tariff.id,
                    "name": meter_type.name
                })
                continue

            current_reading = readings.get(current_period)
            previous_reading = readings.get(previous_period, Decimal(0))

            # Если текущих показаний нет, рассчитываем средний расход за последние 3 месяца
            if current_reading is None:
                consumption = get_average_consumption(meter, current_period)
            else:
                consumption = Decimal(current_reading) - Decimal(previous_reading)

            cost = round_decimal(consumption * tariff.price_per_unit, 2)
            calc_rent.append({
                "id": tariff.id,
                "name": meter_type.name,
                "consumption": float(round_decimal(consumption, 2)),
                "unit": meter_type.unit,
                "cost": float(cost)
            })

        result.append({
            "apartment_id": apartment.id,
            "apartment_number": apartment.number,
            "house_id": house.id,
            "address": house.address,
            "date": datetime(year, month, 1),
            "calc_rent": calc_rent,
            "absent_meters": absent_meters
        })

        UtilityBill.objects.update_or_create(
            apartment=apartment,
            month=datetime(year, month, 1),
            defaults={
                'charge': calc_rent
            }
        )

    return result
