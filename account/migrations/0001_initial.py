# Generated by Django 3.2.12 on 2024-04-20 14:35

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Account',
            fields=[
                ('account_id', models.AutoField(primary_key=True, serialize=False)),
                ('client_id', models.CharField(max_length=100, unique=True)),
                ('client_secret', models.CharField(max_length=100, unique=True)),
                ('account_name', models.CharField(max_length=100)),
                ('user_id', models.IntegerField(default=0)),
                ('access_token', models.CharField(max_length=100)),
                ('refresh_token', models.CharField(max_length=100)),
                ('account_user_id', models.IntegerField(default=0)),
            ],
        ),
    ]