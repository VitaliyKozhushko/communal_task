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
    return f"Apartment {self.number} in {self.house}"

class MeterType(models.Model):
  name = models.CharField(max_length=100, verbose_name='Тип счётчика')
  unit = models.CharField(max_length=50, verbose_name='Единица измерения')

  class Meta:
    verbose_name = 'Тип счётчика'
    verbose_name_plural = 'Типы счётчиков'

  def __str__(self):
    return self.name

class Meter(models.Model):
  apartment = models.ForeignKey(Apartment, related_name='meters', on_delete=models.CASCADE)
  meter_number = models.CharField(max_length=50, verbose_name='Номер счётчика', default='Unknown')
  meter_type = models.ForeignKey(MeterType, related_name='meters', on_delete=models.PROTECT,
                                 verbose_name='Тип счётчика', default=1)
  readings = models.JSONField(null=True, blank=True, verbose_name='Показания')

  class Meta:
    verbose_name = 'Счётчик'
    verbose_name_plural = 'Счётчики'

  def __str__(self):
    return f"Meter {self.id} in {self.apartment}"

class UtilityBill(models.Model):
  apartment = models.ForeignKey(Apartment, related_name='bills', on_delete=models.CASCADE)
  month = models.DateField()
  charge = models.DecimalField(max_digits=10, decimal_places=2)
  maintenance_charge = models.DecimalField(max_digits=10, decimal_places=2)

  def total_charge(self):
    return self.charge + self.maintenance_charge

  def __str__(self):
    return f"Bill for {self.apartment} for {self.month}"
