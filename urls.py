from django.urls import path
from . import views


urlpatterns = [
    # URL for uploading videos
    path('upload/', views.upload_video, name='upload_video'),
    
    # URL to list all uploaded videos
    path('', views.video_list, name='video_list'),
    
    # URL to view details of a specific video
    path('video/<int:id>/', views.video_detail, name='video_detail'),
    
    # URL for searching subtitles
    path('search/', views.search_subtitles, name='search_subtitles'),
]
