# Generated by Django 5.0.7 on 2024-08-12 17:33

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Driver',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('staff_id', models.CharField(max_length=100, unique=True)),
                ('driver_name', models.CharField(max_length=100)),
                ('duty_card_no', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='DriverImportLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('driver_name', models.CharField(max_length=100)),
                ('staff_id', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='DutyCardTrip',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('duty_card_no', models.CharField(max_length=100)),
                ('route_name', models.CharField(max_length=255)),
                ('trip_type', models.CharField(choices=[('inbound', 'Inbound'), ('outbound', 'Outbound')], max_length=8)),
                ('pick_up_time', models.TimeField()),
                ('drop_off_time', models.TimeField()),
                ('shift_time', models.TimeField()),
            ],
        ),
        migrations.CreateModel(
            name='DriverTrip',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('route_name', models.CharField(max_length=100)),
                ('pick_up_time', models.TimeField()),
                ('drop_off_time', models.TimeField()),
                ('shift_time', models.TimeField()),
                ('head_count', models.IntegerField()),
                ('trip_type', models.CharField(choices=[('inbound', 'Inbound'), ('outbound', 'Outbound')], default='inbound', max_length=8)),
                ('date', models.DateField()),
                ('driver', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='duty.driver')),
            ],
        ),
    ]
