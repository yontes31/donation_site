# Generated by Django 5.1.5 on 2025-01-23 12:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('locations', '0002_location_posts'),
    ]

    operations = [
        migrations.AddField(
            model_name='donationlocation',
            name='latitude',
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name='donationlocation',
            name='longitude',
            field=models.FloatField(null=True),
        ),
    ]
