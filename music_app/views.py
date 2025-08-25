import time
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, FileResponse
from django.contrib import messages
from django.urls import reverse
from .models import Music
from .forms import MusicUploadForm, MusicConvertForm
import os
import re
from django.http import JsonResponse

from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

def music_list(request):
    music_files = Music.objects.all().order_by('-uploaded_at')
    return render(request, 'music_app/music_list.html', {'music_files': music_files})

@csrf_exempt
def iphone_upload_api(request):
    """API endpoint specifically for iPhone uploads"""
    if request.method == 'POST':
        try:
            # Handle different content types
            if 'application/x-www-form-urlencoded' in request.content_type:
                # Standard form data
                title = request.POST.get('title', 'Unknown Title')
                artist = request.POST.get('artist', 'Unknown Artist')
                target_extension = request.POST.get('target_extension', 'mp3')
                file = request.FILES.get('original_file')
            else:
                # Handle raw file upload (iOS sometimes does this)
                title = request.META.get('HTTP_X_TITLE', 'Unknown Title')
                artist = request.META.get('HTTP_X_ARTIST', 'Unknown Artist')
                target_extension = request.META.get('HTTP_X_FORMAT', 'mp3')
                
                # Create file from request body
                from django.core.files.base import ContentFile
                filename = request.META.get('HTTP_X_FILENAME', f'audio_{int(time.time())}.mp3')
                file = ContentFile(request.body, name=filename)
            
            if not file:
                return JsonResponse({'error': 'No file provided'}, status=400)
            
            # Create and save music object
            music = Music(
                title=title,
                artist=artist,
                target_extension=target_extension
            )
            music.original_file.save(file.name, file, save=False)
            music.save()
            
            # Return success response
            return JsonResponse({
                'success': True,
                'message': 'File uploaded successfully',
                'id': music.id,
                'title': music.title
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)

def is_iphone(request):
    """Check if the request is from an iPhone"""
    user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
    return 'iphone' in user_agent or 'ipad' in user_agent or 'ipod' in user_agent

def upload_music(request):
    # Check if this is an iPhone and use a different approach
    if is_iphone(request):
        if request.method == 'POST':
            return handle_iphone_upload(request)
        else:
            # Show iPhone-specific upload form
            return render(request, 'music_app/upload_music_iphone.html', {
                'is_iphone': True
            })
    
    # Original upload logic for other devices
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
        'is_iphone': is_iphone(request)
    }
    return render(request, 'music_app/upload_music.html', context)

def handle_iphone_upload(request):
    """Special handling for iPhone uploads"""
    try:
        # Get the file from request.FILES or request.body for iOS
        if 'original_file' in request.FILES:
            file = request.FILES['original_file']
        else:
            # iOS sometimes sends files differently
            # Try to handle raw file data
            if request.body and len(request.body) > 0:
                # Create a file from the request body
                from io import BytesIO
                from django.core.files.base import ContentFile
                
                # Get filename from headers or generate one
                filename = request.META.get('HTTP_X_FILE_NAME', f'audio_{int(time.time())}.mp3')
                file = ContentFile(request.body, name=filename)
            else:
                messages.error(request, 'No file was received from your device.')
                return redirect('upload_music')
        
        # Get other form data
        title = request.POST.get('title', 'Unknown Title')
        artist = request.POST.get('artist', 'Unknown Artist')
        target_extension = request.POST.get('target_extension', 'mp3')
        
        # Create music object
        music = Music(
            title=title,
            artist=artist,
            target_extension=target_extension
        )
        
        # Save the file
        music.original_file.save(file.name, file, save=False)
        music.save()
        
        messages.success(request, 'Music file uploaded successfully from your iPhone!')
        
        # Try conversion
        try:
            if music.convert_audio_file():
                messages.success(request, f'Music file converted to {music.target_extension.upper()} successfully!')
        except Exception as e:
            messages.warning(request, f'File uploaded but conversion failed: {str(e)}')
            
        return redirect('music_list')
        
    except Exception as e:
        messages.error(request, f'Error uploading from iPhone: {str(e)}')
        return redirect('upload_music')
    
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