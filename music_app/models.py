from django.db import models
import os
from django.utils import timezone
from django.core.files import File
from io import BytesIO
from .converters import convert_audio

class Music(models.Model):
    AUDIO_EXTENSIONS = [
        ('mp3', 'MP3'),
        ('wav', 'WAV'),
        ('ogg', 'OGG'),
        ('flac', 'FLAC'),
        ('m4a', 'M4A'),
    ]
    
    original_name = models.CharField(max_length=255)
    title = models.CharField(max_length=200)
    artist = models.CharField(max_length=100, blank=True)
    original_file = models.FileField(upload_to='music/original/')
    converted_file = models.FileField(upload_to='music/converted/', blank=True, null=True)
    original_extension = models.CharField(max_length=10)
    target_extension = models.CharField(max_length=10, choices=AUDIO_EXTENSIONS, default='mp3')
    uploaded_at = models.DateTimeField(default=timezone.now)
    converted_at = models.DateTimeField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.title} - {self.artist}" if self.artist else self.title
    
    def filename(self):
        return os.path.basename(self.original_file.name)
    
    def save(self, *args, **kwargs):
        # Set original name and extension on first save
        if not self.pk:
            self.original_name = self.original_file.name
            self.original_extension = os.path.splitext(self.original_file.name)[1][1:].lower()
            
        super().save(*args, **kwargs)
    
    def convert_audio_file(self):
        """Convert the audio file to the target format"""
        if self.original_file and self.target_extension:
            # Convert the audio
            output_format = self.target_extension
            converted_data = convert_audio(self.original_file.path, output_format)
            
            if converted_data:
                # Generate filename for converted file
                original_name = os.path.splitext(self.original_name)[0]
                converted_filename = f"{original_name}.{output_format}"
                
                # Save converted file
                self.converted_file.save(converted_filename, File(converted_data))
                self.converted_at = timezone.now()
                self.save()
                return True
        return False
    
    class Meta:
        verbose_name_plural = "Music Files"