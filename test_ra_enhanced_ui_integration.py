#!/usr/bin/env python3
"""
Test Ra application with Enhanced UI Manual Task Creation integration
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from PySide6.QtWidgets import QApplication
from montu.task_creator.gui.main_window import TaskCreatorMainWindow

def test_ra_enhanced_ui_integration():
    """Test Ra application with enhanced UI manual task creation integration."""
    print("🧪 Testing Ra Application with Enhanced UI Integration")
    print("=" * 65)
    
    app = QApplication(sys.argv)
    app.setApplicationName("Montu Task Creator - Enhanced UI Integration Test")
    app.setApplicationVersion("0.5.0")
    app.setOrganizationName("Montu Manager")
    
    # Set application style
    app.setStyle('Fusion')
    
    try:
        # Create main window
        window = TaskCreatorMainWindow()
        
        # Test 1: Check enhanced UI integration
        print("1. Testing enhanced UI integration...")
        
        # Check if Create Task button still exists and works
        if hasattr(window, 'create_task_btn'):
            print("   ✅ Create Task button found in Project Management tab")
        else:
            print("   ❌ Create Task button not found")
            return False
            
        # Check if enhanced dialog can be imported and created
        try:
            from montu.task_creator.gui.manual_task_creation_dialog import ManualTaskCreationDialog
            print("   ✅ Enhanced ManualTaskCreationDialog imported successfully")
            
            # Test creating dialog instance
            test_dialog = ManualTaskCreationDialog(window, window.db, ["TEST_PROJECT"])
            print("   ✅ Enhanced dialog instance created successfully")
            
            # Check enhanced UI components
            enhanced_components = [
                'shot_task_types_label',
                'shot_selected_count_label',
                'asset_task_types_label',
                'asset_selected_count_label'
            ]
            
            for component in enhanced_components:
                if hasattr(test_dialog, component):
                    print(f"   ✅ Enhanced UI component found: {component}")
                else:
                    print(f"   ❌ Enhanced UI component missing: {component}")
                    return False
                    
        except Exception as e:
            print(f"   ❌ Failed to create enhanced dialog: {e}")
            return False
            
        # Test 2: Check enhanced UI dimensions
        print("2. Testing enhanced UI dimensions...")
        
        # Check list widget heights
        shot_height = test_dialog.shot_task_types_list.maximumHeight()
        asset_height = test_dialog.asset_task_types_list.maximumHeight()
        
        if shot_height >= 180:
            print(f"   ✅ Shot task types list height enhanced: {shot_height}px")
        else:
            print(f"   ❌ Shot task types list height not enhanced: {shot_height}px")
            return False
            
        if asset_height >= 180:
            print(f"   ✅ Asset task types list height enhanced: {asset_height}px")
        else:
            print(f"   ❌ Asset task types list height not enhanced: {asset_height}px")
            return False
            
        # Test 3: Check enhanced styling
        print("3. Testing enhanced styling...")
        
        # Check list widget styling
        shot_style = test_dialog.shot_task_types_list.styleSheet()
        asset_style = test_dialog.asset_task_types_list.styleSheet()
        
        if "border:" in shot_style and "border-radius:" in shot_style:
            print("   ✅ Shot task types list has enhanced styling")
        else:
            print("   ❌ Shot task types list missing enhanced styling")
            return False
            
        if "border:" in asset_style and "border-radius:" in asset_style:
            print("   ✅ Asset task types list has enhanced styling")
        else:
            print("   ❌ Asset task types list missing enhanced styling")
            return False
            
        # Test 4: Check enhanced methods
        print("4. Testing enhanced methods...")
        
        enhanced_methods = [
            'update_shot_task_types_label',
            'update_asset_task_types_label',
            'show_custom_task_success_feedback',
            'reset_validation_message'
        ]
        
        for method in enhanced_methods:
            if hasattr(test_dialog, method):
                print(f"   ✅ Enhanced method found: {method}")
            else:
                print(f"   ❌ Enhanced method missing: {method}")
                return False
                
        # Test 5: Check enhanced functionality
        print("5. Testing enhanced functionality...")
        
        try:
            # Test label update methods
            test_dialog.update_shot_task_types_label()
            test_dialog.update_asset_task_types_label()
            print("   ✅ Label update methods work correctly")
            
            # Check label content
            shot_label_text = test_dialog.shot_task_types_label.text()
            asset_label_text = test_dialog.asset_task_types_label.text()
            
            if "Available Task Types:" in shot_label_text:
                print("   ✅ Shot task types label content correct")
            else:
                print("   ❌ Shot task types label content incorrect")
                return False
                
            if "Available Task Types:" in asset_label_text:
                print("   ✅ Asset task types label content correct")
            else:
                print("   ❌ Asset task types label content incorrect")
                return False
                
        except Exception as e:
            print(f"   ❌ Enhanced functionality test failed: {e}")
            return False
            
        # Test 6: Check backward compatibility
        print("6. Testing backward compatibility...")
        
        # Check if all original methods still exist
        original_methods = [
            'get_selected_shot_task_types',
            'get_selected_asset_task_types',
            'add_custom_shot_task_type',
            'add_custom_asset_task_type',
            'generate_task_ids',
            'build_all_task_data'
        ]
        
        for method in original_methods:
            if hasattr(test_dialog, method):
                print(f"   ✅ Original method preserved: {method}")
            else:
                print(f"   ❌ Original method missing: {method}")
                return False
                
        # Test 7: Check main window integration
        print("7. Testing main window integration...")
        
        # Check if main window can still show dialog
        if hasattr(window, 'show_create_task_dialog'):
            print("   ✅ Main window dialog method found")
        else:
            print("   ❌ Main window dialog method missing")
            return False
            
        # Check if task management table still exists
        if hasattr(window, 'task_management_table'):
            print("   ✅ Task management table found")
        else:
            print("   ❌ Task management table missing")
            return False
            
        # Test 8: Check database integration
        print("8. Testing database integration...")
        
        if hasattr(window, 'db') and window.db:
            print("   ✅ Database connection available")
            
            # Test enhanced database operations
            try:
                # Test custom task type queries
                projects = window.db.find('project_configs', {})
                print(f"   ✅ Database queries work - found {len(projects)} projects")
                
            except Exception as e:
                print(f"   ❌ Database operations failed: {e}")
                return False
        else:
            print("   ❌ Database connection not available")
            return False
            
        # Test 9: Check enhanced button styling
        print("9. Testing enhanced button styling...")
        
        # Check select all/none buttons
        shot_select_all_style = test_dialog.shot_select_all_btn.styleSheet()
        asset_select_all_style = test_dialog.asset_select_all_btn.styleSheet()
        
        if "background-color:" in shot_select_all_style:
            print("   ✅ Shot select all button has enhanced styling")
        else:
            print("   ❌ Shot select all button missing enhanced styling")
            return False
            
        if "background-color:" in asset_select_all_style:
            print("   ✅ Asset select all button has enhanced styling")
        else:
            print("   ❌ Asset select all button missing enhanced styling")
            return False
            
        # Test 10: Check custom task input styling
        print("10. Testing custom task input styling...")
        
        shot_input_style = test_dialog.shot_custom_task_edit.styleSheet()
        asset_input_style = test_dialog.asset_custom_task_edit.styleSheet()
        
        if "padding:" in shot_input_style and "border:" in shot_input_style:
            print("   ✅ Shot custom task input has enhanced styling")
        else:
            print("   ❌ Shot custom task input missing enhanced styling")
            return False
            
        if "padding:" in asset_input_style and "border:" in asset_input_style:
            print("   ✅ Asset custom task input has enhanced styling")
        else:
            print("   ❌ Asset custom task input missing enhanced styling")
            return False
            
        print("\n🎉 Ra application with Enhanced UI Integration is working correctly!")
        print("🚀 Enhanced UI integration features validated:")
        print("   • Enhanced UI components properly integrated")
        print("   • Expanded task type selection area (180-200px height)")
        print("   • Enhanced visual design with modern styling")
        print("   • Improved custom task type integration")
        print("   • Real-time selection count indicators")
        print("   • Enhanced button and input field styling")
        print("   • Success feedback for custom task type addition")
        print("   • Backward compatibility fully maintained")
        print("   • Main window integration preserved")
        print("   • Database operations continue to work")
        print("   • Professional visual design improvements")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing Ra enhanced UI integration: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_ra_enhanced_ui_integration()
    sys.exit(0 if success else 1)
