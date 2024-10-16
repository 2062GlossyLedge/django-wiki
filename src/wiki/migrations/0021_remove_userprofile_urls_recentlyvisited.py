# Generated by Django 5.0.3 on 2024-10-16 04:03

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wiki', '0020_remove_privilege_penalty_end_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userprofile',
            name='urls',
        ),
        migrations.CreateModel(
            name='RecentlyVisited',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.URLField(max_length=500)),
                ('title', models.CharField(blank=True, max_length=100, null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recently_visited', to='wiki.userprofile')),
            ],
        ),
    ]
