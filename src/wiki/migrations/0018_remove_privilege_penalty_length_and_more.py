# Generated by Django 5.0.3 on 2024-10-15 04:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wiki', '0017_alter_privilege_penalty_length'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='privilege',
            name='penalty_length',
        ),
        migrations.AlterField(
            model_name='privilege',
            name='penalty_start',
            field=models.DateField(blank=True, null=True),
        ),
    ]
