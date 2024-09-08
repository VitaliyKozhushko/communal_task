# Generated by Django 5.1 on 2024-09-08 08:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0013_change_numeric_to_string'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='utilitybill',
            options={'verbose_name': 'Квитанция', 'verbose_name_plural': 'Квитанции'},
        ),
        migrations.RemoveField(
            model_name='utilitybill',
            name='maintenance_charge',
        ),
        migrations.AlterField(
            model_name='utilitybill',
            name='charge',
            field=models.JSONField(),
        ),
    ]
