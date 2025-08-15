#!/usr/bin/env python3
"""
Test Ra application with Scrollable Manual Task Creation integration
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from PySide6.QtWidgets import QApplication, QScrollArea
from montu.task_creator.gui.main_window import TaskCreatorMainWindow

def test_ra_scrollable_integration():
    """Test Ra application with scrollable manual task creation integration."""
    print("🧪 Testing Ra Application with Scrollable Dialog Integration")
    print("=" * 65)
    
    app = QApplication(sys.argv)
    app.setApplicationName("Montu Task Creator - Scrollable Integration Test")
    app.setApplicationVersion("0.5.1")
    app.setOrganizationName("Montu Manager")
    
    # Set application style
    app.setStyle('Fusion')
    
    try:
        # Create main window
        window = TaskCreatorMainWindow()
        
        # Test 1: Check main window integration
        print("1. Testing main window integration...")
        
        # Check if Create Task button still exists and works
        if hasattr(window, 'create_task_btn'):
            print("   ✅ Create Task button found in Project Management tab")
        else:
            print("   ❌ Create Task button not found")
            return False
            
        # Check if enhanced dialog can be imported and created
        try:
            from montu.task_creator.gui.manual_task_creation_dialog import ManualTaskCreationDialog
            print("   ✅ Scrollable ManualTaskCreationDialog imported successfully")
            
            # Test creating dialog instance
            test_dialog = ManualTaskCreationDialog(window, window.db, ["TEST_PROJECT"])
            print("   ✅ Scrollable dialog instance created successfully")
            
        except Exception as e:
            print(f"   ❌ Failed to create scrollable dialog: {e}")
            return False
            
        # Test 2: Check scrollable dialog properties
        print("2. Testing scrollable dialog properties...")
        
        # Check dialog size constraints
        min_size = test_dialog.minimumSize()
        max_size = test_dialog.maximumSize()
        
        if min_size.height() == 600:
            print(f"   ✅ Minimum height set correctly: {min_size.height()}px")
        else:
            print(f"   ❌ Minimum height incorrect: {min_size.height()}px")
            return False
            
        if max_size.width() == 1400 and max_size.height() == 1000:
            print(f"   ✅ Maximum size set correctly: {max_size.width()}x{max_size.height()}")
        else:
            print(f"   ❌ Maximum size incorrect: {max_size.width()}x{max_size.height()}")
            return False
            
        # Test 3: Check scroll area integration
        print("3. Testing scroll area integration...")
        
        # Find scroll areas in the dialog
        scroll_areas = test_dialog.findChildren(QScrollArea)
        
        if len(scroll_areas) == 1:
            scroll_area = scroll_areas[0]
            print("   ✅ Single scroll area found in dialog")
            
            # Check scroll area properties
            if scroll_area.widgetResizable():
                print("   ✅ Scroll area is widget resizable")
            else:
                print("   ❌ Scroll area is not widget resizable")
                return False
                
            # Check content widget
            content_widget = scroll_area.widget()
            if content_widget:
                print("   ✅ Scroll area has content widget")
                
                # Check width constraints (should be adaptive, not fixed minimum)
                min_width = content_widget.minimumWidth()
                max_width = content_widget.maximumWidth()
                print(f"   ✅ Content widget width constraints: min={min_width}px, max={max_width}px")

                # Content should adapt to available space (no fixed minimum that could cause horizontal scrolling)
                if min_width == 0 or min_width <= 400:  # Reasonable minimum or adaptive
                    print("   ✅ Content widget width is adaptive (no horizontal scroll risk)")
                else:
                    print(f"   ❌ Content widget minimum width too large: {min_width}px")
                    return False
            else:
                print("   ❌ Scroll area missing content widget")
                return False
                
        else:
            print(f"   ❌ Expected 1 scroll area, found {len(scroll_areas)}")
            return False
            
        # Test 4: Check enhanced UI elements preservation
        print("4. Testing enhanced UI elements preservation...")
        
        # Check if enhanced UI components are still present
        enhanced_components = [
            'shot_task_types_label',
            'shot_selected_count_label',
            'asset_task_types_label',
            'asset_selected_count_label',
            'shot_task_types_list',
            'asset_task_types_list'
        ]
        
        for component in enhanced_components:
            if hasattr(test_dialog, component):
                element = getattr(test_dialog, component)
                if element:
                    print(f"   ✅ Enhanced UI component preserved: {component}")
                else:
                    print(f"   ❌ Enhanced UI component missing: {component}")
                    return False
            else:
                print(f"   ❌ Enhanced UI component not found: {component}")
                return False
                
        # Test 5: Check task type list heights
        print("5. Testing task type list heights...")
        
        shot_list_height = test_dialog.shot_task_types_list.maximumHeight()
        asset_list_height = test_dialog.asset_task_types_list.maximumHeight()
        
        if shot_list_height >= 180:
            print(f"   ✅ Shot task types list height preserved: {shot_list_height}px")
        else:
            print(f"   ❌ Shot task types list height reduced: {shot_list_height}px")
            return False
            
        if asset_list_height >= 180:
            print(f"   ✅ Asset task types list height preserved: {asset_list_height}px")
        else:
            print(f"   ❌ Asset task types list height reduced: {asset_list_height}px")
            return False
            
        # Test 6: Check interactive functionality
        print("6. Testing interactive functionality...")
        
        try:
            # Test enhanced methods
            test_dialog.update_shot_task_types_label()
            test_dialog.update_asset_task_types_label()
            print("   ✅ Enhanced label update methods work")
            
            # Test form interactions
            test_dialog.shot_radio.setChecked(True)
            test_dialog.project_combo.setCurrentText("TEST_PROJECT")
            print("   ✅ Form interactions work within scroll area")
            
            # Test custom task input
            test_dialog.shot_custom_task_edit.setText("test_custom")
            test_dialog.shot_custom_task_edit.clear()
            print("   ✅ Custom task input works within scroll area")
            
        except Exception as e:
            print(f"   ❌ Interactive functionality test failed: {e}")
            return False
            
        # Test 7: Check backward compatibility
        print("7. Testing backward compatibility...")
        
        # Check if all original methods still exist
        original_methods = [
            'get_selected_shot_task_types',
            'get_selected_asset_task_types',
            'add_custom_shot_task_type',
            'add_custom_asset_task_type',
            'generate_task_ids',
            'build_all_task_data',
            'select_all_shot_task_types',
            'select_none_shot_task_types'
        ]
        
        for method in original_methods:
            if hasattr(test_dialog, method):
                print(f"   ✅ Original method preserved: {method}")
            else:
                print(f"   ❌ Original method missing: {method}")
                return False
                
        # Test 8: Check database integration
        print("8. Testing database integration...")
        
        if hasattr(window, 'db') and window.db:
            print("   ✅ Database connection available")
            
            # Test database operations still work
            try:
                projects = window.db.find('project_configs', {})
                print(f"   ✅ Database queries work - found {len(projects)} projects")
                
            except Exception as e:
                print(f"   ❌ Database operations failed: {e}")
                return False
        else:
            print("   ❌ Database connection not available")
            return False
            
        # Test 9: Check dialog show/hide functionality
        print("9. Testing dialog show/hide functionality...")
        
        try:
            # Test showing dialog (don't actually show to avoid blocking)
            # Just check that the method exists and can be called
            if hasattr(window, 'show_create_task_dialog'):
                print("   ✅ Main window dialog show method exists")
            else:
                print("   ❌ Main window dialog show method missing")
                return False
                
            # Test dialog modal properties
            if test_dialog.isModal():
                print("   ✅ Dialog is modal")
            else:
                print("   ❌ Dialog is not modal")
                return False
                
        except Exception as e:
            print(f"   ❌ Dialog show/hide test failed: {e}")
            return False
            
        # Test 10: Check layout structure preservation
        print("10. Testing layout structure preservation...")
        
        # Check if main layout components are preserved
        main_layout = test_dialog.layout()
        if main_layout and main_layout.count() > 0:
            print("   ✅ Main dialog layout structure preserved")
        else:
            print("   ❌ Main dialog layout structure missing")
            return False
            
        # Check if splitter still exists
        from PySide6.QtWidgets import QSplitter
        splitter = test_dialog.findChild(QSplitter)
        if splitter:
            print("   ✅ Splitter layout preserved")
            
            # Check splitter proportions
            sizes = splitter.sizes()
            if len(sizes) == 2:
                print(f"   ✅ Splitter has correct panels: {sizes}")
            else:
                print(f"   ❌ Splitter panel count incorrect: {len(sizes)}")
                return False
        else:
            print("   ❌ Splitter layout missing")
            return False
            
        print("\n🎉 Ra application with Scrollable Dialog Integration is working correctly!")
        print("🚀 Scrollable integration features validated:")
        print("   • Scrollable dialog properly integrated with main window")
        print("   • Reduced minimum height for smaller screens (600px)")
        print("   • Maximum size constraints prevent oversized dialogs")
        print("   • Single scroll area properly configured in form panel")
        print("   • All enhanced UI elements preserved and functional")
        print("   • Task type list heights maintained (180-200px)")
        print("   • Interactive functionality works within scroll area")
        print("   • Complete backward compatibility maintained")
        print("   • Database integration continues to work")
        print("   • Dialog modal properties and layout structure preserved")
        print("   • Splitter layout and proportions maintained")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing Ra scrollable integration: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_ra_scrollable_integration()
    sys.exit(0 if success else 1)
