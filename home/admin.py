from django.contrib import admin
from .models import House, Apartment, WaterMeter, MeterType
from django import forms

class WaterMeterInline(admin.TabularInline):
  model = WaterMeter
  extra = 0

class ApartmentInline(admin.TabularInline):
  model = Apartment
  extra = 0
  inlines = [WaterMeterInline]

@admin.register(House)
class HouseAdmin(admin.ModelAdmin):
  list_display = ('address',)
  inlines = [ApartmentInline]

  def changelist_view(self, request, extra_context=None):
    extra_context = {'title': 'Выберите дом чтобы изменить'}
    return super(HouseAdmin, self).changelist_view(request, extra_context=extra_context)

@admin.register(Apartment)
class ApartmentAdmin(admin.ModelAdmin):
  list_display = ['number', 'area', 'house']
  list_filter = ['house']
  ordering = ['house', 'area']
  inlines = [WaterMeterInline]

  def changelist_view(self, request, extra_context=None):
    extra_context = {'title': 'Выберите квартиру чтобы изменить'}
    return super(ApartmentAdmin, self).changelist_view(request, extra_context=extra_context)

@admin.register(WaterMeter)
class WaterMeterAdmin(admin.ModelAdmin):
  list_display = ('id', 'meter_number', 'meter_type', 'readings', 'get_apartment_number', 'get_house')
  list_filter = ['apartment', 'apartment__house']

  def get_apartment_number(self, obj):
    return obj.apartment.number

  get_apartment_number.short_description = 'Номер квартиры'

  def get_house(self, obj):
    return obj.apartment.house.address

  get_house.short_description = 'Дом'

@admin.register(MeterType)
class MeterTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'unit')