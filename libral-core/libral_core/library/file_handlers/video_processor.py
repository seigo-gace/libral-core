"""
Video Processor

Provides video processing capabilities for the LIVE VIDEO CHAT module
and other video-related functionality across Libral Core.
"""

import logging
from io import BytesIO
from typing import Tuple, Optional, Union
import subprocess
import tempfile
import os
import shutil
import json
from fractions import Fraction


logger = logging.getLogger(__name__)


class VideoProcessor:
    """
    Unified video processing class for all Libral Core modules.
    
    Design Intent:
    - Enable video sharing and processing in LIVE VIDEO CHAT module
    - Provide consistent video operations across all apps
    - Support format conversion for different platforms
    - Optimize video files for bandwidth efficiency
    
    Note: This class requires FFmpeg to be installed on the system.
    """
    
    # Standard video specifications
    MAX_DURATION_SECONDS = 60  # Maximum video duration for processing
    MAX_FILE_SIZE_MB = 50      # Maximum file size in MB
    
    # Supported formats
    SUPPORTED_INPUT_FORMATS = ['mp4', 'avi', 'mov', 'webm', 'mkv']
    SUPPORTED_OUTPUT_FORMATS = ['mp4', 'webm', 'gif']
    
    def __init__(self):
        """Initialize the video processor."""
        self._check_ffmpeg()
    
    def _check_ffmpeg(self) -> bool:
        """Check if FFmpeg is available on the system."""
        try:
            subprocess.run(['ffmpeg', '-version'], 
                         capture_output=True, check=True, timeout=5)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            logger.warning("FFmpeg not found. Video processing capabilities will be limited.")
            return False
    
    def convert_to_gif(self, video_bytes: bytes, max_duration: int = 10, 
                      size: Optional[Tuple[int, int]] = None, fps: int = 10) -> bytes:
        """
        Convert video to GIF animation for easy sharing.
        
        This function enables LIVE VIDEO CHAT users to convert video clips
        into GIF animations for sharing in messages and social media.
        
        Args:
            video_bytes: Original video data
            max_duration: Maximum GIF duration in seconds
            size: Output size (width, height), None to maintain original
            fps: Frames per second for the GIF
            
        Returns:
            GIF animation data as bytes
            
        Example:
            >>> processor = VideoProcessor()
            >>> with open("video.mp4", "rb") as f:
            ...     video_data = f.read()
            >>> gif_data = processor.convert_to_gif(video_data, max_duration=5)
            >>> with open("animation.gif", "wb") as f:
            ...     f.write(gif_data)
        """
        if not video_bytes:
            raise ValueError("Video data cannot be empty")
        
        if not self._check_ffmpeg():
            raise RuntimeError("FFmpeg is required for video processing")
        
        # Create temporary files
        with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as input_file:
            input_file.write(video_bytes)
            input_path = input_file.name
        
        with tempfile.NamedTemporaryFile(suffix='.gif', delete=False) as output_file:
            output_path = output_file.name
        
        try:
            # Build FFmpeg command
            cmd = [
                'ffmpeg',
                '-i', input_path,
                '-t', str(max_duration),  # Limit duration
                '-r', str(fps),           # Set frame rate
                '-y'                      # Overwrite output file
            ]
            
            # Add size filter if specified
            if size:
                width, height = size
                cmd.extend(['-vf', f'scale={width}:{height}'])
            
            cmd.append(output_path)
            
            # Execute FFmpeg
            result = subprocess.run(cmd, capture_output=True, timeout=60)
            
            if result.returncode != 0:
                error_msg = result.stderr.decode('utf-8', errors='ignore')
                raise RuntimeError(f"Video conversion failed: {error_msg}")
            
            # Read output GIF
            with open(output_path, 'rb') as f:
                gif_data = f.read()
            
            if not gif_data:
                raise RuntimeError("No output generated from video conversion")
            
            return gif_data
            
        except subprocess.TimeoutExpired:
            raise RuntimeError("Video conversion timed out")
        except Exception as e:
            logger.error(f"Video to GIF conversion failed: {e}")
            raise RuntimeError(f"Conversion failed: {e}")
        finally:
            # Clean up temporary files
            for path in [input_path, output_path]:
                try:
                    os.unlink(path)
                except OSError:
                    pass
    
    def compress_video(self, video_bytes: bytes, target_size_mb: float = 5.0,
                      quality: str = "medium") -> bytes:
        """
        Compress video to reduce file size for efficient sharing.
        
        Design Intent: Optimize video files for bandwidth efficiency in LIVE VIDEO CHAT
        
        Args:
            video_bytes: Original video data
            target_size_mb: Target file size in MB
            quality: Compression quality ("low", "medium", "high")
            
        Returns:
            Compressed video data as bytes
        """
        if not video_bytes:
            raise ValueError("Video data cannot be empty")
        
        if not self._check_ffmpeg():
            raise RuntimeError("FFmpeg is required for video processing")
        
        # Quality settings
        quality_settings = {
            "low": {"crf": 28, "preset": "fast"},
            "medium": {"crf": 23, "preset": "medium"},
            "high": {"crf": 18, "preset": "slow"}
        }
        
        settings = quality_settings.get(quality, quality_settings["medium"])
        
        # Create temporary files
        with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as input_file:
            input_file.write(video_bytes)
            input_path = input_file.name
        
        with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as output_file:
            output_path = output_file.name
        
        try:
            # Build compression command
            cmd = [
                'ffmpeg',
                '-i', input_path,
                '-c:v', 'libx264',              # Video codec
                '-crf', str(settings["crf"]),   # Quality factor
                '-preset', settings["preset"],   # Encoding preset
                '-c:a', 'aac',                  # Audio codec
                '-b:a', '128k',                 # Audio bitrate
                '-movflags', '+faststart',       # Web optimization
                '-y',                           # Overwrite output
                output_path
            ]
            
            # Execute compression
            result = subprocess.run(cmd, capture_output=True, timeout=120)
            
            if result.returncode != 0:
                error_msg = result.stderr.decode('utf-8', errors='ignore')
                raise RuntimeError(f"Video compression failed: {error_msg}")
            
            # Read compressed video
            with open(output_path, 'rb') as f:
                compressed_data = f.read()
            
            # Check if compression achieved target size
            compressed_size_mb = len(compressed_data) / (1024 * 1024)
            logger.info(f"Video compressed from {len(video_bytes)/(1024*1024):.1f}MB to {compressed_size_mb:.1f}MB")
            
            return compressed_data
            
        except subprocess.TimeoutExpired:
            raise RuntimeError("Video compression timed out")
        except Exception as e:
            logger.error(f"Video compression failed: {e}")
            raise RuntimeError(f"Compression failed: {e}")
        finally:
            # Clean up temporary files
            for path in [input_path, output_path]:
                try:
                    os.unlink(path)
                except OSError:
                    pass
    
    def extract_thumbnail(self, video_bytes: bytes, timestamp: float = 1.0,
                         size: Tuple[int, int] = (320, 180)) -> bytes:
        """
        Extract thumbnail image from video at specified timestamp.
        
        Args:
            video_bytes: Video data
            timestamp: Time in seconds to extract thumbnail
            size: Thumbnail size (width, height)
            
        Returns:
            Thumbnail image data as bytes (PNG format)
        """
        if not video_bytes:
            raise ValueError("Video data cannot be empty")
        
        if not self._check_ffmpeg():
            raise RuntimeError("FFmpeg is required for video processing")
        
        # Create temporary files
        with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as input_file:
            input_file.write(video_bytes)
            input_path = input_file.name
        
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as output_file:
            output_path = output_file.name
        
        try:
            width, height = size
            
            cmd = [
                'ffmpeg',
                '-i', input_path,
                '-ss', str(timestamp),        # Seek to timestamp
                '-vframes', '1',              # Extract single frame
                '-vf', f'scale={width}:{height}',  # Resize
                '-y',                         # Overwrite output
                output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, timeout=30)
            
            if result.returncode != 0:
                error_msg = result.stderr.decode('utf-8', errors='ignore')
                raise RuntimeError(f"Thumbnail extraction failed: {error_msg}")
            
            # Read thumbnail
            with open(output_path, 'rb') as f:
                thumbnail_data = f.read()
            
            return thumbnail_data
            
        except subprocess.TimeoutExpired:
            raise RuntimeError("Thumbnail extraction timed out")
        except Exception as e:
            logger.error(f"Thumbnail extraction failed: {e}")
            raise RuntimeError(f"Extraction failed: {e}")
        finally:
            # Clean up temporary files
            for path in [input_path, output_path]:
                try:
                    os.unlink(path)
                except OSError:
                    pass
    
    def get_video_info(self, video_bytes: bytes) -> dict:
        """
        Extract video metadata and information.
        
        Args:
            video_bytes: Video data
            
        Returns:
            Dictionary with video information
        """
        if not video_bytes:
            return {}
        
        if not self._check_ffmpeg():
            return {"error": "FFmpeg not available"}
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as input_file:
            input_file.write(video_bytes)
            input_path = input_file.name
        
        try:
            cmd = [
                'ffprobe',
                '-v', 'quiet',
                '-print_format', 'json',
                '-show_format',
                '-show_streams',
                input_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, timeout=30)
            
            if result.returncode != 0:
                return {"error": "Failed to analyze video"}
            
            probe_data = json.loads(result.stdout.decode('utf-8'))
            
            # Extract relevant information
            format_info = probe_data.get('format', {})
            video_stream = None
            
            for stream in probe_data.get('streams', []):
                if stream.get('codec_type') == 'video':
                    video_stream = stream
                    break
            
            info = {
                'duration': float(format_info.get('duration', 0)),
                'size': int(format_info.get('size', 0)),
                'bit_rate': int(format_info.get('bit_rate', 0)),
                'format_name': format_info.get('format_name', ''),
            }
            
            if video_stream:
                # Safely parse frame rate fraction
                frame_rate_str = video_stream.get('r_frame_rate', '0/1')
                try:
                    fps = float(Fraction(frame_rate_str))
                except (ValueError, ZeroDivisionError):
                    fps = 0.0
                
                info.update({
                    'width': int(video_stream.get('width', 0)),
                    'height': int(video_stream.get('height', 0)),
                    'fps': fps,
                    'codec': video_stream.get('codec_name', ''),
                })
            
            return info
            
        except (subprocess.TimeoutExpired, json.JSONDecodeError, Exception) as e:
            logger.error(f"Video info extraction failed: {e}")
            return {"error": str(e)}
        finally:
            try:
                os.unlink(input_path)
            except OSError:
                pass
    
    @staticmethod
    def validate_video(video_bytes: bytes) -> bool:
        """
        Validate if data represents a valid video file.
        
        Args:
            video_bytes: Video data to validate
            
        Returns:
            True if valid video, False otherwise
        """
        if not video_bytes:
            return False
        
        # Check file size
        size_mb = len(video_bytes) / (1024 * 1024)
        if size_mb > VideoProcessor.MAX_FILE_SIZE_MB:
            return False
        
        # Basic header validation for common formats
        if video_bytes.startswith(b'\x00\x00\x00\x18ftypmp4') or \
           video_bytes.startswith(b'\x00\x00\x00\x20ftypmp4'):
            return True  # MP4
        elif video_bytes.startswith(b'RIFF') and b'WEBP' in video_bytes[:12]:
            return True  # WebM
        elif video_bytes.startswith(b'\x1a\x45\xdf\xa3'):
            return True  # WebM/MKV
        
        return False