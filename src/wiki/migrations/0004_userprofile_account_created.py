# Generated by Django 5.0.3 on 2024-11-09 21:35

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wiki', '0003_userbadge'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='account_created',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
