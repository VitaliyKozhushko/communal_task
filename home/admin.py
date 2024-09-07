from django.contrib import admin
from .models import House, Apartment, WaterMeter
from django import forms

class HouseAdminForm(forms.ModelForm):
  model = House

class WaterMeterInline(admin.TabularInline):
  model = WaterMeter
  extra = 0

class ApartmentInline(admin.TabularInline):
  model = Apartment
  extra = 0
  inlines = [WaterMeterInline]

@admin.register(House)
class HouseAdmin(admin.ModelAdmin):
  form = HouseAdminForm
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