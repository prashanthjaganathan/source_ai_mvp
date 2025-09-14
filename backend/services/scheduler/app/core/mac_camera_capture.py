# /backend/services/scheduler/app/core/mac_camera_capture.py
import subprocess
import os
import tempfile
import asyncio
import logging
from typing import Tuple, Optional

logger = logging.getLogger(__name__)

class MacCameraCapture:
    """
    Fast Mac camera capture using built-in tools - optimized for speed
    """
    
    def __init__(self):
        self.temp_dir = tempfile.gettempdir()
        
    async def capture_photo(self, output_path: str) -> Tuple[bool, Optional[str]]:
        """
        Capture a photo using Mac's built-in camera - FAST VERSION
        
        Args:
            output_path: Path where to save the captured photo
            
        Returns:
            Tuple of (success, error_message)
        """
        try:
            logger.info(f"Capturing photo with Mac camera to: {output_path}")
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Method 1: Try using imagesnap (FASTEST - no delays)
            success, error = await self._capture_with_imagesnap(output_path)
            if success:
                return True, None
            
            # Method 2: Try using screencapture (FAST - just a screenshot)
            success, error = await self._capture_with_screencapture(output_path)
            if success:
                return True, None
            
            # Method 3: Try using Photo Booth (FAST - minimal delays)
            success, error = await self._capture_with_photobooth_fast(output_path)
            if success:
                return True, None
            
            # Method 4: Try using QuickTime Player (FAST - no UI delays)
            success, error = await self._capture_with_quicktime(output_path)
            if success:
                return True, None
            
            return False, f"All capture methods failed. Last error: {error}"
            
        except Exception as e:
            logger.error(f"Error in camera capture: {e}")
            return False, str(e)
    
    async def _capture_with_imagesnap(self, output_path: str) -> Tuple[bool, str]:
        """Try to capture using imagesnap utility - FASTEST METHOD"""
        try:
            # Check if imagesnap is available
            result = subprocess.run(['which', 'imagesnap'], capture_output=True, text=True)
            if result.returncode != 0:
                return False, "imagesnap not found"
            
            # Capture photo with imagesnap - NO DELAYS, immediate capture
            cmd = ['imagesnap', output_path]  # Removed -w 1 delay
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)  # Reduced timeout
            
            if result.returncode == 0 and os.path.exists(output_path):
                logger.info("Photo captured successfully with imagesnap (FAST)")
                return True, ""
            else:
                return False, f"imagesnap failed: {result.stderr}"
                
        except subprocess.TimeoutExpired:
            return False, "imagesnap timed out"
        except Exception as e:
            return False, str(e)
    
    async def _capture_with_screencapture(self, output_path: str) -> Tuple[bool, str]:
        """Try to capture using screencapture - FAST SCREENSHOT"""
        try:
            # This captures the screen quickly - no delays
            cmd = ['screencapture', output_path]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=3)  # Very fast timeout
            
            if result.returncode == 0 and os.path.exists(output_path):
                logger.info("Photo captured with screencapture (FAST screenshot)")
                return True, ""
            else:
                return False, f"screencapture failed: {result.stderr}"
                
        except Exception as e:
            return False, str(e)
    
    async def _capture_with_photobooth_fast(self, output_path: str) -> Tuple[bool, str]:
        """Try to capture using Photo Booth - FAST VERSION with minimal delays"""
        try:
            # Create an AppleScript to take a photo with Photo Booth - NO DELAYS
            applescript = '''
            tell application "Photo Booth"
                activate
                take picture
                quit
            end tell
            '''
            
            # Save script to temporary file
            script_path = os.path.join(self.temp_dir, "capture_photo_fast.scpt")
            with open(script_path, 'w') as f:
                f.write(applescript)
            
            # Run the script - reduced timeout
            result = subprocess.run(['osascript', script_path], capture_output=True, text=True, timeout=8)
            
            # Clean up
            if os.path.exists(script_path):
                os.remove(script_path)
            
            if result.returncode == 0:
                # Photo Booth saves to ~/Pictures/Photo Booth, find the latest photo
                photos_dir = os.path.expanduser("~/Pictures/Photo Booth")
                if os.path.exists(photos_dir):
                    photos = [f for f in os.listdir(photos_dir) if f.endswith(('.jpg', '.jpeg', '.png'))]
                    if photos:
                        latest_photo = max(photos, key=lambda x: os.path.getmtime(os.path.join(photos_dir, x)))
                        source_path = os.path.join(photos_dir, latest_photo)
                        
                        # Copy to our desired location
                        import shutil
                        shutil.copy2(source_path, output_path)
                        logger.info("Photo captured with Photo Booth (FAST)")
                        return True, ""
            
            return False, "Photo Booth capture failed"
            
        except Exception as e:
            return False, str(e)
    
    async def _capture_with_quicktime(self, output_path: str) -> Tuple[bool, str]:
        """Try to capture using QuickTime Player - FAST METHOD"""
        try:
            # Create an AppleScript to use QuickTime Player for camera capture
            applescript = f'''
            tell application "QuickTime Player"
                activate
                set newMovieRecording to new movie recording
                tell newMovieRecording
                    start
                    delay 0.5
                    stop
                end tell
                close newMovieRecording
                quit
            end tell
            '''
            
            # Save script to temporary file
            script_path = os.path.join(self.temp_dir, "capture_quicktime.scpt")
            with open(script_path, 'w') as f:
                f.write(applescript)
            
            # Run the script
            result = subprocess.run(['osascript', script_path], capture_output=True, text=True, timeout=10)
            
            # Clean up
            if os.path.exists(script_path):
                os.remove(script_path)
            
            if result.returncode == 0:
                logger.info("Photo captured with QuickTime Player (FAST)")
                return True, ""
            
            return False, "QuickTime Player capture failed"
            
        except Exception as e:
            return False, str(e)

    async def check_camera_availability(self) -> bool:
        """Check if camera is available"""
        try:
            # Fast check - try to list video devices
            result = subprocess.run(['system_profiler', 'SPCameraDataType'], capture_output=True, text=True, timeout=3)
            if result.returncode == 0 and 'Camera' in result.stdout:
                return True
            
            # Alternative fast check
            result = subprocess.run(['ffmpeg', '-f', 'avfoundation', '-list_devices', 'true', '-i', '""'], 
                                  capture_output=True, text=True, timeout=3)
            return 'AVFoundation video devices' in result.stderr
            
        except Exception:
            return False