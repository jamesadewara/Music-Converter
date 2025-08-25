from django.contrib import admin
from .models import Music
from django.utils.html import format_html
from django.urls import reverse

@admin.register(Music)
class MusicAdmin(admin.ModelAdmin):
    list_display = ('title', 'artist', 'original_extension', 'target_extension', 
                   'uploaded_at', 'converted_at', 'audio_preview', 'download_link')
    list_filter = ('original_extension', 'target_extension', 'uploaded_at')
    search_fields = ('title', 'artist')
    readonly_fields = ('uploaded_at', 'converted_at', 'original_name', 'original_extension', 'audio_preview')
    fieldsets = (
        (None, {
            'fields': ('title', 'artist')
        }),
        ('File Information', {
            'fields': ('original_name', 'original_extension', 'target_extension')
        }),
        ('Audio Files', {
            'fields': ('original_file', 'converted_file', 'audio_preview')
        }),
        ('Timestamps', {
            'fields': ('uploaded_at', 'converted_at'),
            'classes': ('collapse',)
        }),
    )
    
    def audio_preview(self, obj):
        if obj.original_file:
            return format_html(
                '<audio controls><source src="{}" type="audio/{}">Your browser does not support the audio element.</audio>',
                obj.original_file.url,
                obj.original_extension
            )
        return "No audio file"
    audio_preview.short_description = 'Audio Preview'
    
    def download_link(self, obj):
        if obj.converted_file:
            return format_html(
                '<a href="{}" download class="button">Download {}</a>',
                obj.converted_file.url,
                obj.target_extension.upper()
            )
        return "No converted file"
    download_link.short_description = 'Download'