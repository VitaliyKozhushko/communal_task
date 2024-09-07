from django.db import models

class House(models.Model):
    address = models.CharField(max_length=255, unique=True, verbose_name='Адрес')

    class Meta:
        verbose_name = 'Дом'
        verbose_name_plural = 'Доступные дома'

    def __str__(self):
        return self.address


class Tariff(models.Model):
    name = models.CharField(max_length=100)
    price_per_unit = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.name}: {self.price_per_unit} per unit"


class Apartment(models.Model):
    house = models.ForeignKey(House, related_name='apartments', on_delete=models.CASCADE)
    number = models.IntegerField(default=None, blank=True, null=True)
    area = models.DecimalField(max_digits=7, decimal_places=2)

    class Meta:
      verbose_name = 'Квартира'
      verbose_name_plural = 'Доступные квартиры'

    def __str__(self):
        return f"Apartment {self.id} in {self.house}"


class WaterMeter(models.Model):
    apartment = models.ForeignKey(Apartment, related_name='meters', on_delete=models.CASCADE)
    readings = models.JSONField()

    def __str__(self):
        return f"Meter {self.id} in {self.apartment}"


class UtilityBill(models.Model):
    apartment = models.ForeignKey(Apartment, related_name='bills', on_delete=models.CASCADE)
    month = models.DateField()
    water_charge = models.DecimalField(max_digits=10, decimal_places=2)
    maintenance_charge = models.DecimalField(max_digits=10, decimal_places=2)

    def total_charge(self):
        return self.water_charge + self.maintenance_charge

    def __str__(self):
        return f"Bill for {self.apartment} for {self.month}"
