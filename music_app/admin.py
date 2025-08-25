from django.contrib import admin
from .models import Music
from django.utils.html import format_html
from django.urls import reverse, path
from django.http import HttpResponseRedirect
from django.contrib import messages

@admin.register(Music)
class MusicAdmin(admin.ModelAdmin):
    list_display = ('title', 'artist', 'original_extension', 'target_extension', 
                   'conversion_status', 'uploaded_at', 'converted_at', 'audio_preview', 'admin_actions')
    list_filter = ('original_extension', 'target_extension', 'conversion_status', 'uploaded_at')
    search_fields = ('title', 'artist')
    readonly_fields = ('uploaded_at', 'converted_at', 'original_name', 'original_extension', 
                      'audio_preview', 'conversion_status', 'error_message')
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
        ('Conversion Status', {
            'fields': ('conversion_status', 'error_message'),
            'classes': ('collapse',)
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
    
    def admin_actions(self, obj):
        actions = []
        if obj.converted_file and obj.conversion_status == 'success':
            actions.append(
                format_html(
                    '<a href="{}" download class="button">Download {}</a>',
                    obj.converted_file.url,
                    obj.target_extension.upper()
                )
            )
        else:
            actions.append(
                format_html(
                    '<a href="{}" class="button">Convert</a>',
                    reverse('admin:convert_music', args=[obj.pk])
                )
            )
        
        actions.append(
            format_html(
                '<a href="{}" download class="button">Original</a>',
                obj.original_file.url
            )
        )
        
        return format_html(' &nbsp; '.join(actions))
    admin_actions.short_description = 'Actions'
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                '<path:object_id>/convert/',
                self.admin_site.admin_view(self.convert_music),
                name='convert_music',
            ),
        ]
        return custom_urls + urls
    
    def convert_music(self, request, object_id, *args, **kwargs):
        music = Music.objects.get(pk=object_id)
        if music.convert_audio_file():
            self.message_user(request, f'Successfully converted to {music.target_extension.upper()}', messages.SUCCESS)
        else:
            self.message_user(request, f'Conversion failed: {music.error_message}', messages.ERROR)
        
        return HttpResponseRedirect(reverse('admin:music_app_music_change', args=[object_id]))