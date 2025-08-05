"""
Media Player Widget

Professional media player widget with OpenRV integration capabilities,
frame-accurate scrubbing, and support for VFX formats.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
from typing import Optional, Dict, Any
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QSlider, QGroupBox, QFrame, QSizePolicy, QMessageBox,
    QTextEdit, QCheckBox, QComboBox, QSpinBox
)
from PySide6.QtCore import Qt, Signal, QTimer, QProcess
from PySide6.QtGui import QPixmap, QFont, QPalette, QColor


class MediaPlayerWidget(QWidget):
    """
    Professional media player widget with OpenRV integration capabilities.

    Provides advanced playback controls, frame-accurate scrubbing, OpenRV integration,
    and support for professional VFX formats (.exr, .mov, .mp4, .jpg, .png).
    """

    # Signals
    mediaLoaded = Signal(str)           # file_path
    playbackStateChanged = Signal(str)  # state (playing, paused, stopped)
    frameChanged = Signal(int)          # frame_number
    openrvLaunched = Signal(str)        # file_path

    def __init__(self, parent=None):
        """Initialize professional media player widget."""
        super().__init__(parent)

        # State
        self.current_media_path: Optional[str] = None
        self.current_media_item: Optional[Dict[str, Any]] = None
        self.is_playing = False
        self.current_frame = 0
        self.total_frames = 0
        self.frame_rate = 24.0

        # OpenRV integration
        self.openrv_available = self.check_openrv_availability()
        self.openrv_process: Optional[QProcess] = None

        # Playback timer
        self.playback_timer = QTimer()
        self.playback_timer.timeout.connect(self.advance_frame)

        # Setup UI
        self.setup_ui()
        self.setup_connections()

        # Initialize with placeholder
        self.show_placeholder()

    def check_openrv_availability(self) -> bool:
        """Check if OpenRV is available on the system."""
        try:
            # Common OpenRV executable names and paths
            openrv_names = ['rv', 'openrv', 'RV', 'OpenRV']

            for name in openrv_names:
                if shutil.which(name):
                    return True

            # Check common installation paths
            common_paths = [
                '/usr/local/bin/rv',
                '/opt/rv/bin/rv',
                'C:\\Program Files\\Tweak\\RV\\bin\\rv.exe',
                'C:\\Program Files\\OpenRV\\bin\\rv.exe'
            ]

            for path in common_paths:
                if os.path.exists(path):
                    return True

            return False

        except Exception as e:
            print(f"Error checking OpenRV availability: {e}")
            return False

    def setup_professional_controls(self, layout):
        """Setup professional media player controls."""
        # Professional controls header
        prof_controls_group = QGroupBox("Professional Media Player")
        prof_layout = QHBoxLayout(prof_controls_group)

        # OpenRV integration
        openrv_layout = QVBoxLayout()

        self.openrv_checkbox = QCheckBox("Use OpenRV (Professional)")
        self.openrv_checkbox.setChecked(self.openrv_available)
        self.openrv_checkbox.setEnabled(self.openrv_available)
        if not self.openrv_available:
            self.openrv_checkbox.setToolTip("OpenRV not found on system. Install OpenRV for professional VFX review capabilities.")
        else:
            self.openrv_checkbox.setToolTip("Use OpenRV for professional VFX review with advanced color management and format support")
        openrv_layout.addWidget(self.openrv_checkbox)

        self.launch_openrv_btn = QPushButton("Launch in OpenRV")
        self.launch_openrv_btn.setEnabled(False)
        self.launch_openrv_btn.setToolTip("Launch current media file in external OpenRV application")
        openrv_layout.addWidget(self.launch_openrv_btn)

        prof_layout.addLayout(openrv_layout)

        # Playback settings
        settings_layout = QVBoxLayout()

        fps_layout = QHBoxLayout()
        fps_layout.addWidget(QLabel("FPS:"))
        self.fps_spinbox = QSpinBox()
        self.fps_spinbox.setRange(1, 120)
        self.fps_spinbox.setValue(24)
        self.fps_spinbox.setToolTip("Playback frame rate")
        fps_layout.addWidget(self.fps_spinbox)
        settings_layout.addLayout(fps_layout)

        # Color space
        colorspace_layout = QHBoxLayout()
        colorspace_layout.addWidget(QLabel("Color Space:"))
        self.colorspace_combo = QComboBox()
        self.colorspace_combo.addItems(["sRGB", "Rec.709", "Linear", "ACES"])
        self.colorspace_combo.setToolTip("Display color space")
        colorspace_layout.addWidget(self.colorspace_combo)
        settings_layout.addLayout(colorspace_layout)

        prof_layout.addLayout(settings_layout)

        # Status info
        status_layout = QVBoxLayout()

        self.openrv_status_label = QLabel("OpenRV: Not Available" if not self.openrv_available else "OpenRV: Available")
        self.openrv_status_label.setStyleSheet(f"""
            QLabel {{
                color: {'#ff6b6b' if not self.openrv_available else '#51cf66'};
                font-weight: bold;
                padding: 4px;
            }}
        """)
        status_layout.addWidget(self.openrv_status_label)

        self.format_support_label = QLabel("Formats: .exr, .mov, .mp4, .jpg, .png")
        self.format_support_label.setStyleSheet("QLabel { color: #888; font-size: 10px; }")
        status_layout.addWidget(self.format_support_label)

        prof_layout.addLayout(status_layout)

        layout.addWidget(prof_controls_group)

    def setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)
        
        # Media display area
        display_group = QGroupBox("Media Viewer")
        display_layout = QVBoxLayout(display_group)
        
        # Media display frame
        self.media_frame = QFrame()
        self.media_frame.setFrameStyle(QFrame.StyledPanel)
        self.media_frame.setMinimumSize(640, 360)
        self.media_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.media_frame.setStyleSheet("""
            QFrame {
                background-color: #2b2b2b;
                border: 2px solid #555;
            }
        """)
        
        frame_layout = QVBoxLayout(self.media_frame)
        
        # Media display label
        self.media_label = QLabel("No media loaded")
        self.media_label.setAlignment(Qt.AlignCenter)
        self.media_label.setStyleSheet("""
            QLabel {
                color: #888;
                font-size: 14pt;
                background-color: transparent;
                border: none;
            }
        """)
        self.media_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        frame_layout.addWidget(self.media_label)
        
        display_layout.addWidget(self.media_frame)
        layout.addWidget(display_group)
        
        # Controls area
        controls_group = QGroupBox("Playback Controls")
        controls_layout = QVBoxLayout(controls_group)
        
        # Timeline scrubber
        timeline_layout = QHBoxLayout()
        
        self.frame_label = QLabel("Frame: 0 / 0")
        self.frame_label.setMinimumWidth(100)
        timeline_layout.addWidget(self.frame_label)
        
        self.timeline_slider = QSlider(Qt.Horizontal)
        self.timeline_slider.setMinimum(0)
        self.timeline_slider.setMaximum(0)
        self.timeline_slider.setValue(0)
        timeline_layout.addWidget(self.timeline_slider)
        
        self.timecode_label = QLabel("00:00:00:00")
        self.timecode_label.setMinimumWidth(80)
        timeline_layout.addWidget(self.timecode_label)
        
        controls_layout.addLayout(timeline_layout)
        
        # Playback buttons
        buttons_layout = QHBoxLayout()
        
        self.first_frame_button = QPushButton("⏮")
        self.first_frame_button.setMaximumWidth(40)
        self.first_frame_button.setToolTip("First Frame")
        buttons_layout.addWidget(self.first_frame_button)
        
        self.prev_frame_button = QPushButton("⏪")
        self.prev_frame_button.setMaximumWidth(40)
        self.prev_frame_button.setToolTip("Previous Frame")
        buttons_layout.addWidget(self.prev_frame_button)
        
        self.play_pause_button = QPushButton("▶")
        self.play_pause_button.setMaximumWidth(60)
        self.play_pause_button.setToolTip("Play/Pause")
        buttons_layout.addWidget(self.play_pause_button)
        
        self.next_frame_button = QPushButton("⏩")
        self.next_frame_button.setMaximumWidth(40)
        self.next_frame_button.setToolTip("Next Frame")
        buttons_layout.addWidget(self.next_frame_button)
        
        self.last_frame_button = QPushButton("⏭")
        self.last_frame_button.setMaximumWidth(40)
        self.last_frame_button.setToolTip("Last Frame")
        buttons_layout.addWidget(self.last_frame_button)
        
        buttons_layout.addStretch()
        
        # Frame rate display
        self.fps_label = QLabel("24 fps")
        self.fps_label.setStyleSheet("color: #666;")
        buttons_layout.addWidget(self.fps_label)
        
        controls_layout.addLayout(buttons_layout)
        
        layout.addWidget(controls_group)
        
        # Media info
        info_group = QGroupBox("Media Information")
        info_layout = QVBoxLayout(info_group)
        
        self.media_info_label = QLabel("No media information available")
        self.media_info_label.setStyleSheet("color: #666; font-size: 9pt;")
        self.media_info_label.setWordWrap(True)
        info_layout.addWidget(self.media_info_label)
        
        layout.addWidget(info_group)
    
    def setup_connections(self):
        """Set up signal connections."""
        # Timeline scrubber
        self.timeline_slider.valueChanged.connect(self.on_timeline_changed)

        # Playback buttons
        self.first_frame_button.clicked.connect(self.go_to_first_frame)
        self.prev_frame_button.clicked.connect(self.previous_frame)
        self.play_pause_button.clicked.connect(self.toggle_playback)
        self.next_frame_button.clicked.connect(self.next_frame)
        self.last_frame_button.clicked.connect(self.go_to_last_frame)

        # Professional controls
        if hasattr(self, 'launch_openrv_btn'):
            self.launch_openrv_btn.clicked.connect(self.launch_in_openrv)

        if hasattr(self, 'fps_spinbox'):
            self.fps_spinbox.valueChanged.connect(self.on_fps_changed)

        if hasattr(self, 'colorspace_combo'):
            self.colorspace_combo.currentTextChanged.connect(self.on_colorspace_changed)
    
    def load_media(self, file_path: str):
        """Load media file for playback."""
        if not os.path.exists(file_path):
            self.clear_media()
            return
        
        self.current_media_path = file_path
        file_name = os.path.basename(file_path)
        file_ext = os.path.splitext(file_name)[1].lower()
        
        # Update media info
        file_size = os.path.getsize(file_path)
        size_mb = file_size / (1024 * 1024)
        
        info_text = f"File: {file_name}\n"
        info_text += f"Size: {size_mb:.1f} MB\n"
        info_text += f"Type: {file_ext.upper()} file"
        
        # Handle different media types
        if file_ext in ['.jpg', '.jpeg', '.png', '.tiff', '.tga', '.exr']:
            # Image file
            self.load_image(file_path)
            self.total_frames = 1
            info_text += "\nFormat: Still Image"
        elif file_ext in ['.mov', '.mp4', '.avi', '.mkv']:
            # Video file
            self.load_video(file_path)
            # For demo purposes, assume 100 frames
            self.total_frames = 100
            info_text += f"\nFormat: Video ({self.total_frames} frames)"
        else:
            # Unsupported format
            self.media_label.setText(f"Unsupported format: {file_ext}")
            self.total_frames = 0
            info_text += "\nFormat: Unsupported"
        
        self.media_info_label.setText(info_text)
        
        # Update timeline
        self.timeline_slider.setMaximum(max(0, self.total_frames - 1))
        self.current_frame = 0
        self.timeline_slider.setValue(0)
        self.update_frame_display()
        
        # Emit signal
        self.mediaLoaded.emit(file_path)
    
    def load_image(self, file_path: str):
        """Load and display image file."""
        try:
            pixmap = QPixmap(file_path)
            if not pixmap.isNull():
                # Scale pixmap to fit display while maintaining aspect ratio
                scaled_pixmap = pixmap.scaled(
                    self.media_label.size(),
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
                self.media_label.setPixmap(scaled_pixmap)
            else:
                self.media_label.setText("Failed to load image")
        except Exception as e:
            self.media_label.setText(f"Error loading image: {str(e)}")
    
    def load_video(self, file_path: str):
        """Load video file (placeholder implementation)."""
        # This is a placeholder implementation
        # In a full implementation, this would use a video library like OpenCV or FFmpeg
        self.media_label.setText(f"Video: {os.path.basename(file_path)}\n\n(Video playback not implemented in demo)")
    
    def clear_media(self):
        """Clear current media."""
        self.current_media_path = None
        self.is_playing = False
        self.current_frame = 0
        self.total_frames = 0
        
        self.media_label.clear()
        self.media_label.setText("No media loaded")
        self.media_info_label.setText("No media information available")
        
        self.timeline_slider.setMaximum(0)
        self.timeline_slider.setValue(0)
        self.update_frame_display()
        
        self.play_pause_button.setText("▶")
        self.playback_timer.stop()
    
    def toggle_playback(self):
        """Toggle play/pause state."""
        if not self.current_media_path or self.total_frames <= 1:
            return
        
        if self.is_playing:
            self.pause()
        else:
            self.play()
    
    def play(self):
        """Start playback."""
        if self.total_frames <= 1:
            return
        
        self.is_playing = True
        self.play_pause_button.setText("⏸")
        
        # Start playback timer (24 fps = ~42ms per frame)
        interval = int(1000 / self.frame_rate)
        self.playback_timer.start(interval)
        
        self.playbackStateChanged.emit("playing")
    
    def pause(self):
        """Pause playback."""
        self.is_playing = False
        self.play_pause_button.setText("▶")
        self.playback_timer.stop()
        
        self.playbackStateChanged.emit("paused")
    
    def stop(self):
        """Stop playback."""
        self.pause()
        self.current_frame = 0
        self.timeline_slider.setValue(0)
        self.update_frame_display()
        
        self.playbackStateChanged.emit("stopped")
    
    def advance_frame(self):
        """Advance to next frame during playback."""
        if self.current_frame < self.total_frames - 1:
            self.current_frame += 1
            self.timeline_slider.setValue(self.current_frame)
            self.update_frame_display()
        else:
            # End of media reached
            self.pause()
    
    def go_to_first_frame(self):
        """Go to first frame."""
        self.current_frame = 0
        self.timeline_slider.setValue(0)
        self.update_frame_display()
    
    def go_to_last_frame(self):
        """Go to last frame."""
        if self.total_frames > 0:
            self.current_frame = self.total_frames - 1
            self.timeline_slider.setValue(self.current_frame)
            self.update_frame_display()
    
    def previous_frame(self):
        """Go to previous frame."""
        if self.current_frame > 0:
            self.current_frame -= 1
            self.timeline_slider.setValue(self.current_frame)
            self.update_frame_display()
    
    def next_frame(self):
        """Go to next frame."""
        if self.current_frame < self.total_frames - 1:
            self.current_frame += 1
            self.timeline_slider.setValue(self.current_frame)
            self.update_frame_display()
    
    def on_timeline_changed(self, value: int):
        """Handle timeline slider change."""
        self.current_frame = value
        self.update_frame_display()
        
        # If this is a video, update the display for the new frame
        # (placeholder - would need actual video frame seeking)
    
    def update_frame_display(self):
        """Update frame number and timecode displays."""
        self.frame_label.setText(f"Frame: {self.current_frame + 1} / {self.total_frames}")
        
        # Calculate timecode (assuming 24fps)
        if self.frame_rate > 0:
            total_seconds = self.current_frame / self.frame_rate
            hours = int(total_seconds // 3600)
            minutes = int((total_seconds % 3600) // 60)
            seconds = int(total_seconds % 60)
            frames = int(self.current_frame % self.frame_rate)
            
            timecode = f"{hours:02d}:{minutes:02d}:{seconds:02d}:{frames:02d}"
            self.timecode_label.setText(timecode)
        
        # Emit frame change signal
        self.frameChanged.emit(self.current_frame)
    
    def set_frame_rate(self, fps: float):
        """Set playback frame rate."""
        self.frame_rate = fps
        self.fps_label.setText(f"{fps:.1f} fps")
        
        # Update playback timer if playing
        if self.is_playing:
            interval = int(1000 / self.frame_rate)
            self.playback_timer.start(interval)

    def launch_in_openrv(self):
        """Launch current media file in external OpenRV application."""
        if not self.current_media_path:
            QMessageBox.warning(self, "No Media", "No media file is currently loaded.")
            return

        if not self.openrv_available:
            QMessageBox.warning(self, "OpenRV Not Available",
                              "OpenRV is not installed or not found in system PATH.\n\n"
                              "To install OpenRV:\n"
                              "1. Visit: https://github.com/AcademySoftwareFoundation/OpenRV\n"
                              "2. Download and install OpenRV\n"
                              "3. Ensure 'rv' command is in your system PATH")
            return

        try:
            # Find OpenRV executable
            openrv_cmd = None
            for name in ['rv', 'openrv', 'RV', 'OpenRV']:
                if shutil.which(name):
                    openrv_cmd = name
                    break

            if not openrv_cmd:
                # Try common installation paths
                common_paths = [
                    '/usr/local/bin/rv',
                    '/opt/rv/bin/rv',
                    'C:\\Program Files\\Tweak\\RV\\bin\\rv.exe',
                    'C:\\Program Files\\OpenRV\\bin\\rv.exe'
                ]

                for path in common_paths:
                    if os.path.exists(path):
                        openrv_cmd = path
                        break

            if not openrv_cmd:
                QMessageBox.critical(self, "OpenRV Not Found",
                                   "OpenRV executable not found. Please check your installation.")
                return

            # Launch OpenRV with the media file
            if hasattr(self, 'openrv_process') and self.openrv_process and self.openrv_process.state() == QProcess.Running:
                self.openrv_process.kill()
                self.openrv_process.waitForFinished(3000)

            self.openrv_process = QProcess(self)
            self.openrv_process.finished.connect(self.on_openrv_finished)

            # OpenRV command line arguments
            args = [self.current_media_path]

            # Add color space if specified
            if hasattr(self, 'colorspace_combo'):
                colorspace = self.colorspace_combo.currentText()
                if colorspace != "sRGB":
                    args.extend(["-c", colorspace])

            # Add frame rate
            if hasattr(self, 'fps_spinbox'):
                fps = self.fps_spinbox.value()
                if fps != 24:
                    args.extend(["-fps", str(fps)])

            print(f"Launching OpenRV: {openrv_cmd} {' '.join(args)}")
            self.openrv_process.start(openrv_cmd, args)

            if self.openrv_process.waitForStarted(5000):
                self.openrvLaunched.emit(self.current_media_path)
                QMessageBox.information(self, "OpenRV Launched",
                                      f"OpenRV launched successfully with:\n{os.path.basename(self.current_media_path)}")
            else:
                QMessageBox.critical(self, "Launch Failed",
                                   "Failed to launch OpenRV. Please check your installation.")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error launching OpenRV: {str(e)}")

    def on_openrv_finished(self, exit_code):
        """Handle OpenRV process finished."""
        print(f"OpenRV process finished with exit code: {exit_code}")
        if hasattr(self, 'openrv_process'):
            self.openrv_process = None

    def load_media_with_metadata(self, media_item: Dict[str, Any]):
        """Load media with comprehensive metadata from database."""
        if hasattr(self, 'current_media_item'):
            self.current_media_item = media_item

        # Extract media information
        file_path = media_item.get('file_path', '')
        file_name = media_item.get('file_name', 'Unknown')
        media_type = media_item.get('media_type', 'unknown')
        file_extension = media_item.get('file_extension', '')
        author = media_item.get('author', 'Unknown')
        version = media_item.get('version', 'v001')
        approval_status = media_item.get('approval_status', 'pending')

        # Get metadata
        metadata = media_item.get('metadata', {})
        file_size = metadata.get('file_size', 0)
        width = metadata.get('width')
        height = metadata.get('height')
        duration = metadata.get('duration')
        color_space = metadata.get('color_space', 'Unknown')

        # Update UI with media information
        self.media_label.setText(f"📁 {file_name}")

        # Create detailed info text
        info_parts = []
        info_parts.append(f"Type: {media_type.title()} ({file_extension})")
        info_parts.append(f"Author: {author}")
        info_parts.append(f"Version: {version}")
        info_parts.append(f"Status: {approval_status.title()}")

        if width and height:
            info_parts.append(f"Resolution: {width}x{height}")

        if duration:
            info_parts.append(f"Duration: {duration:.2f}s")

        if file_size > 0:
            size_mb = file_size / (1024 * 1024)
            info_parts.append(f"Size: {size_mb:.1f} MB")

        info_parts.append(f"Color Space: {color_space}")

        # Handle virtual media files (database entries without physical files)
        if not os.path.exists(file_path):
            info_parts.append("⚠️ Virtual Media File (Database Entry)")
            info_parts.append("Physical file not available for playback")
            if hasattr(self, 'launch_openrv_btn'):
                self.launch_openrv_btn.setEnabled(False)
                self.launch_openrv_btn.setToolTip("Physical media file not available")
        else:
            if hasattr(self, 'launch_openrv_btn'):
                self.launch_openrv_btn.setEnabled(self.openrv_available)
                self.launch_openrv_btn.setToolTip("Launch in OpenRV for professional review")

        # Update info display if available
        info_text = " | ".join(info_parts)
        print(f"Media Info: {info_text}")  # Debug output

        # Set current media path
        self.current_media_path = file_path

        # Update frame information for videos
        if media_type == 'video' and duration:
            fps = 24.0  # Default FPS
            if hasattr(self, 'fps_spinbox'):
                fps = self.fps_spinbox.value()
            self.total_frames = int(duration * fps)
            self.frame_rate = fps
            self.timeline_slider.setMaximum(max(0, self.total_frames - 1))
        else:
            self.total_frames = 1
            self.timeline_slider.setMaximum(0)

        self.current_frame = 0
        self.timeline_slider.setValue(0)
        self.update_frame_display()

        # Emit signal
        self.mediaLoaded.emit(file_path)

    def on_fps_changed(self, fps):
        """Handle FPS change."""
        self.frame_rate = fps
        if hasattr(self, 'fps_label'):
            self.fps_label.setText(f"{fps:.1f} fps")

        # Update playback timer if playing
        if self.is_playing:
            interval = int(1000 / self.frame_rate)
            self.playback_timer.start(interval)

    def on_colorspace_changed(self, colorspace):
        """Handle color space change."""
        print(f"Color space changed to: {colorspace}")
        # This would be used for display color management in a full implementation
