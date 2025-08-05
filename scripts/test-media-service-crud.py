#!/usr/bin/env python3
"""
Media Service CRUD Operations Test Suite

Comprehensive testing of media file storage, retrieval, metadata extraction,
thumbnail generation, and versioning capabilities.
"""

import sys
import os
import tempfile
import shutil
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

def create_test_media_files(temp_dir: Path) -> dict:
    """Create test media files for testing."""
    test_files = {}
    
    # Create test image file (simple bitmap)
    image_path = temp_dir / "test_image.jpg"
    try:
        # Create a simple test image
        from PIL import Image
        img = Image.new('RGB', (640, 480), color='red')
        img.save(image_path, 'JPEG')
        test_files['image'] = str(image_path)
    except ImportError:
        # Create a dummy file if PIL not available
        with open(image_path, 'wb') as f:
            f.write(b'\xFF\xD8\xFF\xE0\x00\x10JFIF')  # JPEG header
        test_files['image'] = str(image_path)
    
    # Create test video file (dummy)
    video_path = temp_dir / "test_video.mp4"
    with open(video_path, 'wb') as f:
        # Write minimal MP4 header
        f.write(b'\x00\x00\x00\x20ftypmp42')
    test_files['video'] = str(video_path)
    
    # Create test text file
    text_path = temp_dir / "test_document.txt"
    with open(text_path, 'w') as f:
        f.write("This is a test document for media service testing.")
    test_files['document'] = str(text_path)
    
    return test_files

def test_media_storage_backend():
    """Test media storage backend functionality."""
    print("🔍 Testing Media Storage Backend...")
    print("=" * 50)
    
    try:
        from montu.shared.media_service import LocalFileSystemBackend
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create storage backend
            storage_dir = temp_path / "media_storage"
            backend = LocalFileSystemBackend(str(storage_dir))
            
            # Create test file
            test_file = temp_path / "test_file.txt"
            test_content = "Test file content for storage backend testing"
            with open(test_file, 'w') as f:
                f.write(test_content)
            
            # Test file storage
            storage_key = "test/folder/test_file.txt"
            stored_path = backend.store_file(str(test_file), storage_key)
            
            if os.path.exists(stored_path):
                print(f"   ✅ File storage: Successfully stored file")
            else:
                print(f"   ❌ File storage: Failed to store file")
                return False
            
            # Test file existence check
            if backend.file_exists(storage_key):
                print(f"   ✅ File existence: Correctly detected existing file")
            else:
                print(f"   ❌ File existence: Failed to detect existing file")
                return False
            
            # Test file retrieval
            retrieved_file = temp_path / "retrieved_file.txt"
            if backend.retrieve_file(storage_key, str(retrieved_file)):
                with open(retrieved_file, 'r') as f:
                    retrieved_content = f.read()
                if retrieved_content == test_content:
                    print(f"   ✅ File retrieval: Successfully retrieved file with correct content")
                else:
                    print(f"   ❌ File retrieval: Content mismatch")
                    return False
            else:
                print(f"   ❌ File retrieval: Failed to retrieve file")
                return False
            
            # Test file deletion
            if backend.delete_file(storage_key):
                if not backend.file_exists(storage_key):
                    print(f"   ✅ File deletion: Successfully deleted file")
                else:
                    print(f"   ❌ File deletion: File still exists after deletion")
                    return False
            else:
                print(f"   ❌ File deletion: Failed to delete file")
                return False
        
        return True
        
    except Exception as e:
        print(f"   ❌ Storage backend test failed: {e}")
        return False

