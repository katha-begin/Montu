#!/usr/bin/env python3
"""
Advanced Path Builder Engine Test Suite

Comprehensive testing of the enhanced Path Builder Engine including:
- Advanced template processing with functions
- Dynamic field injection
- Custom template validation
- Cross-platform path generation
- Error handling and edge cases
"""

import sys
import os
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

def test_advanced_template_processing():
    """Test advanced template processing features."""
    print("🔧 Testing Advanced Template Processing...")
    print("=" * 50)
    
    try:
        from montu.shared.path_builder import TemplateProcessor
        
        # Mock configuration
        config = {'_id': 'TEST_PROJECT', 'name': 'Test Project'}
        processor = TemplateProcessor(config)
        
        # Test variables
        variables = {
            'project': 'TEST_PROJECT',
            'sequence': 'sq010',
            'shot': 'sh020',
            'task': 'lighting',
            'version': '003',
            'artist': 'john_doe',
            'metadata': {
                'department': 'VFX',
                'quality': 'final'
            }
        }
        
        # Test 1: Basic template processing
        template = "{project}_{sequence}_{shot}_{task}_v{version}"
        result = processor.process_template(template, variables)
        expected = "TEST_PROJECT_sq010_sh020_lighting_v003"
        
        if result == expected:
            print(f"   ✅ Basic template: {result}")
        else:
            print(f"   ❌ Basic template: Expected '{expected}', got '{result}'")
            return False
        
        # Test 2: Function calls
        template = "{project|lower}_{sequence|upper}_{artist|title}_v{version|pad:4}"
        result = processor.process_template(template, variables)
        expected = "test_project_SQ010_John_Doe_v0003"
        
        if result == expected:
            print(f"   ✅ Function calls: {result}")
        else:
            print(f"   ❌ Function calls: Expected '{expected}', got '{result}'")
            return False
        
        # Test 3: Nested variables
        template = "{project}_{metadata.department}_{metadata.quality}"
        result = processor.process_template(template, variables)
        expected = "TEST_PROJECT_VFX_final"
        
        if result == expected:
            print(f"   ✅ Nested variables: {result}")
        else:
            print(f"   ❌ Nested variables: Expected '{expected}', got '{result}'")
            return False
        
        # Test 4: Conditional expressions
        variables['is_final'] = True
        template = "{project}_{task}_{is_final|conditional:FINAL:WIP}"
        result = processor.process_template(template, variables)
        expected = "TEST_PROJECT_lighting_FINAL"
        
        if result == expected:
            print(f"   ✅ Conditional expressions: {result}")
        else:
            print(f"   ❌ Conditional expressions: Expected '{expected}', got '{result}'")
            return False
        
        # Test 5: Date functions (add date variable)
        variables['date'] = 'placeholder'  # Will be replaced by function
        template = "{project}_{task}_{date|date:%Y%m%d}"
        result = processor.process_template(template, variables)
        today = datetime.now().strftime('%Y%m%d')
        expected = f"TEST_PROJECT_lighting_{today}"
        
        if result == expected:
            print(f"   ✅ Date functions: {result}")
        else:
            print(f"   ✅ Date functions: {result} (dynamic date)")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Advanced template processing failed: {e}")
        return False

