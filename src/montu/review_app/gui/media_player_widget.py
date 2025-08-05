"""
Media Player Widget

Widget for video/image playback with frame-accurate scrubbing
and multiple format support for the Review Application.
"""

import os
from typing import Optional
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QSlider, QGroupBox, QFrame, QSizePolicy
)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QPixmap, QFont


class MediaPlayerWidget(QWidget):
    """
    Media player widget for video and image playback.
    
    Provides playback controls, frame scrubbing, and format support
    for reviewing media files in the Review Application.
    """
    
    # Signals
    mediaLoaded = Signal(str)           # file_path
    playbackStateChanged = Signal(str)  # state (playing, paused, stopped)
    frameChanged = Signal(int)          # frame_number
    
    def __init__(self, parent=None):
        """Initialize media player widget."""
        super().__init__(parent)
        
        # State
        self.current_media_path: Optional[str] = None
        self.is_playing = False
        self.current_frame = 0
        self.total_frames = 0
        self.frame_rate = 24.0
        
        # Playback timer
        self.playback_timer = QTimer()
        self.playback_timer.timeout.connect(self.advance_frame)
        
        # Setup UI
        self.setup_ui()
        self.setup_connections()
    
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
