# Generated by Django 4.2.20 on 2025-04-22 11:51

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('apesf', '0008_partner_description'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='partner',
            name='description',
        ),
    ]
