# Generated by Django 5.1 on 2024-09-07 10:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0008_rename_watermeter_meter'),
    ]

    operations = [
        migrations.RenameField(
            model_name='utilitybill',
            old_name='water_charge',
            new_name='charge',
        ),
    ]
