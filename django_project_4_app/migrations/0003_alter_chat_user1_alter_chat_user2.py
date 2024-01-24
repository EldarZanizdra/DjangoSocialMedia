# Generated by Django 5.0.1 on 2024-01-23 17:00

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('django_project_4_app', '0002_like_user_alter_like_comment_alter_like_post'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chat',
            name='user1',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user1_chats', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='chat',
            name='user2',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user2_chats', to=settings.AUTH_USER_MODEL),
        ),
    ]
