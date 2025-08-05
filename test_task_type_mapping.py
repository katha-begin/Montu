#!/usr/bin/env python3
"""
Test script to verify task type mapping from "Composite" to "comp"
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '.'))

from src.montu.task_creator.csv_parser import CSVParser

def test_task_type_mapping():
    """Test that CSV parser correctly maps task types."""
    parser = CSVParser()
    
    print("🧪 Testing Task Type Mapping")
    print("=" * 50)
    
    # Test various task name inputs
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
        result = parser.normalize_task_name(input_name)
        status = "✅" if result == expected_output else "❌"
        print(f"   {status} '{input_name}' → '{result}' (expected: '{expected_output}')")
        
        if result != expected_output:
            all_passed = False
    
    print()
    print("🔧 Task Extension Mapping:")
    
    # Test file extension mapping
    extension_tests = [
        ("comp", ".nk"),
        ("composite", ".nk"),  # Legacy support
        ("lighting", ".ma"),
    ]
    
    for task_type, expected_ext in extension_tests:
        result = parser.task_extensions.get(task_type, "NOT_FOUND")
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
    success = test_task_type_mapping()
    sys.exit(0 if success else 1)
