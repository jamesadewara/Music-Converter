from django import forms
from .models import Music
import os

class MusicUploadForm(forms.ModelForm):
    class Meta:
        model = Music
        fields = ['title', 'artist', 'original_file', 'target_extension']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter song title'}),
            'artist': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter artist name'}),
            'original_file': forms.FileInput(attrs={'class': 'form-control', 'accept': 'audio/*'}),
            'target_extension': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'target_extension': 'Convert to format'
        }

    def clean_original_file(self):
        file = self.cleaned_data.get('original_file')
        if not file:
            raise forms.ValidationError('Please select a file to upload.')
        
        # Check file size (max 25MB)
        max_size = 25 * 1024 * 1024  # 25MB
        if file.size > max_size:
            raise forms.ValidationError('File size must be less than 25MB.')
        
        # Check file extension
        valid_extensions = ['.mp3', '.wav', '.ogg', '.flac', '.m4a', '.aac']
        ext = os.path.splitext(file.name)[1].lower()
        if ext not in valid_extensions:
            raise forms.ValidationError('Unsupported file format. Please upload MP3, WAV, OGG, FLAC, M4A, or AAC.')
        
        return file

class MusicConvertForm(forms.ModelForm):
    class Meta:
        model = Music
        fields = ['target_extension']
        widgets = {
            'target_extension': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'target_extension': 'Convert to format'
        }