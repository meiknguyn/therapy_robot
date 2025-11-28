# modules/camera_capture.py
"""
Camera Capture Module
Uses OpenCV for image capture and saving.
"""
import os
import cv2
from datetime import datetime


class CameraCapture:
    """
    Camera controller for capturing and saving images.
    """

    def __init__(self, save_dir="proofs", log_callback=None):
        """
        Initialize camera capture.
        
        Args:
            save_dir: Directory to save captured images
            log_callback: Optional callback function(event_type, details) for logging
        """
        self.save_dir = save_dir
        self.log_callback = log_callback
        self.camera = None
        
        # Ensure save directory exists
        if not os.path.exists(save_dir):
            os.makedirs(save_dir, exist_ok=True)
            print(f"[Camera] Created directory: {save_dir}")

    def _log(self, event_type: str, details: dict):
        """Log event using callback."""
        if self.log_callback:
            try:
                self.log_callback(event_type, details)
            except Exception as e:
                print(f"[Camera] Error in log callback: {e}")

    def capture_frame(self, save_path=None):
        """
        Capture a frame from camera and save it.
        
        Args:
            save_path: Optional custom path/filename. If None, auto-generates filename.
        
        Returns:
            Path to saved image file, or None on error
        """
        try:
            # Try to open camera (typically device 0)
            cap = cv2.VideoCapture(0)
            
            if not cap.isOpened():
                print("[Camera] Could not open camera device")
                return None
            
            # Capture frame
            ret, frame = cap.read()
            cap.release()
            
            if not ret or frame is None:
                print("[Camera] Failed to capture frame")
                return None
            
            # Generate filename if not provided
            if save_path is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"capture_{timestamp}.jpg"
                save_path = os.path.join(self.save_dir, filename)
            else:
                # Ensure it's in save_dir
                if not os.path.dirname(save_path):
                    save_path = os.path.join(self.save_dir, save_path)
                # Ensure .jpg extension
                if not save_path.lower().endswith(('.jpg', '.jpeg', '.png')):
                    save_path += ".jpg"
            
            # Save image
            success = cv2.imwrite(save_path, frame)
            
            if success:
                print(f"[Camera] Captured and saved: {save_path}")
                self._log("camera_capture", {
                    "file": os.path.basename(save_path),
                    "path": save_path,
                    "timestamp": datetime.now().isoformat()
                })
                return save_path
            else:
                print(f"[Camera] Failed to save image: {save_path}")
                return None
                
        except Exception as e:
            print(f"[Camera] Error during capture: {e}")
            return None

    def capture(self, filename=None):
        """
        Alias for capture_frame for simpler API.
        
        Args:
            filename: Optional filename
        
        Returns:
            Path to saved image file, or None on error
        """
        return self.capture_frame(filename)

    def list_captures(self):
        """
        List all captured images in save directory.
        
        Returns:
            List of captured image filenames
        """
        if not os.path.exists(self.save_dir):
            return []
        
        image_extensions = ['.jpg', '.jpeg', '.png']
        files = []
        
        for filename in os.listdir(self.save_dir):
            if any(filename.lower().endswith(ext) for ext in image_extensions):
                files.append(filename)
        
        return sorted(files, reverse=True)  # Most recent first

    def cleanup(self):
        """Clean up resources."""
        if self.camera is not None:
            try:
                self.camera.release()
            except:
                pass
            self.camera = None

