import subprocess

def convert_video(input_file, output_file):
    command = [
        'ffmpeg',
        '-i', input_file,
        '-c:v', 'libvpx',  # Use VP8 codec for video
        '-b:v', '1M',  # Set video bitrate
        '-c:a', 'libvorbis',  # Use Vorbis codec for audio
        '-b:a', '192k',  # Set audio bitrate
        '-map', '0:v',  # Map video stream
        '-map', '0:a',  # Map audio stream
        '-map', '0:s',  # Map subtitle stream if available
        output_file
    ]

    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    if result.returncode != 0:
        print(f"Error: {result.stderr.decode()}")
    else:
        print("Conversion successful!")

# Example usage
if __name__ == "__main__":
    convert_video('C:\\Users\\lenovo\\Desktop\\Fatmug\\video_processor\\media\\videos\\test1_hqPwCq9.mkv', 'output.webm')
