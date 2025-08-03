"""
Task Creator CSV Parser

Intelligent CSV parsing with automatic naming pattern detection
and configurable field mapping for task creation.
"""

import csv
import re
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
import pandas as pd


@dataclass
class NamingPattern:
    """Represents a detected naming pattern for episodes, sequences, and shots."""
    episode_pattern: str
    sequence_pattern: str
    shot_pattern: str
    delimiter: str = "_"
    confidence: float = 0.0


@dataclass
class TaskRecord:
    """Represents a single task record to be created."""
    task_id: str
    project: str
    type: str
    episode: str
    sequence: str
    shot: str
    task: str
    artist: str
    status: str
    milestone: str
    priority: str
    frame_range: Dict[str, int]
    estimated_duration_hours: float
    start_time: Optional[str] = None
    deadline: Optional[str] = None
    actual_time_logged: float = 0.0
    milestone_note: str = ""
    versions: List[Dict] = None
    client_submission_history: List[Dict] = None

    # Enhanced fields for path generation
    current_version: str = "v001"
    published_version: str = "v000"
    file_extension: str = ".ma"
    master_file: bool = True
    working_file_path: str = ""
    render_output_path: str = ""
    media_file_path: str = ""
    cache_file_path: str = ""
    filename: str = ""
    sequence_clean: str = ""
    shot_clean: str = ""
    episode_clean: str = ""

    def __post_init__(self):
        if self.versions is None:
            self.versions = []
        if self.client_submission_history is None:
            self.client_submission_history = []

    def to_dict(self) -> Dict[str, Any]:
        """Convert TaskRecord to dictionary for JSON serialization."""
        return {
            '_id': self.task_id,
            'project': self.project,
            'type': self.type,
            'episode': self.episode,
            'sequence': self.sequence,
            'shot': self.shot,
            'task': self.task,
            'artist': self.artist,
            'status': self.status,
            'milestone': self.milestone,
            'milestone_note': self.milestone_note,
            'frame_range': self.frame_range,
            'priority': self.priority,
            'start_time': self.start_time,
            'deadline': self.deadline,
            'actual_time_logged': self.actual_time_logged,
            'estimated_duration_hours': self.estimated_duration_hours,
            'versions': self.versions,
            'client_submission_history': self.client_submission_history,

            # Enhanced fields for path generation
            'current_version': self.current_version,
            'published_version': self.published_version,
            'file_extension': self.file_extension,
            'master_file': self.master_file,
            'working_file_path': self.working_file_path,
            'render_output_path': self.render_output_path,
            'media_file_path': self.media_file_path,
            'cache_file_path': self.cache_file_path,
            'filename': self.filename,
            'sequence_clean': self.sequence_clean,
            'shot_clean': self.shot_clean,
            'episode_clean': self.episode_clean
        }


