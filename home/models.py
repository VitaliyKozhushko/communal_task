from django.db import models
from .validators import validate_area

class House(models.Model):
  address = models.CharField(max_length=255, unique=True, verbose_name='Адрес')

  class Meta:
    verbose_name = 'Дом'
    verbose_name_plural = 'Доступные дома'

  def __str__(self):
    return self.address

class Apartment(models.Model):
  house = models.ForeignKey(House, related_name='apartments', on_delete=models.CASCADE)
  number = models.IntegerField(default=None, blank=True, null=True)
  area = models.DecimalField(max_digits=7, decimal_places=2, validators=[validate_area])

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
  charge = models.JSONField()

  class Meta:
    verbose_name = 'Квитанция'
    verbose_name_plural = 'Квитанции'

  def __str__(self):
    return f"Bill for {self.apartment} for {self.month}"

class Tariff(models.Model):
  meter_type = models.ForeignKey(MeterType, null=True, blank=True, on_delete=models.SET_NULL, related_name='tariffs',
                                 verbose_name='Тип счётчика')
  custom_name = models.CharField(max_length=100, blank=True, null=True, verbose_name='Название тарифа')
  unit = models.CharField(max_length=50, blank=True, verbose_name='Единица измерения')
  price_per_unit = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена за единицу')

  class Meta:
    verbose_name = 'Тариф'
    verbose_name_plural = 'Тарифы'

  def __str__(self):
    return f"{self.custom_name or self.meter_type.name}: {self.price_per_unit} per unit" if self.custom_name or self.meter_type else 'No Name'

class CalculationProgress(models.Model):
  house_id = models.IntegerField()
  year = models.IntegerField()
  month = models.IntegerField()
  status = models.CharField(max_length=50,
                            choices=[('в работе', 'In Progress'), ('готово', 'Completed'), ('ошибка', 'Error')],
                            default='в работе')
  error_message = models.TextField(blank=True, null=True)
  created_at = models.DateTimeField(auto_now_add=True)

  def __str__(self):
    return f"Calculation for house {self.house_id} ({self.year}-{self.month}): {self.status}"