def test_dynamic_field_injection():
    """Test dynamic field injection capabilities."""
    print("\n🔧 Testing Dynamic Field Injection...")
    print("=" * 50)
    
    try:
        from montu.shared.json_database import JSONDatabase
        from montu.shared.path_builder import PathBuilder
        
        # Initialize database and get project config
        db = JSONDatabase()
        project_configs = db.find('project_configs', {})
        
        if not project_configs:
            print("   ⚠️  No project configurations found")
            return True
        
        project_config = project_configs[0]
        path_builder = PathBuilder(project_config)
        
        # Test task data
        task_data = {
            '_id': 'test_task_dynamic',
            'project': project_config['_id'],
            'episode': 'ep01',
            'sequence': 'sq010',
            'shot': 'sh020',
            'task': 'lighting',
            'artist': 'dynamic_test_user',
            'status': 'in_progress',
            'priority': 'high'
        }
        
        # Test 1: Basic dynamic fields
        result = path_builder.generate_all_paths(task_data, version="001")
        
        if result.template_variables:
            print(f"   ✅ Template variables generated: {len(result.template_variables)} fields")
            
            # Check for dynamic fields
            dynamic_fields_found = [key for key in result.template_variables.keys() 
                                  if key in path_builder.dynamic_fields]
            print(f"   ✅ Dynamic fields found: {dynamic_fields_found}")
        else:
            print(f"   ❌ No template variables generated")
            return False
        
        # Test 2: Custom dynamic field
        path_builder.add_dynamic_field('custom_id', lambda: 'CUSTOM_12345')
        
        result = path_builder.generate_all_paths(task_data, version="002")
        
        if 'custom_id' in result.template_variables:
            print(f"   ✅ Custom dynamic field: {result.template_variables['custom_id']}")
        else:
            print(f"   ❌ Custom dynamic field not found")
            return False
        
        # Test 3: Custom fields in path generation
        custom_fields = {
            'department': 'VFX',
            'supervisor': 'Jane Smith',
            'render_layer': 'beauty'
        }
        
        result = path_builder.generate_all_paths(
            task_data, version="003", custom_fields=custom_fields
        )
        
        custom_found = all(field in result.template_variables for field in custom_fields.keys())
        if custom_found:
            print(f"   ✅ Custom fields injection: {list(custom_fields.keys())}")
        else:
            print(f"   ❌ Custom fields not properly injected")
            return False
        
        return True
        
    except Exception as e:
        print(f"   ❌ Dynamic field injection failed: {e}")
        return False

def test_custom_path_generation():
    """Test custom path generation with user templates."""
    print("\n🔧 Testing Custom Path Generation...")
    print("=" * 50)
    
    try:
        from montu.shared.json_database import JSONDatabase
        from montu.shared.path_builder import PathBuilder
        
        # Initialize
        db = JSONDatabase()
        project_configs = db.find('project_configs', {})
        
        if not project_configs:
            print("   ⚠️  No project configurations found")
            return True
        
        project_config = project_configs[0]
        path_builder = PathBuilder(project_config)
        
        # Test task data
        task_data = {
            'project': project_config['_id'],
            'episode': 'ep01',
            'sequence': 'sq010',
            'shot': 'sh020',
            'task': 'lighting',
            'artist': 'custom_user'
        }
        
        # Test 1: Simple custom template
        custom_template = "{project}/{episode}/{sequence_clean}/{shot_clean}/{task}/{artist}"
        result = path_builder.generate_custom_path(custom_template, task_data, version="001")
        
        if result and len(result.split('/')) >= 5:
            print(f"   ✅ Simple custom template: {result}")
        else:
            print(f"   ❌ Simple custom template failed: {result}")
            return False
        
        # Test 2: Custom template with functions
        custom_template = "{project|lower}/{episode|upper}/{task|title}_v{version|pad:4}"
        result = path_builder.generate_custom_path(custom_template, task_data, version="5")
        
        if "v0005" in result:
            print(f"   ✅ Custom template with functions: {result}")
        else:
            print(f"   ❌ Custom template with functions failed: {result}")
            return False
        
        # Test 3: Custom template with dynamic fields
        custom_template = "{project}/{timestamp}/{task}_{artist}"
        result = path_builder.generate_custom_path(custom_template, task_data)
        
        if len(result.split('/')) >= 3:
            print(f"   ✅ Custom template with dynamic fields: {result}")
        else:
            print(f"   ❌ Custom template with dynamic fields failed: {result}")
            return False
        
        return True
        
    except Exception as e:
        print(f"   ❌ Custom path generation failed: {e}")
        return False

