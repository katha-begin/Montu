#!/usr/bin/env python3
"""
Run all test files and report results
"""

import os
import subprocess
import sys

def run_all_tests():
    """Run all test files and report results."""
    print("🧪 Running All Test Files")
    print("=" * 50)
    
    # Get all test files
    test_files = [f for f in os.listdir('.') if f.startswith('test_') and f.endswith('.py')]
    test_files.sort()
    
    results = []
    
    for test_file in test_files:
        print(f"\n🔍 Running {test_file}...")
        try:
            result = subprocess.run(['python', test_file], 
                                  capture_output=True, 
                                  text=True, 
                                  timeout=60)
            
            if result.returncode == 0:
                print(f"   ✅ PASSED")
                results.append((test_file, True, ""))
            else:
                print(f"   ❌ FAILED (Exit code: {result.returncode})")
                if result.stderr:
                    print(f"   Error: {result.stderr[:200]}...")
                results.append((test_file, False, result.stderr))
                
        except subprocess.TimeoutExpired:
            print(f"   ⏰ TIMEOUT")
            results.append((test_file, False, "Timeout"))
        except Exception as e:
            print(f"   💥 ERROR: {e}")
            results.append((test_file, False, str(e)))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    passed = sum(1 for _, success, _ in results if success)
    total = len(results)
    
    for test_file, success, error in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status:8} {test_file}")
        if not success and error:
            print(f"         Error: {error[:100]}...")
    
    print(f"\nResult: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    return passed == total

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
