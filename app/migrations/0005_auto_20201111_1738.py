# Generated by Django 3.1.3 on 2020-11-11 08:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0004_auto_20201109_1644'),
    ]

    operations = [
        migrations.AddField(
            model_name='weather',
            name='area',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='weather',
            name='windspeed',
            field=models.FloatField(null=True),
        ),
    ]
