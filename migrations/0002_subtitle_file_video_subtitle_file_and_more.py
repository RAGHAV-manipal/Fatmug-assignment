# Generated by Django 5.1.1 on 2024-09-15 09:46

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('videos', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='subtitle',
            name='file',
            field=models.FileField(null=True, upload_to='subtitles/'),
        ),
        migrations.AddField(
            model_name='video',
            name='subtitle_file',
            field=models.FileField(blank=True, null=True, upload_to='subtitles/'),
        ),
        migrations.AlterField(
            model_name='subtitle',
            name='video',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='subtitle_set', to='videos.video'),
        ),
    ]
