# import os
# import subprocess
# from celery import shared_task
# from google.cloud import speech
# from .models import Video

# # Extract audio using ffmpeg
# def extract_audio(video_path):
#     audio_path = f'{video_path}.wav'
#     command = ['ffmpeg', '-i', video_path, '-q:a', '0', '-map', 'a', audio_path]
#     subprocess.run(command, check=True)
#     return audio_path

# # Transcribe audio to subtitles using Google Cloud Speech API
# def transcribe_audio(audio_path):
#     client = speech.SpeechClient()

#     with open(audio_path, "rb") as audio_file:
#         content = audio_file.read()

#     audio = speech.RecognitionAudio(content=content)
#     config = speech.RecognitionConfig(
#         encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
#         sample_rate_hertz=16000,
#         language_code="en-US",
#     )

#     response = client.recognize(config=config, audio=audio)

#     subtitle_lines = []
#     for result in response.results:
#         for alternative in result.alternatives:
#             timestamp = result.result_end_time.seconds
#             subtitle_lines.append((timestamp, alternative.transcript))

#     return subtitle_lines

# # Save subtitles in .srt format
# def save_subtitles_to_srt(subtitle_lines, subtitle_path):
#     with open(subtitle_path, 'w') as f:
#         for i, (timestamp, text) in enumerate(subtitle_lines, start=1):
#             start_time = f"{timestamp//3600:02}:{(timestamp%3600)//60:02}:{timestamp%60:02},000"
#             end_time = f"{(timestamp+2)//3600:02}:{(timestamp+2)%3600//60:02}:{(timestamp+2)%60:02},000"
#             f.write(f"{i}\n{start_time} --> {end_time}\n{text}\n\n")

# # Task to process video and generate subtitles
# @shared_task
# def generate_subtitles(video_id):
#     video = Video.objects.get(id=video_id)
#     video_path = video.file.path

#     audio_path = extract_audio(video_path)
#     subtitle_lines = transcribe_audio(audio_path)
#     subtitle_path = f'{os.path.splitext(video.file.path)[0]}.srt'

#     save_subtitles_to_srt(subtitle_lines, subtitle_path)

#     video.subtitle_file = subtitle_path
#     video.save()

#  #   os.remove(audio_path)  # Cleanup the audio file after processing
