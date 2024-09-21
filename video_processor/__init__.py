# # import ffmpeg

# # input_file = 'path/to/video.mp4'
# # output_file = 'path/to/output_with_subtitles.mp4'
# # srt_file = 'path/to/subtitles.srt'

# # try:
# #     # Burn the subtitles into the video
# #     ffmpeg.input(input_file).output(output_file, vf=f'subtitles={srt_file}', c='copy').run(capture_stdout=True, capture_stderr=True)
# #     print("Subtitles have been successfully burned into the video.")
# # except ffmpeg.Error as e:
# #     print(f"FFmpeg error: {e.stderr.decode()}")
# # except Exception as e:
# #     print(f"An unexpected error occurred: {e}")
# import ffmpeg

# # Path to your video and subtitle files
# input_file = 'path/to/video.mp4'
# output_file = 'path/to/output_with_subtitles.mp4'
# subtitle_file = 'path/to/subtitles.srt'

# try:
#     # Burn subtitles into the video using FFmpeg
#     (
#         ffmpeg
#         .input(input_file)
#         .output(output_file, vf=f"subtitles={subtitle_file}")
#         .run(capture_stdout=True, capture_stderr=True)
#     )
#     print("Subtitles have been successfully burned into the video.")
# except Exception as e:
#     # Print out the error
#     print(f"An error occurred: {e}")

