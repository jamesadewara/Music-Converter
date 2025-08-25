import os
from pydub import AudioSegment
from io import BytesIO
import tempfile

def convert_audio(input_path, output_format):
    """
    Convert audio file to the specified format using pydub
    """
    try:
        # Map format to pydub format
        format_map = {
            'mp3': 'mp3',
            'wav': 'wav',
            'ogg': 'ogg',
            'flac': 'flac',
            'm4a': 'ipod'  # pydub uses 'ipod' for m4a format
        }
        
        if output_format not in format_map:
            return None
        
        # Load audio file
        audio = AudioSegment.from_file(input_path)
        
        # Create a temporary file to store the converted audio
        with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{output_format}') as tmp:
            # Export to the desired format
            audio.export(tmp.name, format=format_map[output_format])
            
            # Read the converted data
            with open(tmp.name, 'rb') as f:
                converted_data = BytesIO(f.read())
                converted_data.seek(0)
            
            # Clean up temporary file
            os.unlink(tmp.name)
            
            return converted_data
            
    except Exception as e:
        print(f"Error converting audio: {e}")
        return None