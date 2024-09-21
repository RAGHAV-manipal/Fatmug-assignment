from django.db import models
from django.conf import settings
import os
import subprocess
import ffmpeg
from django.core.exceptions import SuspiciousOperation


class Video(models.Model):
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to='videos/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    subtitle_files= models.JSONField(default=list)  # Store multiple subtitle paths
    embedded_file = models.FileField(upload_to='embedded/', null=True, blank=True)

    def _str_(self):
        return self.title

    def process_video(self):
        video_path = os.path.join(settings.MEDIA_ROOT, self.file.name)
        subtitles_dir = os.path.join(settings.MEDIA_ROOT, f'subtitles/{self.id}/')
        os.makedirs(subtitles_dir, exist_ok=True)

        languages = ['eng', 'spa', 'fre']
        for idx, lang in enumerate(languages):
            subtitles_path = os.path.join(subtitles_dir, f'{lang}_subtitles.srt')

            try:
                ffmpeg.input(video_path).output(subtitles_path, **{'map': f'0:s:{idx}'}).run()
            except ffmpeg.Error as e:
                print(f"FFmpeg error: {e}")
                raise

            self.subtitle_files.append(f'subtitles/{self.id}/{lang}_subtitles.srt')
        self.save()

    def embed_subtitles(self):
        video_path = os.path.join(settings.MEDIA_ROOT, self.file.name)
        subtitles_paths = [os.path.join(settings.MEDIA_ROOT, sub) for sub in self.subtitle_files]

        output_path = os.path.join(settings.MEDIA_ROOT, f'embedded/{self.id}_with_subtitles.mkv')
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        command = ['ffmpeg', '-i', video_path]
        for sub_path in subtitles_paths:
            command.extend(['-f', 'srt', '-i', sub_path])

        command.extend([
            '-map', '0:0',
            '-map', '0:1',
        ])
        for idx in range(len(subtitles_paths)):
            command.extend(['-map', f'{idx + 1}:0'])

        command.extend([
            '-c:v', 'copy', '-c:a', 'copy',
            '-c:s', 'srt',
            '-disposition:s:0', 'default',
            output_path
        ])

        try:
            subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except subprocess.CalledProcessError as e:
            raise SuspiciousOperation(f"FFmpeg error: {e.stderr.decode()}")

        self.embedded_file.name = f'embedded/{self.id}_with_subtitles.mkv'
        self.save()


class Subtitle(models.Model):
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name='subtitles')
    language = models.CharField(max_length=100)
    file = models.FileField(upload_to='subtitles/', default='default_subtitle.srt')  # Default value

    def _str_(self):
        return f"{self.language} subtitles for {self.video.title}"