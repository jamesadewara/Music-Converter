from django import forms
from .models import Music

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