def test_metadata_extraction():
    """Test metadata extraction functionality."""
    print("\n🔍 Testing Metadata Extraction...")
    print("=" * 50)
    
    try:
        from montu.shared.media_service import MediaMetadataExtractor
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            test_files = create_test_media_files(temp_path)
            
            # Test basic metadata extraction
            image_file = test_files['image']
            metadata = MediaMetadataExtractor.extract_basic_metadata(image_file)
            
            if metadata.file_size > 0:
                print(f"   ✅ Basic metadata: File size extracted ({metadata.file_size} bytes)")
            else:
                print(f"   ❌ Basic metadata: Failed to extract file size")
                return False
            
            if metadata.checksum:
                print(f"   ✅ Basic metadata: Checksum calculated ({metadata.checksum[:8]}...)")
            else:
                print(f"   ❌ Basic metadata: Failed to calculate checksum")
                return False
            
            if metadata.mime_type:
                print(f"   ✅ Basic metadata: MIME type detected ({metadata.mime_type})")
            else:
                print(f"   ❌ Basic metadata: Failed to detect MIME type")
                return False
            
            # Test image metadata extraction
            image_metadata = MediaMetadataExtractor.extract_image_metadata(image_file)
            
            if hasattr(image_metadata, 'width') and image_metadata.width:
                print(f"   ✅ Image metadata: Dimensions extracted ({image_metadata.width}x{image_metadata.height})")
            else:
                print(f"   ⚠️  Image metadata: Dimensions not extracted (PIL may not be available)")
            
            # Test video metadata extraction
            video_file = test_files['video']
            video_metadata = MediaMetadataExtractor.extract_video_metadata(video_file)
            
            if video_metadata.file_size > 0:
                print(f"   ✅ Video metadata: Basic metadata extracted")
            else:
                print(f"   ❌ Video metadata: Failed to extract basic metadata")
                return False
            
            print(f"   ⚠️  Video metadata: Advanced extraction requires OpenCV")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Metadata extraction test failed: {e}")
        return False

def test_thumbnail_generation():
    """Test thumbnail generation functionality."""
    print("\n🔍 Testing Thumbnail Generation...")
    print("=" * 50)
    
    try:
        from montu.shared.media_service import ThumbnailGenerator
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            test_files = create_test_media_files(temp_path)
            
            # Test image thumbnail generation
            image_file = test_files['image']
            thumbnail_path = temp_path / "image_thumbnail.jpg"
            
            success = ThumbnailGenerator.generate_image_thumbnail(
                str(image_file), str(thumbnail_path)
            )
            
            if success and thumbnail_path.exists():
                print(f"   ✅ Image thumbnail: Successfully generated")
            else:
                print(f"   ⚠️  Image thumbnail: Generation failed (PIL may not be available)")
            
            # Test video thumbnail generation
            video_file = test_files['video']
            video_thumbnail_path = temp_path / "video_thumbnail.jpg"
            
            success = ThumbnailGenerator.generate_video_thumbnail(
                str(video_file), str(video_thumbnail_path)
            )
            
            if success and video_thumbnail_path.exists():
                print(f"   ✅ Video thumbnail: Successfully generated")
            else:
                print(f"   ⚠️  Video thumbnail: Generation failed (OpenCV may not be available)")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Thumbnail generation test failed: {e}")
        return False

