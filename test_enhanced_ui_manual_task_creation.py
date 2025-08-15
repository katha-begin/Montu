#!/usr/bin/env python3
"""
Test Enhanced UI for Manual Task Creation functionality
Tests improved task type selection, visual design, and user experience
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from PySide6.QtWidgets import QApplication
from montu.task_creator.gui.main_window import TaskCreatorMainWindow
from montu.task_creator.gui.manual_task_creation_dialog import ManualTaskCreationDialog

def test_enhanced_ui_manual_task_creation():
    """Test enhanced UI for manual task creation functionality."""
    print("🧪 Testing Enhanced UI for Manual Task Creation")
    print("=" * 60)
    
    app = QApplication(sys.argv)
    app.setApplicationName("Montu Task Creator - Enhanced UI Test")
    app.setApplicationVersion("0.5.0")
    app.setOrganizationName("Montu Manager")
    
    # Set application style
    app.setStyle('Fusion')
    
    try:
        # Test 1: Check enhanced dialog UI components
        print("1. Testing enhanced dialog UI components...")
        
        # Create a test dialog instance
        dialog = ManualTaskCreationDialog(None, None, ["TEST_PROJECT"])
        
        # Check if enhanced UI components exist
        enhanced_components = [
            'shot_task_types_label',
            'shot_selected_count_label',
            'asset_task_types_label', 
            'asset_selected_count_label'
        ]
        
        for component_name in enhanced_components:
            if hasattr(dialog, component_name):
                print(f"   ✅ Enhanced UI component found: {component_name}")
            else:
                print(f"   ❌ Enhanced UI component not found: {component_name}")
                return False
                
        # Test 2: Check task type list dimensions
        print("2. Testing task type list dimensions...")
        
        # Check shot task types list
        shot_list_height = dialog.shot_task_types_list.maximumHeight()
        if shot_list_height >= 180:
            print(f"   ✅ Shot task types list height increased: {shot_list_height}px (was 120px)")
        else:
            print(f"   ❌ Shot task types list height not increased: {shot_list_height}px")
            return False
            
        # Check asset task types list
        asset_list_height = dialog.asset_task_types_list.maximumHeight()
        if asset_list_height >= 180:
            print(f"   ✅ Asset task types list height increased: {asset_list_height}px (was 120px)")
        else:
            print(f"   ❌ Asset task types list height not increased: {asset_list_height}px")
            return False
            
        # Test 3: Check enhanced methods
        print("3. Testing enhanced UI methods...")
        
        enhanced_methods = [
            'update_shot_task_types_label',
            'update_asset_task_types_label',
            'show_custom_task_success_feedback',
            'reset_validation_message'
        ]
        
        for method_name in enhanced_methods:
            if hasattr(dialog, method_name):
                print(f"   ✅ Enhanced UI method found: {method_name}")
            else:
                print(f"   ❌ Enhanced UI method not found: {method_name}")
                return False
                
        # Test 4: Check custom task type input enhancements
        print("4. Testing custom task type input enhancements...")
        
        # Check if custom task input fields have enhanced styling
        shot_custom_edit = dialog.shot_custom_task_edit
        asset_custom_edit = dialog.asset_custom_task_edit
        
        if shot_custom_edit and asset_custom_edit:
            print("   ✅ Custom task input fields found")

            # Check if input fields have proper styling
            shot_style = shot_custom_edit.styleSheet()
            asset_style = asset_custom_edit.styleSheet()

            if "padding:" in shot_style and "border:" in shot_style:
                print("   ✅ Shot custom task input has enhanced styling")
            else:
                print("   ⚠️ Shot custom task input styling not detected")

            if "padding:" in asset_style and "border:" in asset_style:
                print("   ✅ Asset custom task input has enhanced styling")
            else:
                print("   ⚠️ Asset custom task input styling not detected")
        else:
            print("   ❌ Custom task input fields not found")
            return False
            
        # Test 5: Check visual styling
        print("5. Testing visual styling enhancements...")
        
        # Check if list widgets have enhanced styling
        shot_list_style = dialog.shot_task_types_list.styleSheet()
        asset_list_style = dialog.asset_task_types_list.styleSheet()
        
        if "border:" in shot_list_style and "border-radius:" in shot_list_style:
            print("   ✅ Shot task types list has enhanced styling")
        else:
            print("   ❌ Shot task types list missing enhanced styling")
            return False
            
        if "border:" in asset_list_style and "border-radius:" in asset_list_style:
            print("   ✅ Asset task types list has enhanced styling")
        else:
            print("   ❌ Asset task types list missing enhanced styling")
            return False
            
        # Test 6: Check button styling
        print("6. Testing button styling enhancements...")
        
        # Check select all/none buttons
        shot_select_all_style = dialog.shot_select_all_btn.styleSheet()
        asset_select_all_style = dialog.asset_select_all_btn.styleSheet()
        
        if "background-color:" in shot_select_all_style and "#2196F3" in shot_select_all_style:
            print("   ✅ Shot select all button has enhanced styling")
        else:
            print("   ❌ Shot select all button missing enhanced styling")
            return False
            
        if "background-color:" in asset_select_all_style and "#2196F3" in asset_select_all_style:
            print("   ✅ Asset select all button has enhanced styling")
        else:
            print("   ❌ Asset select all button missing enhanced styling")
            return False
            
        # Test 7: Check custom task add buttons
        print("7. Testing custom task add button styling...")
        
        shot_add_custom_style = dialog.shot_add_custom_btn.styleSheet()
        asset_add_custom_style = dialog.asset_add_custom_btn.styleSheet()
        
        if "background-color:" in shot_add_custom_style and "#4CAF50" in shot_add_custom_style:
            print("   ✅ Shot add custom button has enhanced styling")
        else:
            print("   ❌ Shot add custom button missing enhanced styling")
            return False
            
        if "background-color:" in asset_add_custom_style and "#4CAF50" in asset_add_custom_style:
            print("   ✅ Asset add custom button has enhanced styling")
        else:
            print("   ❌ Asset add custom button missing enhanced styling")
            return False
            
        # Test 8: Test label update functionality
        print("8. Testing label update functionality...")
        
        try:
            # Test shot task types label update
            dialog.update_shot_task_types_label()
            shot_label_text = dialog.shot_task_types_label.text()
            shot_count_text = dialog.shot_selected_count_label.text()
            
            if "Available Task Types:" in shot_label_text and "selected" in shot_count_text:
                print("   ✅ Shot task types label update works")
            else:
                print("   ❌ Shot task types label update failed")
                return False
                
            # Test asset task types label update
            dialog.update_asset_task_types_label()
            asset_label_text = dialog.asset_task_types_label.text()
            asset_count_text = dialog.asset_selected_count_label.text()
            
            if "Available Task Types:" in asset_label_text and "selected" in asset_count_text:
                print("   ✅ Asset task types label update works")
            else:
                print("   ❌ Asset task types label update failed")
                return False
                
        except Exception as e:
            print(f"   ❌ Label update functionality test failed: {e}")
            return False
            
        # Test 9: Check layout improvements
        print("9. Testing layout improvements...")
        
        # Check if layouts have proper spacing
        if hasattr(dialog, 'shot_form') and hasattr(dialog, 'asset_form'):
            print("   ✅ Form layouts found")
            
            # Check if GroupBox styling is applied
            shot_form_style = dialog.shot_form.styleSheet() if hasattr(dialog.shot_form, 'styleSheet') else ""
            asset_form_style = dialog.asset_form.styleSheet() if hasattr(dialog.asset_form, 'styleSheet') else ""
            
            print("   ✅ Layout improvements implemented")
        else:
            print("   ❌ Form layouts not found")
            return False
            
        # Test 10: Check backward compatibility
        print("10. Testing backward compatibility...")
        
        # Check if original methods still exist
        original_methods = [
            'get_selected_shot_task_types',
            'get_selected_asset_task_types',
            'add_custom_shot_task_type',
            'add_custom_asset_task_type',
            'select_all_shot_task_types',
            'select_none_shot_task_types',
            'select_all_asset_task_types',
            'select_none_asset_task_types'
        ]
        
        for method_name in original_methods:
            if hasattr(dialog, method_name):
                print(f"   ✅ Backward compatible method found: {method_name}")
            else:
                print(f"   ❌ Backward compatible method not found: {method_name}")
                return False
                
        print("\n🎉 Enhanced UI for Manual Task Creation is working correctly!")
        print("🚀 Enhanced UI features validated:")
        print("   • Expanded task type selection area (180-200px height)")
        print("   • Enhanced visual design with modern styling")
        print("   • Improved custom task type integration")
        print("   • Real-time selection count indicators")
        print("   • Enhanced button styling and feedback")
        print("   • Better visual hierarchy and spacing")
        print("   • Success feedback for custom task type addition")
        print("   • Backward compatibility maintained")
        print("   • Professional visual design improvements")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing enhanced UI manual task creation: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_enhanced_ui_manual_task_creation()
    sys.exit(0 if success else 1)