class CSVParser:
    """Intelligent CSV parser for task creation."""
    
    def __init__(self):
        self.naming_patterns: List[NamingPattern] = []
        self.default_values = {
            'artist': 'Unassigned',
            'status': 'not_started',
            'milestone': 'not_started',
            'priority': 'medium',
            'estimated_duration_hours': 24.0,  # 3 days * 8 hours
            'actual_time_logged': 0.0,
            'milestone_note': 'Imported from CSV'
        }

        # Task type to file extension mapping
        self.task_extensions = {
            'lighting': '.ma',
            'composite': '.nk',
            'comp': '.nk',
            'modeling': '.ma',
            'rigging': '.ma',
            'animation': '.ma',
            'fx': '.hip',
            'lookdev': '.ma',
            'layout': '.ma',
            'texturing': '.ma',
            'surfacing': '.ma'
        }
    
    def detect_naming_patterns(self, sample_data: List[Dict[str, Any]]) -> List[NamingPattern]:
        """
        Automatically detect naming patterns from sample data.
        
        Args:
            sample_data: List of dictionaries representing CSV rows
            
        Returns:
            List of detected naming patterns sorted by confidence
        """
        patterns = []
        
        # Analyze sequence and shot naming patterns
        sequences = set()
        shots = set()
        episodes = set()
        
        for row in sample_data:
            if 'Sequence' in row and row['Sequence']:
                sequences.add(row['Sequence'])
            if 'Shot' in row and row['Shot']:
                shots.add(row['Shot'])
            if 'Episode' in row and row['Episode']:
                episodes.add(row['Episode'])
        
        # Pattern 1: Standard pipeline naming (Project_Episode_Sequence, Project_Episode_Shot)
        if sequences and shots:
            sample_seq = next(iter(sequences))
            sample_shot = next(iter(shots))
            sample_ep = next(iter(episodes)) if episodes else ""
            
            # Analyze delimiter and structure
            for delimiter in ['_', '-', '.']:
                seq_parts = sample_seq.split(delimiter)
                shot_parts = sample_shot.split(delimiter)
                
                if len(seq_parts) >= 3 and len(shot_parts) >= 3:
                    # Calculate confidence based on consistency
                    confidence = self._calculate_pattern_confidence(
                        sequences, shots, episodes, delimiter
                    )
                    
                    pattern = NamingPattern(
                        episode_pattern=f"part[1]",  # Second part after project
                        sequence_pattern=f"part[2]",  # Third part
                        shot_pattern=f"part[2]",     # Third part for shots
                        delimiter=delimiter,
                        confidence=confidence
                    )
                    patterns.append(pattern)
        
        # Sort by confidence
        patterns.sort(key=lambda p: p.confidence, reverse=True)
        return patterns
    
    def _calculate_pattern_confidence(self, sequences: set, shots: set, 
                                    episodes: set, delimiter: str) -> float:
        """Calculate confidence score for a naming pattern."""
        total_items = len(sequences) + len(shots) + len(episodes)
        if total_items == 0:
            return 0.0
        
        consistent_items = 0
        
        # Check consistency of delimiter usage
        for item in list(sequences) + list(shots) + list(episodes):
            if delimiter in item:
                parts = item.split(delimiter)
                if len(parts) >= 3:  # Project_Episode_Sequence/Shot format
                    consistent_items += 1
        
        return consistent_items / total_items
    
    def generate_task_id(self, project: str, episode: str, sequence: str, 
                        shot: str, task: str) -> str:
        """
        Generate a readable task ID following the PRD pattern.
        
        Alternative ID generation patterns for better scalability:
        
        1. Current PRD Pattern: "ep01_seq0010_sh0010_lighting"
           - Pros: Human readable, follows episode/sequence/shot hierarchy
           - Cons: Can become long, assumes specific naming conventions
        
        2. Hash-based Pattern: "swa_a1b2c3d4_lighting" 
           - Pros: Shorter, guaranteed unique, scalable
           - Cons: Less human readable
        
        3. Hierarchical Pattern: "swa.ep01.sq0010.sh0010.lighting"
           - Pros: Clear hierarchy, extensible, readable
           - Cons: Longer than hash-based
        
        4. Hybrid Pattern: "swa_ep01_a1b2_lighting" (project_episode_hash_task)
           - Pros: Balance of readability and uniqueness
           - Cons: Requires hash collision handling
        
        Recommendation: Use the PRD pattern for now, but make it configurable
        for future scalability needs.
        """
        
        # Clean and normalize components
        project_clean = self._clean_identifier(project)
        episode_clean = self._clean_identifier(episode)
        sequence_clean = self._clean_identifier(sequence)
        shot_clean = self._clean_identifier(shot)
        task_clean = self._clean_identifier(task)
        
        # Generate ID using PRD pattern
        task_id = f"{episode_clean}_{sequence_clean}_{shot_clean}_{task_clean}"
        
        return task_id.lower()
    
    def _clean_identifier(self, identifier: str) -> str:
        """Clean identifier for use in task IDs."""
        if not identifier:
            return "unknown"
        
        # Remove project prefix if present (e.g., "SWA_Ep00" -> "Ep00")
        # But preserve original naming as requested
        cleaned = re.sub(r'^[A-Z]+_', '', identifier)
        
        # Replace spaces and special characters with underscores
        cleaned = re.sub(r'[^\w]', '_', cleaned)
        
        # Remove multiple underscores
        cleaned = re.sub(r'_+', '_', cleaned)
        
        # Remove leading/trailing underscores
        cleaned = cleaned.strip('_')
        
        return cleaned if cleaned else "unknown"
    
    def parse_csv_file(self, file_path: Path, naming_pattern: Optional[NamingPattern] = None) -> List[TaskRecord]:
        """
        Parse CSV file and convert to task records.
        
        Args:
            file_path: Path to CSV file
            naming_pattern: Optional naming pattern to use (auto-detect if None)
            
        Returns:
            List of TaskRecord objects
        """
        # Read CSV file
        df = pd.read_csv(file_path)
        
        # Convert to list of dictionaries
        data = df.to_dict('records')
        
        # Auto-detect naming pattern if not provided
        if naming_pattern is None:
            patterns = self.detect_naming_patterns(data)
            naming_pattern = patterns[0] if patterns else NamingPattern("", "", "")
        
        # Parse tasks
        tasks = []
        for row in data:
            # Extract multiple tasks from single row
            row_tasks = self._extract_tasks_from_row(row, naming_pattern)
            tasks.extend(row_tasks)
        
        return tasks
    
    def _extract_tasks_from_row(self, row: Dict[str, Any], 
                               naming_pattern: NamingPattern) -> List[TaskRecord]:
        """Extract multiple task records from a single CSV row."""
        tasks = []
        
        # Extract basic information
        project = str(row.get('Project', 'Unknown'))
        episode = str(row.get('Episode', 'Unknown'))
        sequence = str(row.get('Sequence', 'Unknown'))
        shot = str(row.get('Shot', 'Unknown'))
        type_field = str(row.get('Type', 'shot')).lower()
        
        # Extract frame range
        frame_range = {
            'start': int(row.get('Cut In', 1001)),
            'end': int(row.get('Cut Out', 1001))
        }
        
        # Extract tasks - handle multiple task columns
        task_columns = [col for col in row.keys() if col.startswith('Task')]
        duration_columns = [col for col in row.keys() if 'duration' in col.lower()]
        
        # Pair tasks with their durations
        task_pairs = []
        task_index = 0
        duration_index = 0
        
        for i, col in enumerate(row.keys()):
            if col.startswith('Task') and not 'duration' in col.lower():
                task_name = str(row[col])
                duration = 3.0  # Default 3 days
                
                # Try to find corresponding duration
                if duration_index < len(duration_columns):
                    duration_col = duration_columns[duration_index]
                    try:
                        duration = float(row[duration_col])
                    except (ValueError, TypeError):
                        duration = 3.0
                    duration_index += 1
                
                if task_name and task_name.strip() and task_name != 'nan':
                    task_pairs.append((task_name.strip(), duration))
                task_index += 1
        
        # Create task records
        for task_name, duration_days in task_pairs:
            task_id = self.generate_task_id(project, episode, sequence, shot, task_name)

            # Get appropriate file extension for task type
            file_extension = self.task_extensions.get(task_name.lower(), '.ma')

            task_record = TaskRecord(
                task_id=task_id,
                project=project,
                type=type_field,
                episode=episode,
                sequence=sequence,
                shot=shot,
                task=task_name,
                artist=self.default_values['artist'],
                status=self.default_values['status'],
                milestone=self.default_values['milestone'],
                priority=self.default_values['priority'],
                frame_range=frame_range,
                estimated_duration_hours=duration_days * 8.0,  # Convert days to hours
                actual_time_logged=self.default_values['actual_time_logged'],
                milestone_note=self.default_values['milestone_note'],

                # Enhanced fields
                current_version="v001",
                published_version="v000",
                file_extension=file_extension,
                master_file=True,
                working_file_path="",  # Will be generated by Path Builder
                render_output_path="",  # Will be generated by Path Builder
                media_file_path="",     # Will be generated by Path Builder
                cache_file_path="",     # Will be generated by Path Builder
                filename="",            # Will be generated by Path Builder
                sequence_clean="",      # Will be generated by Path Builder
                shot_clean="",          # Will be generated by Path Builder
                episode_clean=""        # Will be generated by Path Builder
            )

            tasks.append(task_record)
        
        return tasks
    
    def validate_tasks(self, tasks: List[TaskRecord]) -> Tuple[List[TaskRecord], List[str]]:
        """
        Validate task records and return valid tasks and error messages.
        
        Args:
            tasks: List of task records to validate
            
        Returns:
            Tuple of (valid_tasks, error_messages)
        """
        valid_tasks = []
        errors = []
        
        seen_ids = set()
        
        for i, task in enumerate(tasks):
            # Check for duplicate task IDs
            if task.task_id in seen_ids:
                errors.append(f"Row {i+1}: Duplicate task ID '{task.task_id}'")
                continue
            
            # Validate required fields
            if not task.project:
                errors.append(f"Row {i+1}: Missing project")
                continue
            
            if not task.task:
                errors.append(f"Row {i+1}: Missing task name")
                continue
            
            # Validate frame range
            if task.frame_range['start'] >= task.frame_range['end']:
                errors.append(f"Row {i+1}: Invalid frame range {task.frame_range}")
                continue
            
            seen_ids.add(task.task_id)
            valid_tasks.append(task)
        
        return valid_tasks, errors
