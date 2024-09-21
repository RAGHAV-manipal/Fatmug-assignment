# Generated by Django 5.1.1 on 2024-09-20 09:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('videos', '0003_video_embedded_file_alter_subtitle_file_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='subtitle',
            name='text',
        ),
        migrations.RemoveField(
            model_name='subtitle',
            name='timestamp',
        ),
        migrations.RemoveField(
            model_name='video',
            name='subtitle_file',
        ),
        migrations.AddField(
            model_name='subtitle',
            name='language',
            field=models.CharField(default='en', max_length=10),
        ),
    ]
