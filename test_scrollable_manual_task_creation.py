#!/usr/bin/env python3
"""
Test Scrollable Manual Task Creation Dialog functionality
Tests that the dialog works properly with scroll area on smaller screens
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from PySide6.QtWidgets import QApplication, QScrollArea
from PySide6.QtCore import QSize
from montu.task_creator.gui.main_window import TaskCreatorMainWindow
from montu.task_creator.gui.manual_task_creation_dialog import ManualTaskCreationDialog

def test_scrollable_manual_task_creation():
    """Test scrollable manual task creation dialog functionality."""
    print("🧪 Testing Scrollable Manual Task Creation Dialog")
    print("=" * 55)
    
    app = QApplication(sys.argv)
    app.setApplicationName("Montu Task Creator - Scrollable Dialog Test")
    app.setApplicationVersion("0.5.1")
    app.setOrganizationName("Montu Manager")
    
    # Set application style
    app.setStyle('Fusion')
    
    try:
        # Test 1: Check scroll area integration
        print("1. Testing scroll area integration...")
        
        # Create a test dialog instance
        dialog = ManualTaskCreationDialog(None, None, ["TEST_PROJECT"])
        
        # Check if dialog has proper size constraints
        min_size = dialog.minimumSize()
        max_size = dialog.maximumSize()
        current_size = dialog.size()
        
        print(f"   📏 Dialog size constraints:")
        print(f"      Minimum: {min_size.width()}x{min_size.height()}")
        print(f"      Maximum: {max_size.width()}x{max_size.height()}")
        print(f"      Current: {current_size.width()}x{current_size.height()}")
        
        if min_size.height() <= 600:
            print("   ✅ Minimum height reduced for smaller screens")
        else:
            print("   ❌ Minimum height not reduced")
            return False
            
        if max_size.width() > 0 and max_size.height() > 0:
            print("   ✅ Maximum size constraints set")
        else:
            print("   ❌ Maximum size constraints not set")
            return False
            
        # Test 2: Check scroll area in form panel
        print("2. Testing scroll area in form panel...")
        
        # Find the scroll area in the dialog
        scroll_areas = dialog.findChildren(QScrollArea)
        
        if len(scroll_areas) > 0:
            scroll_area = scroll_areas[0]
            print(f"   ✅ Found {len(scroll_areas)} scroll area(s)")
            
            # Check scroll area properties
            if scroll_area.widgetResizable():
                print("   ✅ Scroll area is widget resizable")
            else:
                print("   ❌ Scroll area is not widget resizable")
                return False
                
            # Check scroll bar policies
            from PySide6.QtCore import Qt
            h_policy = scroll_area.horizontalScrollBarPolicy()
            v_policy = scroll_area.verticalScrollBarPolicy()

            if h_policy == Qt.ScrollBarPolicy.ScrollBarAlwaysOff:
                print("   ✅ Horizontal scroll bar always off")
            else:
                print(f"   ❌ Horizontal scroll bar policy incorrect: {h_policy}")
                return False

            if v_policy == Qt.ScrollBarPolicy.ScrollBarAsNeeded:
                print("   ✅ Vertical scroll bar as needed")
            else:
                print(f"   ❌ Vertical scroll bar policy incorrect: {v_policy}")
                return False
                
            # Check if scroll area has content widget
            content_widget = scroll_area.widget()
            if content_widget:
                print("   ✅ Scroll area has content widget")
                
                # Check content widget minimum width
                min_width = content_widget.minimumWidth()
                if min_width >= 850:
                    print(f"   ✅ Content widget minimum width set: {min_width}px")
                else:
                    print(f"   ❌ Content widget minimum width too small: {min_width}px")
                    return False
            else:
                print("   ❌ Scroll area has no content widget")
                return False
                
        else:
            print("   ❌ No scroll area found in dialog")
            return False
            
        # Test 3: Check form components accessibility
        print("3. Testing form components accessibility...")
        
        # Check if all major form components are still accessible
        form_components = [
            'project_combo',
            'shot_radio',
            'asset_radio',
            'shot_task_types_list',
            'asset_task_types_list',
            'shot_custom_task_edit',
            'asset_custom_task_edit'
        ]
        
        for component_name in form_components:
            if hasattr(dialog, component_name):
                component = getattr(dialog, component_name)
                if component and component.isEnabled():
                    print(f"   ✅ Form component accessible: {component_name}")
                else:
                    print(f"   ⚠️ Form component disabled: {component_name}")
            else:
                print(f"   ❌ Form component not found: {component_name}")
                return False
                
        # Test 4: Check interactive elements functionality
        print("4. Testing interactive elements functionality...")
        
        try:
            # Test project combo
            dialog.project_combo.setCurrentText("TEST_PROJECT")
            print("   ✅ Project combo interaction works")
            
            # Test radio buttons
            dialog.shot_radio.setChecked(True)
            print("   ✅ Radio button interaction works")
            
            # Test task type lists
            if dialog.shot_task_types_list.count() > 0:
                first_item = dialog.shot_task_types_list.item(0)
                if first_item:
                    first_item.setSelected(True)
                    print("   ✅ Task type list interaction works")
            
            # Test custom task input
            dialog.shot_custom_task_edit.setText("test_task")
            dialog.shot_custom_task_edit.clear()
            print("   ✅ Custom task input interaction works")
            
        except Exception as e:
            print(f"   ❌ Interactive elements test failed: {e}")
            return False
            
        # Test 5: Check layout preservation
        print("5. Testing layout preservation...")
        
        # Check if main layout structure is preserved
        main_layout = dialog.layout()
        if main_layout and main_layout.count() > 0:
            print("   ✅ Main dialog layout preserved")
        else:
            print("   ❌ Main dialog layout missing")
            return False
            
        # Check if splitter still exists
        splitters = dialog.findChildren(dialog.findChild(type(dialog.findChild(QScrollArea).__class__.__bases__[0])).__class__)
        # Simplified check - look for the splitter widget
        if hasattr(dialog, 'findChild'):
            from PySide6.QtWidgets import QSplitter
            splitter = dialog.findChild(QSplitter)
            if splitter:
                print("   ✅ Splitter layout preserved")
            else:
                print("   ❌ Splitter layout missing")
                return False
        else:
            print("   ✅ Layout structure appears preserved")
            
        # Test 6: Check scroll functionality simulation
        print("6. Testing scroll functionality simulation...")
        
        try:
            # Get the scroll area and content widget
            scroll_area = scroll_areas[0]
            content_widget = scroll_area.widget()
            
            # Check if content is larger than viewport
            content_height = content_widget.sizeHint().height()
            viewport_height = scroll_area.viewport().height()
            
            print(f"   📏 Content height: {content_height}px")
            print(f"   📏 Viewport height: {viewport_height}px")
            
            if content_height > viewport_height:
                print("   ✅ Content is scrollable (content > viewport)")
            else:
                print("   ℹ️ Content fits in viewport (no scrolling needed)")
                
            # Test scroll bar visibility
            v_scrollbar = scroll_area.verticalScrollBar()
            if v_scrollbar:
                if v_scrollbar.isVisible():
                    print("   ✅ Vertical scroll bar is visible when needed")
                else:
                    print("   ℹ️ Vertical scroll bar hidden (content fits)")
            else:
                print("   ❌ Vertical scroll bar not found")
                return False
                
        except Exception as e:
            print(f"   ❌ Scroll functionality test failed: {e}")
            return False
            
        # Test 7: Check dialog resizing behavior
        print("7. Testing dialog resizing behavior...")
        
        try:
            # Test resizing to smaller size
            original_size = dialog.size()
            dialog.resize(900, 500)  # Resize to smaller height
            new_size = dialog.size()
            
            print(f"   📏 Resized from {original_size.width()}x{original_size.height()} to {new_size.width()}x{new_size.height()}")
            
            # Check if minimum size is respected
            if new_size.height() >= dialog.minimumSize().height():
                print("   ✅ Minimum size constraints respected")
            else:
                print("   ❌ Minimum size constraints violated")
                return False
                
            # Restore original size
            dialog.resize(original_size)
            print("   ✅ Dialog resizing behavior works correctly")
            
        except Exception as e:
            print(f"   ❌ Dialog resizing test failed: {e}")
            return False
            
        # Test 8: Check enhanced UI elements still work
        print("8. Testing enhanced UI elements compatibility...")
        
        # Check if enhanced UI elements are still present
        enhanced_elements = [
            'shot_task_types_label',
            'shot_selected_count_label',
            'asset_task_types_label',
            'asset_selected_count_label'
        ]
        
        for element_name in enhanced_elements:
            if hasattr(dialog, element_name):
                element = getattr(dialog, element_name)
                if element:
                    print(f"   ✅ Enhanced UI element preserved: {element_name}")
                else:
                    print(f"   ❌ Enhanced UI element missing: {element_name}")
                    return False
            else:
                print(f"   ❌ Enhanced UI element not found: {element_name}")
                return False
                
        # Test enhanced methods
        enhanced_methods = [
            'update_shot_task_types_label',
            'update_asset_task_types_label'
        ]
        
        for method_name in enhanced_methods:
            if hasattr(dialog, method_name):
                try:
                    method = getattr(dialog, method_name)
                    method()  # Call the method to test it works
                    print(f"   ✅ Enhanced method works: {method_name}")
                except Exception as e:
                    print(f"   ❌ Enhanced method failed: {method_name} - {e}")
                    return False
            else:
                print(f"   ❌ Enhanced method not found: {method_name}")
                return False
                
        print("\n🎉 Scrollable Manual Task Creation Dialog is working correctly!")
        print("🚀 Scrollable dialog features validated:")
        print("   • Scroll area properly integrated into form panel")
        print("   • Reduced minimum height for smaller screens (600px)")
        print("   • Maximum size constraints prevent oversized dialogs")
        print("   • Horizontal scrolling disabled, vertical scrolling as needed")
        print("   • All form components remain accessible and functional")
        print("   • Interactive elements work correctly within scroll area")
        print("   • Layout structure and splitter preserved")
        print("   • Enhanced UI elements compatibility maintained")
        print("   • Dialog resizing behavior works correctly")
        print("   • Content widget minimum width ensures proper layout")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing scrollable manual task creation: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_scrollable_manual_task_creation()
    sys.exit(0 if success else 1)
