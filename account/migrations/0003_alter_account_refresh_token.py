# Generated by Django 3.2.6 on 2024-04-16 07:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0002_account_refresh_token'),
    ]

    operations = [
        migrations.AlterField(
            model_name='account',
            name='refresh_token',
            field=models.CharField(max_length=100),
        ),
    ]
