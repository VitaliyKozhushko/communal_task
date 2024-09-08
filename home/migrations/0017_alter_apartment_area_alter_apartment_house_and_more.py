# Generated by Django 5.1 on 2024-09-08 16:44

import django.db.models.deletion
import home.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0016_alter_apartment_area'),
    ]

    operations = [
        migrations.AlterField(
            model_name='apartment',
            name='area',
            field=models.DecimalField(decimal_places=2, max_digits=7, validators=[home.validators.validate_area], verbose_name='Площадь'),
        ),
        migrations.AlterField(
            model_name='apartment',
            name='house',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='apartments', to='home.house', verbose_name='Дом'),
        ),
        migrations.AlterField(
            model_name='apartment',
            name='number',
            field=models.IntegerField(blank=True, default=None, null=True, verbose_name='Номер квартиры'),
        ),
    ]
