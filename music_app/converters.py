import os
import tempfile
from io import BytesIO
import subprocess
import logging

# Set up logging
logger = logging.getLogger(__name__)

def convert_audio_with_ffmpeg(input_path, output_format):
    """
    Convert audio file to the specified format using FFmpeg directly
    """
    try:
        # Validate input file exists
        if not os.path.exists(input_path):
            logger.error(f"Input file does not exist: {input_path}")
            return None
        
        # Create a temporary file to store the converted audio
        with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{output_format}') as tmp:
            output_path = tmp.name
            
        # Build FFmpeg command based on output format
        ffmpeg_cmd = [
            'ffmpeg',
            '-y',  # Overwrite output file without asking
            '-i', input_path,
        ]
        
        # Add format-specific parameters
        if output_format == 'mp3':
            ffmpeg_cmd.extend([
                '-codec:a', 'libmp3lame',
                '-qscale:a', '2',  # Good quality (0-9, 0 is best)
            ])
        elif output_format == 'wav':
            ffmpeg_cmd.extend([
                '-codec:a', 'pcm_s16le',
            ])
        elif output_format == 'ogg':
            ffmpeg_cmd.extend([
                '-codec:a', 'libvorbis',
                '-qscale:a', '5',  # Good quality (0-10, 10 is best)
            ])
        elif output_format == 'flac':
            ffmpeg_cmd.extend([
                '-codec:a', 'flac',
                '-compression_level', '5',  # Medium compression (0-12, 12 is max)
            ])
        elif output_format in ['m4a', 'aac']:
            ffmpeg_cmd.extend([
                '-codec:a', 'aac',
                '-b:a', '192k',  # Bitrate
            ])
        else:
            # Default to MP3
            ffmpeg_cmd.extend([
                '-codec:a', 'libmp3lame',
                '-qscale:a', '2',
            ])
        
        # Add output file to command
        ffmpeg_cmd.append(output_path)
        
        # Run FFmpeg command
        result = subprocess.run(
            ffmpeg_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Check if conversion was successful
        if result.returncode != 0:
            logger.error(f"FFmpeg conversion failed: {result.stderr}")
            if os.path.exists(output_path):
                os.unlink(output_path)
            return None
        
        # Read the converted data
        with open(output_path, 'rb') as f:
            converted_data = BytesIO(f.read())
            converted_data.seek(0)
        
        # Clean up temporary file
        os.unlink(output_path)
        
        return converted_data
            
    except FileNotFoundError:
        logger.error("FFmpeg is not installed or not found in PATH")
        return None
    except Exception as e:
        logger.error(f"Error converting audio with FFmpeg: {e}")
        # Clean up temporary file if it exists
        if 'output_path' in locals() and os.path.exists(output_path):
            try:
                os.unlink(output_path)
            except:
                pass
        return None


# Alternative implementation using pydub (even simpler)
def convert_audio_with_pydub(input_path, output_format):
    """
    Convert audio file using pydub (lightweight audio library)
    """
    try:
        from pydub import AudioSegment
        
        # Load audio file
        audio = AudioSegment.from_file(input_path)
        
        # Export to the desired format
        if output_format == 'mp3':
            converted_data = audio.export(format='mp3', bitrate='192k')
        elif output_format == 'wav':
            converted_data = audio.export(format='wav')
        elif output_format == 'ogg':
            converted_data = audio.export(format='ogg', bitrate='192k')
        elif output_format == 'flac':
            converted_data = audio.export(format='flac')
        elif output_format in ['m4a', 'aac']:
            converted_data = audio.export(format='ipod')  # pydub uses 'ipod' for m4a/aac
        else:
            # Default to MP3
            converted_data = audio.export(format='mp3', bitrate='192k')
        
        # Return the data as BytesIO
        converted_bytes = BytesIO(converted_data.read())
        converted_bytes.seek(0)
        converted_data.close()
        
        return converted_bytes
            
    except ImportError:
        logger.error("pydub is not installed. Install it with: pip install pydub")
        return None
    except Exception as e:
        logger.error(f"Error converting audio with pydub: {e}")
        return None


# Main converter function that tries both methods
def convert_audio(input_path, output_format):
    """
    Convert audio file using the best available method
    """
    # First try pydub (lightweight)
    result = convert_audio_with_pydub(input_path, output_format)
    if result:
        return result
    
    # Fall back to FFmpeg if pydub fails
    return convert_audio_with_ffmpeg(input_path, output_format)