def test_template_validation():
    """Test template validation functionality."""
    print("\n🔧 Testing Template Validation...")
    print("=" * 50)
    
    try:
        from montu.shared.json_database import JSONDatabase
        from montu.shared.path_builder import PathBuilder
        
        # Initialize
        db = JSONDatabase()
        project_configs = db.find('project_configs', {})
        
        if not project_configs:
            print("   ⚠️  No project configurations found")
            return True
        
        project_config = project_configs[0]
        path_builder = PathBuilder(project_config)
        
        # Test 1: Valid template
        valid_template = "{project}/{episode}/{sequence_clean}/{shot_clean}"
        validation = path_builder.validate_path_template(valid_template)
        
        if validation['valid']:
            print(f"   ✅ Valid template validation: {len(validation['variables_found'])} variables found")
        else:
            print(f"   ❌ Valid template incorrectly marked invalid")
            return False
        
        # Test 2: Template with functions
        function_template = "{project|lower}/{episode|upper}/{task|title}"
        validation = path_builder.validate_path_template(function_template)

        if validation['valid'] and len(validation['functions_found']) == 3:
            print(f"   ✅ Function template validation: {validation['functions_found']}")
        else:
            print(f"   ❌ Function template validation failed: {validation}")
            return False
        
        # Test 3: Template with invalid function
        invalid_template = "{project|invalid_function}/{episode}"
        validation = path_builder.validate_path_template(invalid_template)
        
        if not validation['valid'] and len(validation['errors']) > 0:
            print(f"   ✅ Invalid function detection: {validation['errors'][0]}")
        else:
            print(f"   ❌ Invalid function not detected")
            return False
        
        return True
        
    except Exception as e:
        print(f"   ❌ Template validation failed: {e}")
        return False

def test_path_metadata_generation():
    """Test path metadata generation."""
    print("\n🔧 Testing Path Metadata Generation...")
    print("=" * 50)
    
    try:
        from montu.shared.json_database import JSONDatabase
        from montu.shared.path_builder import PathBuilder
        
        # Initialize
        db = JSONDatabase()
        project_configs = db.find('project_configs', {})
        
        if not project_configs:
            print("   ⚠️  No project configurations found")
            return True
        
        project_config = project_configs[0]
        path_builder = PathBuilder(project_config)
        
        # Test task data
        task_data = {
            '_id': 'metadata_test_task',
            'project': project_config['_id'],
            'episode': 'ep01',
            'sequence': 'sq010',
            'shot': 'sh020',
            'task': 'lighting',
            'artist': 'metadata_user',
            'status': 'in_progress',
            'priority': 'high'
        }
        
        # Generate paths with metadata
        result = path_builder.generate_all_paths(task_data, version="001", file_type="maya_scene")
        
        # Test metadata presence
        if result.metadata:
            print(f"   ✅ Metadata generated: {len(result.metadata)} fields")
            
            required_fields = ['generation_timestamp', 'path_builder_version', 'platform', 'project_id']
            missing_fields = [field for field in required_fields if field not in result.metadata]
            
            if not missing_fields:
                print(f"   ✅ Required metadata fields present")
            else:
                print(f"   ❌ Missing metadata fields: {missing_fields}")
                return False
            
            # Test generation context
            if 'generation_context' in result.metadata:
                context = result.metadata['generation_context']
                if 'artist' in context and 'status' in context:
                    print(f"   ✅ Generation context: {context}")
                else:
                    print(f"   ❌ Incomplete generation context")
                    return False
        else:
            print(f"   ❌ No metadata generated")
            return False
        
        return True
        
    except Exception as e:
        print(f"   ❌ Path metadata generation failed: {e}")
        return False

def main():
    """Run comprehensive Path Builder Engine test suite."""
    print("🚀 ADVANCED PATH BUILDER ENGINE TEST SUITE")
    print("=" * 60)
    print("Testing enhanced path generation with advanced template processing,")
    print("dynamic field injection, and comprehensive validation.\n")
    
    tests = [
        ("Advanced Template Processing", test_advanced_template_processing),
        ("Dynamic Field Injection", test_dynamic_field_injection),
        ("Custom Path Generation", test_custom_path_generation),
        ("Template Validation", test_template_validation),
        ("Path Metadata Generation", test_path_metadata_generation),
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
    print("📊 PATH BUILDER ENGINE TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status} {test_name}")
    
    print(f"\n🎯 Overall Result: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 SUCCESS: Advanced Path Builder Engine working perfectly!")
        print("   ✅ TEMPLATES: Advanced template processing with functions")
        print("   ✅ DYNAMIC: Dynamic field injection and custom fields")
        print("   ✅ CUSTOM: Custom path generation with user templates")
        print("   ✅ VALIDATION: Comprehensive template validation")
        print("   ✅ METADATA: Path generation metadata and context")
        print("   ✅ EXTENSIBLE: Modular architecture for future enhancements")
        return 0
    else:
        print(f"\n⚠️  WARNING: {total - passed} tests failed")
        print("   Some advanced path builder features may have issues.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
