# Generated by Django 5.0.3 on 2024-11-15 18:57

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wiki', '0007_discussionboard_delete_discussionboards'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='DiscussionReport',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('article_id', models.IntegerField()),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('post_id', models.IntegerField()),
                ('report_type', models.CharField(max_length=255)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='discussion_report', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
