# Generated by Django 5.1 on 2024-09-07 09:55
from django.db import migrations

def create_default_meter_types(apps, schema_editor):
    MeterType = apps.get_model('home', 'MeterType')
    if not MeterType.objects.exists():
        MeterType.objects.create(name='ХВС', unit='м3')
        MeterType.objects.create(name='Эл-во', unit='кВт/ч')

class Migration(migrations.Migration):
    dependencies = [
        ('home', '0005_alter_watermeter_readings'),
    ]

    operations = [
        migrations.RunPython(create_default_meter_types),
    ]
