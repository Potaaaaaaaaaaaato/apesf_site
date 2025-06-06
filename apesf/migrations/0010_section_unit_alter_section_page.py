# Generated by Django 4.2.20 on 2025-04-23 07:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('apesf', '0009_remove_partner_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='section',
            name='unit',
            field=models.CharField(blank=True, choices=[('marmousets', 'Marmousets'), ('angelus', 'Angélus'), ('service_externalise', 'Service externalisé'), ('', 'Aucune unité')], default='', max_length=50, verbose_name='Unité associée'),
        ),
        migrations.AlterField(
            model_name='section',
            name='page',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='sections', to='apesf.pagecontent', verbose_name='Page associée'),
        ),
    ]
