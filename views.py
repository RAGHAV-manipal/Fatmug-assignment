import subprocess
import os
import zipfile
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from .forms import VideoForm
from .models import Video, Subtitle
from django.core.exceptions import SuspiciousOperation


def upload_video(request):
    """Handles video upload and processes the video to extract subtitles."""
    if request.method == 'POST':
        form = VideoForm(request.POST, request.FILES)
        if form.is_valid():
            video = form.save()
            try:
                # Process and extract multiple subtitles
                video.process_video()
                # Embed multiple subtitle tracks into the video
                video.embed_subtitles()
            except Exception as e:
                return HttpResponse(f"An error occurred: {str(e)}", status=500)
            return redirect('video_list')
    else:
        form = VideoForm()
    return render(request, 'videos/upload_video.html', {'form': form})


def process_video(video):
    """Extracts subtitles from the uploaded video."""
    video_path = os.path.join(settings.MEDIA_ROOT, video.file.name)

    # Paths for multiple subtitles (e.g., English and French)
    eng_subtitles_path = os.path.join(settings.MEDIA_ROOT, 'subtitles', f'{video.id}/eng_subtitles.srt')
    fre_subtitles_path = os.path.join(settings.MEDIA_ROOT, 'subtitles', f'{video.id}/fre_subtitles.srt')

    if not os.path.isfile(video_path):
        raise FileNotFoundError(f"Video file {video_path} does not exist.")
    
    # Create directories for subtitles if they don't exist
    os.makedirs(os.path.dirname(eng_subtitles_path), exist_ok=True)

    # Command for extracting multiple subtitle streams (assuming 0:s:0 for English and 0:s:1 for French)
    command_eng = [
        'ffmpeg',
        '-i', video_path,
        '-map', '0:s:0',  # English subtitle
        eng_subtitles_path
    ]
    
    command_fre = [
        'ffmpeg',
        '-i', video_path,
        '-map', '0:s:1',  # French subtitle
        fre_subtitles_path
    ]

    try:
        subprocess.run(command_eng, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        subprocess.run(command_fre, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        raise SuspiciousOperation(f"FFmpeg error: {e.stderr.decode()}")

    # Store the paths of the extracted subtitles
    video.subtitle_files = [
        {'language': 'English', 'path': f'subtitles/{video.id}/eng_subtitles.srt'},
        {'language': 'French', 'path': f'subtitles/{video.id}/fre_subtitles.srt'}
    ]
    video.save()


def embed_subtitles(video):
    """Embeds subtitles (English and French) into the video."""
    video_path = os.path.join(settings.MEDIA_ROOT, video.file.name)

    # Paths for multiple subtitles
    eng_subtitles_path = os.path.join(settings.MEDIA_ROOT, 'subtitles', f'{video.id}/eng_subtitles.srt')
    fre_subtitles_path = os.path.join(settings.MEDIA_ROOT, 'subtitles', f'{video.id}/fre_subtitles.srt')

    if not os.path.isfile(video_path) or not os.path.isfile(eng_subtitles_path) or not os.path.isfile(fre_subtitles_path):
        raise FileNotFoundError("Required video or subtitle file not found.")
    
    output_path = os.path.join(settings.MEDIA_ROOT, 'embedded', f'{video.id}_with_subtitles.mkv')
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Command to embed both English and French subtitles into the video
    command = [
        'ffmpeg',
        '-i', video_path,
        '-f', 'srt',
        '-i', eng_subtitles_path,
        '-f', 'srt',
        '-i', fre_subtitles_path,
        '-map', '0:0',  # Video stream
        '-map', '0:1',  # Audio stream
        '-map', '1:0',  # English subtitle
        '-map', '2:0',  # French subtitle
        '-c:v', 'copy',
        '-c:a', 'copy',
        '-c:s', 'srt',
        '-metadata:s:s:0', 'title="English Subtitles"',
        '-metadata:s:s:1', 'title="French Subtitles"',
        '-disposition:s:0', 'default',
        '-disposition:s:1', 'default',
        output_path
    ]

    try:
        subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        raise SuspiciousOperation(f"FFmpeg error: {e.stderr.decode()}")

    video.embedded_file.name = f'embedded/{video.id}_with_subtitles.mkv'
    video.save()


def video_detail(request, id):
    """Displays video details and available subtitles."""
    video = get_object_or_404(Video, id=id)

    # Fetch subtitles related to the video
    subtitles = Subtitle.objects.filter(video=video)

    # Process subtitles (assuming they are named like 'eng_subtitles.srt')
    processed_subtitles = []
    for subtitle in subtitles:
        processed_subtitles.append({
            'language': subtitle.language,
            'path': subtitle.file.url
        })

    timestamp = request.GET.get('timestamp', None)
    
    return render(request, 'videos/video_detail.html', {
        'video': video,
        'subtitles': processed_subtitles,  # Pass the processed subtitles
        'timestamp': timestamp
    })


def download_subtitles(request, video_id):
    """Allows the user to download the extracted subtitles."""
    video = get_object_or_404(Video, id=video_id)

    # Check if subtitle files exist
    if not video.subtitle_files or not video.subtitle_files:
        return HttpResponse("No subtitle files available.", status=404)

    subtitle_paths = [os.path.join(settings.MEDIA_ROOT, sub['path']) for sub in video.subtitle_files]

    # Send the subtitle files as a response
    response = HttpResponse(content_type='application/zip')
    response['Content-Disposition'] = f'attachment; filename=subtitle_files.zip'

    with zipfile.ZipFile(response, 'w') as zip_file:
        for subtitle_path in subtitle_paths:
            if os.path.exists(subtitle_path):
                zip_file.write(subtitle_path, os.path.basename(subtitle_path))

    return response


def download_video_with_subtitles(request, video_id):
    """Allows the user to download the video with embedded subtitles."""
    video = get_object_or_404(Video, id=video_id)

    # Check if the embedded video file exists
    if not video.embedded_file or not video.embedded_file.name:
        return HttpResponse("No video file with embedded subtitles available.", status=404)

    video_path = os.path.join(settings.MEDIA_ROOT, video.embedded_file.name)

    if not os.path.exists(video_path):
        return HttpResponse("Video file not found.", status=404)

    # Send the video file as a response
    with open(video_path, 'rb') as video_file:
        response = HttpResponse(video_file.read(), content_type='video/mkv')
        response['Content-Disposition'] = f'attachment; filename={os.path.basename(video_path)}'
        return response


def search_subtitles(request):
    """Searches subtitles for a given query in a specific video."""
    query = request.GET.get('q', '').strip()
    video_id = request.GET.get('video_id')

    results = []
    video = None
    
    if query and video_id:
        video = get_object_or_404(Video, id=video_id)

        # Iterate through the subtitle file paths
        subtitle_paths = video.subtitle_files  # Ensure this is a list of strings

        for subtitle_path in subtitle_paths:
            full_path = os.path.join(settings.MEDIA_ROOT, subtitle_path)  # Create the full path
            if os.path.isfile(full_path):
                with open(full_path, 'r', encoding='utf-8') as subtitle_file:
                    for line in subtitle_file:
                        if query.lower() in line.lower():  # Case-insensitive search
                            timestamp = extract_start_timestamp(line)
                            if timestamp:
                                results.append({'video': video, 'text': line.strip(), 'timestamp': timestamp})

    return render(request, 'videos/search_results.html', {
        'results': results,
        'query': query,
        'video': video
    })


def extract_start_timestamp(line):
    # Extract the start timestamp from the line, e.g., "00:00:05,000 --> 00:00:10,000"
    if line:
        parts = line.split(' --> ')
        if parts:
            return parts[0].strip()  # Return the start timestamp
    return None


def video_list(request):
    """Displays a list of all uploaded videos."""
    videos = Video.objects.all()  # Fetch all video records from the database
    return render(request, 'videos/video_list.html', {'videos': videos})