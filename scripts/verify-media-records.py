#!/usr/bin/env python3
"""
Verify Media Records

Simple script to verify the created media records and show statistics.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

def main():
    """Verify media records and show statistics."""
    try:
        from montu.shared.json_database import JSONDatabase
        
        db = JSONDatabase()
        media_records = db.find('media_records', {})
        
        print(f'📊 Media Records Summary:')
        print(f'Total records: {len(media_records)}')
        print()
        
        # Group by task
        task_groups = {}
        for record in media_records:
            task_id = record['linked_task_id']
            if task_id not in task_groups:
                task_groups[task_id] = []
            task_groups[task_id].append(record)
        
        print('🎬 Media by Task (first 5):')
        for i, (task_id, records) in enumerate(list(task_groups.items())[:5]):
            print(f'  {i+1}. {task_id}:')
            for record in records:
                status = record['approval_status']
                version = record['linked_version']
                filename = record['file_name']
                author = record['author']
                print(f'     - {version} | {status} | {author} | {filename}')
            print()
        
        # Status distribution
        status_counts = {}
        for record in media_records:
            status = record['approval_status']
            status_counts[status] = status_counts.get(status, 0) + 1
        
        print(f'📈 Approval Status Distribution:')
        for status, count in status_counts.items():
            print(f'  {status}: {count}')
        print()
        
        # File type distribution
        type_counts = {}
        for record in media_records:
            ext = record['file_extension']
            type_counts[ext] = type_counts.get(ext, 0) + 1
        
        print(f'📁 File Type Distribution:')
        for ext, count in type_counts.items():
            print(f'  {ext}: {count}')
        print()
        
        # Artist distribution
        artist_counts = {}
        for record in media_records:
            artist = record['author']
            artist_counts[artist] = artist_counts.get(artist, 0) + 1
        
        print(f'👥 Artist Distribution:')
        for artist, count in artist_counts.items():
            print(f'  {artist}: {count}')
        print()
        
        # Version distribution
        version_counts = {}
        for record in media_records:
            version = record['linked_version']
            version_counts[version] = version_counts.get(version, 0) + 1
        
        print(f'🔢 Version Distribution:')
        for version, count in version_counts.items():
            print(f'  {version}: {count}')
        print()
        
        # Sample metadata
        print('📋 Sample Media Record:')
        if media_records:
            sample = media_records[0]
            print(f'  ID: {sample["_id"]}')
            print(f'  Task: {sample["linked_task_id"]}')
            print(f'  File: {sample["file_name"]}')
            print(f'  Type: {sample["media_type"]} ({sample["file_extension"]})')
            print(f'  Author: {sample["author"]}')
            print(f'  Status: {sample["approval_status"]}')
            print(f'  Version: {sample["linked_version"]}')
            print(f'  Size: {sample["metadata"]["file_size"]:,} bytes')
            if sample["metadata"]["width"]:
                print(f'  Resolution: {sample["metadata"]["width"]}x{sample["metadata"]["height"]}')
            print(f'  Upload: {sample["upload_time"]}')
        
        print('\n✅ Media records verification complete!')
        
    except Exception as e:
        print(f'❌ Verification failed: {e}')
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
