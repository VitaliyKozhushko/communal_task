# Generated by Django 5.1 on 2024-09-08 10:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0014_alter_utilitybill_options_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='CalculationProgress',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('house_id', models.IntegerField()),
                ('year', models.IntegerField()),
                ('month', models.IntegerField()),
                ('status', models.CharField(choices=[('в работе', 'In Progress'), ('готово', 'Completed'), ('ошибка', 'Error')], default='в работе', max_length=50)),
                ('error_message', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
