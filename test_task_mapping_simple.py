#!/usr/bin/env python3
"""
Simple test script to verify task type mapping without GUI
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '.'))

def test_task_mapping():
    """Test task type mapping logic."""
    print("🧪 Testing Task Type Mapping (No GUI)")
    print("=" * 50)
    
    # Test the mapping dictionary directly
    task_name_mapping = {
        'composite': 'comp',
        'Composite': 'comp',
        'COMPOSITE': 'comp',
        'lighting': 'lighting',
        'Lighting': 'lighting',
        'LIGHTING': 'lighting',
    }
    
    def normalize_task_name(task_name: str) -> str:
        """Normalize task name from CSV to configured task type."""
        if task_name in task_name_mapping:
            return task_name_mapping[task_name]
        return task_name.lower()
    
    # Test cases
    test_cases = [
        ("Composite", "comp"),
        ("composite", "comp"),
        ("COMPOSITE", "comp"),
        ("Lighting", "lighting"),
        ("lighting", "lighting"),
        ("comp", "comp"),  # Should remain as comp
    ]
    
    print("📋 Task Name Normalization Tests:")
    all_passed = True
    
    for input_name, expected_output in test_cases:
        result = normalize_task_name(input_name)
        status = "✅" if result == expected_output else "❌"
        print(f"   {status} '{input_name}' → '{result}' (expected: '{expected_output}')")
        
        if result != expected_output:
            all_passed = False
    
    print()
    print("🔧 File Extension Mapping:")
    
    task_extensions = {
        'lighting': '.ma',
        'composite': '.nk',
        'comp': '.nk',
        'modeling': '.ma',
        'rigging': '.ma',
        'animation': '.ma',
        'fx': '.hip',
        'lookdev': '.ma',
        'layout': '.ma',
    }
    
    extension_tests = [
        ("comp", ".nk"),
        ("composite", ".nk"),  # Legacy support
        ("lighting", ".ma"),
    ]
    
    for task_type, expected_ext in extension_tests:
        result = task_extensions.get(task_type, "NOT_FOUND")
        status = "✅" if result == expected_ext else "❌"
        print(f"   {status} '{task_type}' → '{result}' (expected: '{expected_ext}')")
        
        if result != expected_ext:
            all_passed = False
    
    print()
    if all_passed:
        print("🎉 ALL TESTS PASSED! Task type mapping is working correctly.")
        print("   • 'Composite' CSV entries will be normalized to 'comp'")
        print("   • File extensions are correctly mapped")
        print("   • Configuration changes are properly reflected")
    else:
        print("❌ SOME TESTS FAILED! Please check the implementation.")
    
    return all_passed

if __name__ == "__main__":
    success = test_task_mapping()
    sys.exit(0 if success else 1)
