from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, FileResponse
from django.contrib import messages
from django.urls import reverse
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
            try:
                music = form.save()
                messages.success(request, 'Music file uploaded successfully!')
                
                # Try to convert immediately after upload
                try:
                    if music.convert_audio_file():
                        messages.success(request, f'Music file converted to {music.target_extension.upper()} successfully!')
                    else:
                        messages.warning(request, 'File uploaded but conversion failed. You can try converting it manually.')
                except Exception as e:
                    messages.warning(request, f'File uploaded but conversion failed: {str(e)}')
                    
                return redirect('music_list')
                
            except Exception as e:
                messages.error(request, f'Error saving file: {str(e)}')
        else:
            # Add form errors to messages
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = MusicUploadForm()
    
    # Add mobile context
    context = {
        'form': form,
        'is_mobile': getattr(request, 'is_mobile_device', False)
    }
    return render(request, 'music_app/upload_music.html', context)

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
                messages.error(request, f'Error converting music file: {music.error_message}')
                
            return redirect('music_list')
    else:
        form = MusicConvertForm(instance=music)
    
    return render(request, 'music_app/convert_music.html', {'form': form, 'music': music})

def download_music(request, pk):
    music = get_object_or_404(Music, pk=pk)
    
    if music.converted_file and music.conversion_status == 'success':
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

def download_original(request, pk):
    music = get_object_or_404(Music, pk=pk)
    
    if music.original_file:
        file_path = music.original_file.path
        filename = os.path.basename(file_path)
        
        response = FileResponse(open(file_path, 'rb'))
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
    else:
        messages.error(request, 'Original file not found.')
        return redirect('music_list')