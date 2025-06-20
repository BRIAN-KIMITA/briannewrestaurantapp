# Generated by Django 5.2.1 on 2025-06-04 21:09

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Reservation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('phone', models.CharField(max_length=20)),
                ('email', models.EmailField(max_length=254)),
                ('guests', models.PositiveIntegerField()),
                ('date', models.DateField()),
                ('time', models.TimeField()),
                ('message', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
