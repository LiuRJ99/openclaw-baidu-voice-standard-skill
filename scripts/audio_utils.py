"""
Audio utility functions for format conversion and validation
"""
import os
import subprocess
import tempfile
from pathlib import Path


def check_ffmpeg():
    """Check if FFmpeg is available"""
    try:
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, text=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False


def convert_audio_for_baidu_asr(input_path, output_path=None):
    """
    Convert audio file to Baidu ASR compatible format (16kHz, mono, PCM)
    
    Args:
        input_path (str): Input audio file path
        output_path (str): Output path for converted file (optional)
    
    Returns:
        str: Path to converted file or None if failed
    """
    if not os.path.exists(input_path):
        print(f"Input file does not exist: {input_path}")
        return None
    
    if output_path is None:
        # Generate temporary file
        temp_dir = tempfile.gettempdir()
        input_filename = Path(input_path).stem
        output_path = os.path.join(temp_dir, f"{input_filename}_baidu_asr.pcm")
    
    try:
        # Use FFmpeg to convert audio to Baidu ASR compatible format
        cmd = [
            'ffmpeg',
            '-i', input_path,           # Input file
            '-ar', '16000',             # Set sample rate to 16kHz
            '-ac', '1',                 # Set to mono
            '-f', 's16le',              # Set format to signed 16-bit little-endian PCM
            '-y',                       # Overwrite output file if exists
            output_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            # Verify the output file exists and has content
            if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                return output_path
            else:
                print("Output file was created but is empty or missing")
                return None
        else:
            print(f"FFmpeg conversion failed: {result.stderr}")
            return None
            
    except Exception as e:
        print(f"Error during audio conversion: {e}")
        return None


def validate_audio_for_baidu_asr(file_path):
    """
    Validate if audio file meets Baidu ASR requirements
    
    Args:
        file_path (str): Path to audio file
    
    Returns:
        tuple: (is_valid, reason) where is_valid is boolean and reason is string
    """
    if not os.path.exists(file_path):
        return False, "File does not exist"
    
    # Check file size (Baidu ASR has 60MB limit for 60s audio)
    file_size = os.path.getsize(file_path)
    if file_size == 0:
        return False, "File is empty"
    
    # For PCM files, 16kHz mono, 16-bit, 60 seconds max would be about 1.92MB
    # Let's be generous and allow up to 5MB for 60 seconds of audio
    if file_size > 5 * 1024 * 1024:  # 5MB
        return False, "File is too large (>5MB), likely exceeds 60 second limit"
    
    # Try to get audio info using ffprobe if available
    try:
        result = subprocess.run([
            'ffprobe', 
            '-v', 'error', 
            '-show_entries', 'stream=codec_type,sample_rate,channels,duration',
            '-of', 'csv=p=0',
            file_path
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            # Parse the output to check audio properties
            lines = result.stdout.strip().split('\n')
            for line in lines:
                parts = line.split(',')
                if len(parts) >= 2 and parts[0] == 'audio':
                    # Found audio stream, check properties
                    if len(parts) >= 3:
                        sample_rate = int(parts[1]) if parts[1].isdigit() else 16000
                        channels = int(parts[2]) if len(parts) > 2 and parts[2].isdigit() else 2
                        
                        # Instead of rejecting unsupported sample rates, we'll return a warning
                        # This allows the system to attempt conversion for any sample rate
                        if sample_rate not in [8000, 16000]:
                            return False, f"Sample rate {sample_rate}Hz not supported (must be 8000Hz or 16000Hz)"
                        
                        if channels != 1:
                            return False, f"Only mono audio supported, got {channels} channels"
                            
                        break
        
    except FileNotFoundError:
        # ffprobe not available, skip detailed validation
        pass
    except Exception:
        # Some other error occurred, skip detailed validation
        pass
    
    return True, "Valid"


def get_audio_duration(file_path):
    """
    Get audio duration in seconds using ffprobe
    
    Args:
        file_path (str): Path to audio file
    
    Returns:
        float: Duration in seconds or -1 if unable to determine
    """
    try:
        result = subprocess.run([
            'ffprobe',
            '-v', 'error',
            '-show_entries', 'format=duration',
            '-of', 'csv=p=0',
            file_path
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            duration_str = result.stdout.strip()
            if duration_str and duration_str != 'N/A':
                return float(duration_str)
    except:
        pass
    
    return -1


def prepare_audio_for_asr(input_path):
    """
    Prepare audio file for Baidu ASR by validating and converting if necessary
    
    Args:
        input_path (str): Path to input audio file
    
    Returns:
        str: Path to prepared audio file ready for ASR, or None if failed
    """
    # First validate the audio
    is_valid, reason = validate_audio_for_baidu_asr(input_path)
    
    # Check if file needs conversion regardless of validation result
    # If validation fails due to unsupported format, we should still attempt conversion
    file_ext = Path(input_path).suffix.lower()
    
    # If file is not in PCM format, or validation failed due to format issues, convert it
    if file_ext != '.pcm' or "Sample rate" in reason or "channels" in reason:
        print(f"Converting {input_path} to Baidu ASR compatible format...")
        converted_path = convert_audio_for_baidu_asr(input_path)
        if converted_path:
            # After conversion, check the duration
            duration = get_audio_duration(converted_path)
            if duration > 0 and duration > 60:
                print(f"Warning: Audio duration ({duration:.2f}s) exceeds 60s limit")
                try:
                    os.remove(converted_path)  # Clean up converted file
                except:
                    pass
                return None
            return converted_path
        else:
            print(f"Audio conversion failed: {reason}")
            return None
    
    # If validation passed and no conversion needed, return original path
    if is_valid:
        duration = get_audio_duration(input_path)
        if duration > 0 and duration > 60:
            print(f"Warning: Audio duration ({duration:.2f}s) exceeds 60s limit")
            return None
        return input_path
    else:
        print(f"Audio validation failed: {reason}")
        return None