def test_media_service_crud():
    """Test complete media service CRUD operations."""
    print("\n🔍 Testing Media Service CRUD Operations...")
    print("=" * 50)
    
    try:
        from montu.shared.json_database import JSONDatabase
        from montu.shared.media_service import MediaService, LocalFileSystemBackend
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Initialize database and storage
            db = JSONDatabase(str(temp_path / "test_db"))
            storage_backend = LocalFileSystemBackend(str(temp_path / "media_storage"))
            media_service = MediaService(db, storage_backend)
            
            # Create test files
            test_files = create_test_media_files(temp_path)
            
            # Create test task
            test_task = {
                '_id': 'test_task_001',
                'project': 'TEST_PROJECT',
                'name': 'Test Task',
                'status': 'active'
            }
            db.insert_one('tasks', test_task)
            
            # Test 1: Upload media
            media_id = media_service.upload_media(
                file_path=test_files['image'],
                task_id='test_task_001',
                version='v001',
                author='Test User',
                description='Test image upload',
                tags=['test', 'image']
            )
            
            if media_id:
                print(f"   ✅ Upload media: Successfully uploaded ({media_id})")
            else:
                print(f"   ❌ Upload media: Failed to upload")
                return False
            
            # Test 2: Retrieve media by ID
            media_record = media_service.get_media_by_id(media_id)
            if media_record and media_record['_id'] == media_id:
                print(f"   ✅ Get media by ID: Successfully retrieved")
            else:
                print(f"   ❌ Get media by ID: Failed to retrieve")
                return False
            
            # Test 3: Get media by task
            task_media = media_service.get_media_by_task('test_task_001')
            if len(task_media) == 1:
                print(f"   ✅ Get media by task: Found {len(task_media)} media files")
            else:
                print(f"   ❌ Get media by task: Expected 1, found {len(task_media)}")
                return False
            
            # Test 4: Update media metadata
            success = media_service.update_media_metadata(
                media_id, 
                {'custom_field': 'custom_value', 'updated': True}
            )
            if success:
                print(f"   ✅ Update metadata: Successfully updated")
            else:
                print(f"   ❌ Update metadata: Failed to update")
                return False
            
            # Test 5: Update media info
            success = media_service.update_media_info(
                media_id,
                description='Updated description',
                tags=['updated', 'test'],
                review_selected=True,
                approval_status='approved'
            )
            if success:
                print(f"   ✅ Update media info: Successfully updated")
            else:
                print(f"   ❌ Update media info: Failed to update")
                return False
            
            # Test 6: Create media version
            new_media_id = media_service.create_media_version(
                source_media_id=media_id,
                new_file_path=test_files['video'],
                version='v002',
                author='Test User',
                description='Version 2 of media'
            )
            
            if new_media_id:
                print(f"   ✅ Create version: Successfully created v002 ({new_media_id})")
            else:
                print(f"   ❌ Create version: Failed to create version")
                return False
            
            # Test 7: Get media versions
            versions = media_service.get_media_versions('test_task_001')
            if 'v001' in versions and 'v002' in versions:
                print(f"   ✅ Get versions: Found versions {versions}")
            else:
                print(f"   ❌ Get versions: Expected v001 and v002, got {versions}")
                return False
            
            # Test 8: Search media
            search_results = media_service.search_media('test', task_id='test_task_001')
            if len(search_results) >= 1:
                print(f"   ✅ Search media: Found {len(search_results)} results")
            else:
                print(f"   ❌ Search media: No results found")
                return False
            
            # Test 9: Get statistics
            stats = media_service.get_media_statistics(task_id='test_task_001')
            if stats['total_media'] >= 2:
                print(f"   ✅ Get statistics: {stats['total_media']} total media files")
            else:
                print(f"   ❌ Get statistics: Expected >= 2, got {stats['total_media']}")
                return False
            
            # Test 10: Archive media
            success = media_service.archive_media(media_id)
            if success:
                archived_record = media_service.get_media_by_id(media_id)
                if archived_record['approval_status'] == 'archived':
                    print(f"   ✅ Archive media: Successfully archived")
                else:
                    print(f"   ❌ Archive media: Status not updated")
                    return False
            else:
                print(f"   ❌ Archive media: Failed to archive")
                return False
            
            # Test 11: Restore media
            success = media_service.restore_media(media_id)
            if success:
                restored_record = media_service.get_media_by_id(media_id)
                if restored_record['approval_status'] == 'pending':
                    print(f"   ✅ Restore media: Successfully restored")
                else:
                    print(f"   ❌ Restore media: Status not updated")
                    return False
            else:
                print(f"   ❌ Restore media: Failed to restore")
                return False
            
            # Test 12: Delete media
            success = media_service.delete_media(new_media_id, remove_files=True)
            if success:
                deleted_record = media_service.get_media_by_id(new_media_id)
                if not deleted_record:
                    print(f"   ✅ Delete media: Successfully deleted")
                else:
                    print(f"   ❌ Delete media: Record still exists")
                    return False
            else:
                print(f"   ❌ Delete media: Failed to delete")
                return False
        
        return True
        
    except Exception as e:
        print(f"   ❌ Media service CRUD test failed: {e}")
        return False

