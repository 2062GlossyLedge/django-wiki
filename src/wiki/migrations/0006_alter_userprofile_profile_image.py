# Generated by Django 5.0.3 on 2024-09-10 14:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wiki', '0005_alter_userprofile_profile_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='profile_image',
            field=models.ImageField(null=True, upload_to='profile_pics/'),
        ),
    ]
