# Generated by Django 4.2.20 on 2025-04-17 07:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('apesf', '0006_partner_description'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='partner',
            name='description',
        ),
    ]