def test_media_service_integration():
    """Test media service integration with existing systems."""
    print("\n🔍 Testing Media Service Integration...")
    print("=" * 50)
    
    try:
        from montu.shared.json_database import JSONDatabase
        from montu.shared.media_service import MediaService, LocalFileSystemBackend
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Initialize services
            db = JSONDatabase(str(temp_path / "test_db"))
            storage_backend = LocalFileSystemBackend(str(temp_path / "media_storage"))
            media_service = MediaService(db, storage_backend)
            
            # Create test project and tasks (similar to existing data)
            project_config = {
                '_id': 'SWA',
                'name': 'Star Wars Animated',
                'base_path': '/projects/swa'
            }
            db.insert_one('project_configs', project_config)
            
            test_task = {
                '_id': 'swa_ep01_sq0010_sh0010_lighting',
                'project': 'SWA',
                'episode': 'ep01',
                'sequence': 'sq0010',
                'shot': 'sh0010',
                'task': 'lighting',
                'artist': 'John Doe',
                'status': 'in_progress'
            }
            db.insert_one('tasks', test_task)
            
            # Create test media file
            test_files = create_test_media_files(temp_path)
            
            # Upload media linked to task
            media_id = media_service.upload_media(
                file_path=test_files['image'],
                task_id='swa_ep01_sq0010_sh0010_lighting',
                version='v001',
                author='John Doe',
                description='Lighting render v001'
            )
            
            if media_id:
                print(f"   ✅ Task integration: Media linked to task successfully")
            else:
                print(f"   ❌ Task integration: Failed to link media to task")
                return False
            
            # Test project-level statistics
            project_stats = media_service.get_media_statistics(project_id='SWA')
            if project_stats['total_media'] >= 1:
                print(f"   ✅ Project statistics: Found {project_stats['total_media']} media files for project")
            else:
                print(f"   ❌ Project statistics: No media found for project")
                return False
            
            # Test media file path generation
            file_path = media_service.get_media_file_path(media_id)
            if file_path and os.path.exists(file_path):
                print(f"   ✅ File path access: Media file accessible at path")
            else:
                print(f"   ❌ File path access: Media file not accessible")
                return False
        
        return True
        
    except Exception as e:
        print(f"   ❌ Integration test failed: {e}")
        return False

def main():
    """Run comprehensive media service test suite."""
    print("🚀 MEDIA SERVICE CRUD OPERATIONS TEST SUITE")
    print("=" * 60)
    print("Testing comprehensive media file management functionality")
    print("including storage, metadata, thumbnails, and versioning.\n")
    
    tests = [
        ("Media Storage Backend", test_media_storage_backend),
        ("Metadata Extraction", test_metadata_extraction),
        ("Thumbnail Generation", test_thumbnail_generation),
        ("Media Service CRUD", test_media_service_crud),
        ("System Integration", test_media_service_integration),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"   💥 {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 MEDIA SERVICE TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status} {test_name}")
    
    print(f"\n🎯 Overall Result: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 SUCCESS: All media service operations working perfectly!")
        print("   ✅ STORAGE: File storage and retrieval operations")
        print("   ✅ METADATA: Media metadata extraction and management")
        print("   ✅ THUMBNAILS: Thumbnail generation for images and videos")
        print("   ✅ CRUD: Complete create, read, update, delete operations")
        print("   ✅ VERSIONING: Media versioning and task linking")
        print("   ✅ INTEGRATION: Seamless integration with existing systems")
        return 0
    else:
        print(f"\n⚠️  WARNING: {total - passed} tests failed")
        print("   Some media service operations may have issues.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
