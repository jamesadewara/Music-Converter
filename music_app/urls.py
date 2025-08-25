from django.urls import path
from . import views

urlpatterns = [
    path('', views.music_list, name='music_list'),
    path('upload/', views.upload_music, name='upload_music'),
    path('convert/<int:pk>/', views.convert_music, name='convert_music'),
    path('download/<int:pk>/', views.download_music, name='download_music'),
    path('download-original/<int:pk>/', views.download_original, name='download_original'),
    path('delete/<int:pk>/', views.delete_music, name='delete_music'),
    path('api/iphone-upload/', views.iphone_upload_api, name='iphone_upload_api'),
]