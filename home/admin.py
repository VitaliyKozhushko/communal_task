from django.contrib import admin
from .models import House, Apartment, Meter, MeterType, Tariff
from django import forms
from django.utils.html import format_html
from django.urls import reverse

class MeterInline(admin.TabularInline):
  model = Meter
  extra = 0


class ApartmentInline(admin.TabularInline):
  model = Apartment
  extra = 0
  readonly_fields = ['view_link']
  fields = ['number', 'area', 'view_link']

  def view_link(self, obj):
    if obj.pk:
      url = reverse('admin:%s_%s_change' % (obj._meta.app_label, obj._meta.model_name),
                    args=[obj.pk])
      return format_html('<a href="{}">{}</a>', url, obj.number)
    return '-'

  view_link.short_description = 'Ссылка'

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
  inlines = [MeterInline]

  def changelist_view(self, request, extra_context=None):
    extra_context = {'title': 'Выберите квартиру чтобы изменить'}
    return super(ApartmentAdmin, self).changelist_view(request, extra_context=extra_context)

@admin.register(Meter)
class MeterAdmin(admin.ModelAdmin):
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


class TariffForm(forms.ModelForm):
  class Meta:
    model = Tariff
    fields = ['meter_type', 'custom_name', 'price_per_unit', 'unit']
    widgets = {
      'meter_type': forms.Select(attrs={'class': 'form-control'}),
      'custom_name': forms.TextInput(attrs={'class': 'form-control'}),
      'unit': forms.TextInput(attrs={'class': 'form-control'}),
      'price_per_unit': forms.NumberInput(attrs={'class': 'form-control'}),
    }

  def clean(self):
    cleaned_data = super().clean()
    meter_type = cleaned_data.get('meter_type')
    custom_name = cleaned_data.get('custom_name')
    unit = cleaned_data.get('unit')

    if not meter_type and not custom_name:
      raise forms.ValidationError("Необходимо выбрать либо тип счетчика, либо ввести название.")

    if meter_type and custom_name:
      raise forms.ValidationError("Нельзя одновременно выбрать тип счётчика и название.")

    if meter_type and unit:
      raise forms.ValidationError("Нельзя вручную устанавливать единицу измерения, если выбран тип счетчика.")

    if custom_name and not unit:
      raise forms.ValidationError("Необходимо указать единицу измерения.")

    if meter_type:
      cleaned_data['unit'] = meter_type.unit

    return cleaned_data

class TariffAdmin(admin.ModelAdmin):
  form = TariffForm
  list_display = ('id', 'name', 'price_per_unit', 'unit')

  def name(self, obj):
    return obj.custom_name or obj.meter_type.name if obj.meter_type else 'No Name'

  name.short_description = 'Название'

  def changelist_view(self, request, extra_context=None):
    extra_context = {'title': 'Выберите тариф чтобы изменить'}
    return super(TariffAdmin, self).changelist_view(request, extra_context=extra_context)

admin.site.register(Tariff, TariffAdmin)
admin.site.register(House, HouseAdmin)