# /backend/services/scheduler/app/core/mac_camera_wrapper.py
import subprocess
import os
import asyncio
import logging
from typing import Optional, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)

class MacCameraWrapper:
    """
    Python wrapper for the macOS camera service
    """
    
    def __init__(self):
        self.camera_service_path = self._get_camera_service_path()
        self.camera_process = None
        
    def _get_camera_service_path(self) -> str:
        """Get the path to the compiled camera service"""
        current_dir = Path(__file__).parent.parent.parent.parent
        service_path = current_dir / "mac_camera_service" / "camera_service"
        return str(service_path)
    
    async def start_camera_service(self):
        """Start the macOS camera service"""
        try:
            if self.camera_process is None or self.camera_process.poll() is not None:
                logger.info("Starting macOS camera service...")
                
                # Compile the Swift service if needed
                await self._compile_camera_service()
                
                # Start the camera service
                self.camera_process = subprocess.Popen(
                    [self.camera_service_path],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                
                # Give it a moment to start
                await asyncio.sleep(2)
                
                if self.camera_process.poll() is None:
                    logger.info("Camera service started successfully")
                else:
                    stdout, stderr = self.camera_process.communicate()
                    logger.error(f"Camera service failed to start: {stderr}")
                    
        except Exception as e:
            logger.error(f"Error starting camera service: {e}")
    
    async def _compile_camera_service(self):
        """Compile the Swift camera service"""
        try:
            service_dir = Path(self.camera_service_path).parent
            swift_file = service_dir / "main.swift"
            
            if not swift_file.exists():
                logger.error("Swift camera service file not found")
                return
            
            # Compile the Swift file
            compile_cmd = [
                "swiftc",
                "-framework", "AVFoundation",
                "-framework", "AppKit",
                "-framework", "Foundation",
                str(swift_file),
                "-o", self.camera_service_path
            ]
            
            result = subprocess.run(compile_cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info("Camera service compiled successfully")
            else:
                logger.error(f"Failed to compile camera service: {result.stderr}")
                
        except Exception as e:
            logger.error(f"Error compiling camera service: {e}")
    
    async def capture_photo(self, output_path: str) -> Tuple[bool, Optional[str]]:
        """
        Capture a photo using the macOS camera
        
        Args:
            output_path: Path where to save the captured photo
            
        Returns:
            Tuple of (success, error_message)
        """
        try:
            # Ensure camera service is running
            if self.camera_process is None or self.camera_process.poll() is not None:
                await self.start_camera_service()
            
            # Create a temporary script to trigger photo capture
            capture_script = self._create_capture_script(output_path)
            
            # Execute the capture script
            result = subprocess.run(
                ["osascript", "-e", capture_script],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                # Check if the photo was actually created
                if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                    logger.info(f"Photo captured successfully: {output_path}")
                    return True, None
                else:
                    return False, "Photo file was not created or is empty"
            else:
                return False, f"Capture failed: {result.stderr}"
                
        except subprocess.TimeoutExpired:
            return False, "Photo capture timed out"
        except Exception as e:
            logger.error(f"Error capturing photo: {e}")
            return False, str(e)
    
    def _create_capture_script(self, output_path: str) -> str:
        """Create an AppleScript to trigger photo capture"""
        return f'''
        tell application "System Events"
            -- This would need to be implemented based on your specific needs
            -- For now, we'll use a different approach
        end tell
        '''
    
    async def stop_camera_service(self):
        """Stop the camera service"""
        try:
            if self.camera_process and self.camera_process.poll() is None:
                self.camera_process.terminate()
                await asyncio.sleep(1)
                
                if self.camera_process.poll() is None:
                    self.camera_process.kill()
                
                logger.info("Camera service stopped")
                
        except Exception as e:
            logger.error(f"Error stopping camera service: {e}")