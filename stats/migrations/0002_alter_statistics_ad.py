# Generated by Django 4.2.7 on 2024-04-19 09:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ads', '0001_initial'),
        ('stats', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='statistics',
            name='ad',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, to='ads.ad'),
        ),
    ]
