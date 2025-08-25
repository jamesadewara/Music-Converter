from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, FileResponse
from django.contrib import messages
from .models import Music
from .forms import MusicUploadForm, MusicConvertForm
import os

def music_list(request):
    music_files = Music.objects.all().order_by('-uploaded_at')
    return render(request, 'music_app/music_list.html', {'music_files': music_files})

def upload_music(request):
    if request.method == 'POST':
        form = MusicUploadForm(request.POST, request.FILES)
        if form.is_valid():
            music = form.save()
            messages.success(request, 'Music file uploaded successfully!')
            return redirect('music_list')
    else:
        form = MusicUploadForm()
    return render(request, 'music_app/upload_music.html', {'form': form})

def convert_music(request, pk):
    music = get_object_or_404(Music, pk=pk)
    
    if request.method == 'POST':
        form = MusicConvertForm(request.POST, instance=music)
        if form.is_valid():
            form.save()
            
            # Convert the audio file
            if music.convert_audio_file():
                messages.success(request, f'Music file converted to {music.target_extension.upper()} successfully!')
            else:
                messages.error(request, 'Error converting music file. Please try again.')
                
            return redirect('music_list')
    else:
        form = MusicConvertForm(instance=music)
    
    return render(request, 'music_app/convert_music.html', {'form': form, 'music': music})

def download_music(request, pk):
    music = get_object_or_404(Music, pk=pk)
    
    if music.converted_file:
        file_path = music.converted_file.path
        filename = os.path.basename(file_path)
        
        response = FileResponse(open(file_path, 'rb'))
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
    else:
        messages.error(request, 'No converted file available. Please convert the file first.')
        return redirect('music_list')

def delete_music(request, pk):
    music = get_object_or_404(Music, pk=pk)
    
    if request.method == 'POST':
        # Delete associated files
        if music.original_file:
            music.original_file.delete()
        if music.converted_file:
            music.converted_file.delete()
        
        # Delete the database record
        music.delete()
        
        messages.success(request, 'Music file deleted successfully!')
        return redirect('music_list')
    
    return render(request, 'music_app/delete_music.html', {'music': music})