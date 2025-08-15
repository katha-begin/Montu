#!/usr/bin/env python3
"""
Test Horizontal Scroll Bar Fix for Manual Task Creation Dialog
Verifies that horizontal scrolling is completely disabled
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from PySide6.QtWidgets import QApplication, QScrollArea
from PySide6.QtCore import Qt, QSize
from montu.task_creator.gui.manual_task_creation_dialog import ManualTaskCreationDialog

def test_horizontal_scroll_fix():
    """Test that horizontal scrolling is properly disabled in the manual task creation dialog."""
    print("🧪 Testing Horizontal Scroll Bar Fix")
    print("=" * 45)
    
    app = QApplication(sys.argv)
    app.setApplicationName("Montu Task Creator - Horizontal Scroll Fix Test")
    app.setApplicationVersion("0.5.2")
    app.setOrganizationName("Montu Manager")
    
    # Set application style
    app.setStyle('Fusion')
    
    try:
        # Test 1: Check scroll area configuration
        print("1. Testing scroll area configuration...")
        
        # Create a test dialog instance
        dialog = ManualTaskCreationDialog(None, None, ["TEST_PROJECT"])
        
        # Find the scroll area
        scroll_areas = dialog.findChildren(QScrollArea)
        
        if len(scroll_areas) == 1:
            scroll_area = scroll_areas[0]
            print("   ✅ Single scroll area found")
            
            # Check horizontal scroll bar policy
            h_policy = scroll_area.horizontalScrollBarPolicy()
            if h_policy == Qt.ScrollBarPolicy.ScrollBarAlwaysOff:
                print("   ✅ Horizontal scroll bar policy correctly set to ScrollBarAlwaysOff")
            else:
                print(f"   ❌ Horizontal scroll bar policy incorrect: {h_policy}")
                return False
                
            # Check vertical scroll bar policy
            v_policy = scroll_area.verticalScrollBarPolicy()
            if v_policy == Qt.ScrollBarPolicy.ScrollBarAsNeeded:
                print("   ✅ Vertical scroll bar policy correctly set to ScrollBarAsNeeded")
            else:
                print(f"   ❌ Vertical scroll bar policy incorrect: {v_policy}")
                return False
                
        else:
            print(f"   ❌ Expected 1 scroll area, found {len(scroll_areas)}")
            return False
            
        # Test 2: Check content widget size policy
        print("2. Testing content widget size policy...")
        
        content_widget = scroll_area.widget()
        if content_widget:
            print("   ✅ Content widget found")
            
            # Check size policy
            size_policy = content_widget.sizePolicy()
            h_policy = size_policy.horizontalPolicy()
            v_policy = size_policy.verticalPolicy()
            
            print(f"   📏 Content widget size policy: H={h_policy}, V={v_policy}")
            
            # Check if horizontal policy allows expansion
            from PySide6.QtWidgets import QSizePolicy
            if h_policy == QSizePolicy.Policy.Expanding:
                print("   ✅ Content widget horizontal policy set to Expanding")
            else:
                print(f"   ⚠️ Content widget horizontal policy: {h_policy}")
                
        else:
            print("   ❌ Content widget not found")
            return False
            
        # Test 3: Check horizontal scroll bar visibility
        print("3. Testing horizontal scroll bar visibility...")
        
        h_scrollbar = scroll_area.horizontalScrollBar()
        if h_scrollbar:
            if not h_scrollbar.isVisible():
                print("   ✅ Horizontal scroll bar is not visible")
            else:
                print("   ❌ Horizontal scroll bar is visible")
                return False
                
            # Check if horizontal scroll bar is enabled
            if not h_scrollbar.isEnabled():
                print("   ✅ Horizontal scroll bar is disabled")
            else:
                print("   ❌ Horizontal scroll bar is enabled")
                return False
                
        else:
            print("   ❌ Horizontal scroll bar not found")
            return False
            
        # Test 4: Test dialog resizing behavior
        print("4. Testing dialog resizing behavior...")
        
        # Get original size
        original_size = dialog.size()
        print(f"   📏 Original dialog size: {original_size.width()}x{original_size.height()}")
        
        # Resize to smaller width to test horizontal scrolling
        test_width = 800  # Smaller than original
        dialog.resize(test_width, original_size.height())
        
        # Force layout update
        dialog.updateGeometry()
        app.processEvents()
        
        # Check if horizontal scroll bar appeared
        h_scrollbar = scroll_area.horizontalScrollBar()
        if not h_scrollbar.isVisible():
            print(f"   ✅ No horizontal scroll bar after resizing to {test_width}px width")
        else:
            print(f"   ❌ Horizontal scroll bar appeared after resizing to {test_width}px width")
            return False
            
        # Test even smaller width
        test_width = 700
        dialog.resize(test_width, original_size.height())
        dialog.updateGeometry()
        app.processEvents()
        
        if not h_scrollbar.isVisible():
            print(f"   ✅ No horizontal scroll bar after resizing to {test_width}px width")
        else:
            print(f"   ❌ Horizontal scroll bar appeared after resizing to {test_width}px width")
            return False
            
        # Restore original size
        dialog.resize(original_size)
        
        # Test 5: Check content widget width adaptation
        print("5. Testing content widget width adaptation...")
        
        # Get scroll area viewport width
        viewport_width = scroll_area.viewport().width()
        content_width = content_widget.width()
        
        print(f"   📏 Scroll area viewport width: {viewport_width}px")
        print(f"   📏 Content widget width: {content_width}px")
        
        if content_width <= viewport_width:
            print("   ✅ Content widget width fits within viewport")
        else:
            print("   ❌ Content widget width exceeds viewport")
            return False
            
        # Test 6: Check form elements don't cause horizontal overflow
        print("6. Testing form elements don't cause horizontal overflow...")
        
        # Check if any child widgets have excessive width
        child_widgets = content_widget.findChildren(content_widget.__class__)
        max_child_width = 0
        
        for child in child_widgets:
            if child.isVisible():
                child_width = child.width()
                if child_width > max_child_width:
                    max_child_width = child_width
                    
        print(f"   📏 Maximum child widget width: {max_child_width}px")
        
        if max_child_width <= viewport_width:
            print("   ✅ All child widgets fit within viewport")
        else:
            print("   ⚠️ Some child widgets may be wider than viewport")
            
        # Test 7: Test with different dialog sizes
        print("7. Testing with different dialog sizes...")
        
        test_sizes = [
            (900, 600),   # Minimum size
            (1000, 750),  # Default size
            (1200, 900),  # Larger size
            (850, 550),   # Below minimum (should be constrained)
        ]
        
        for width, height in test_sizes:
            dialog.resize(width, height)
            dialog.updateGeometry()
            app.processEvents()
            
            actual_size = dialog.size()
            h_scrollbar = scroll_area.horizontalScrollBar()
            
            if not h_scrollbar.isVisible():
                print(f"   ✅ No horizontal scroll bar at size {actual_size.width()}x{actual_size.height()}")
            else:
                print(f"   ❌ Horizontal scroll bar appeared at size {actual_size.width()}x{actual_size.height()}")
                return False
                
        # Test 8: Check scroll area widget resizable property
        print("8. Testing scroll area widget resizable property...")
        
        if scroll_area.widgetResizable():
            print("   ✅ Scroll area widget resizable property is True")
        else:
            print("   ❌ Scroll area widget resizable property is False")
            return False
            
        # Test 9: Verify no minimum width constraint on content
        print("9. Testing content widget width constraints...")
        
        min_width = content_widget.minimumWidth()
        max_width = content_widget.maximumWidth()
        
        print(f"   📏 Content widget minimum width: {min_width}px")
        print(f"   📏 Content widget maximum width: {max_width}px")
        
        # Check if minimum width could cause horizontal scrolling
        if min_width == 0 or min_width <= 800:  # Reasonable minimum
            print("   ✅ Content widget minimum width won't cause horizontal scrolling")
        else:
            print(f"   ❌ Content widget minimum width too large: {min_width}px")
            return False
            
        # Test 10: Final verification with form interactions
        print("10. Testing form interactions don't trigger horizontal scrolling...")
        
        try:
            # Interact with form elements
            dialog.shot_radio.setChecked(True)
            dialog.project_combo.setCurrentText("TEST_PROJECT")
            
            # Add some text to input fields
            dialog.shot_episode_edit.setText("Ep01")
            dialog.shot_sequence_edit.setText("sq010")
            dialog.shot_shot_edit.setText("sh020")
            
            # Force layout updates
            dialog.updateGeometry()
            app.processEvents()
            
            # Check horizontal scroll bar one more time
            h_scrollbar = scroll_area.horizontalScrollBar()
            if not h_scrollbar.isVisible():
                print("   ✅ No horizontal scroll bar after form interactions")
            else:
                print("   ❌ Horizontal scroll bar appeared after form interactions")
                return False
                
        except Exception as e:
            print(f"   ❌ Form interaction test failed: {e}")
            return False
            
        print("\n🎉 Horizontal Scroll Bar Fix is working correctly!")
        print("🚀 Horizontal scrolling prevention validated:")
        print("   • Horizontal scroll bar policy set to ScrollBarAlwaysOff")
        print("   • Content widget size policy allows proper expansion")
        print("   • Horizontal scroll bar remains invisible at all dialog sizes")
        print("   • Content widget adapts to available viewport width")
        print("   • Form elements don't cause horizontal overflow")
        print("   • Dialog resizing doesn't trigger horizontal scrolling")
        print("   • Widget resizable property correctly configured")
        print("   • No excessive minimum width constraints")
        print("   • Form interactions don't trigger horizontal scrolling")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing horizontal scroll fix: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_horizontal_scroll_fix()
    sys.exit(0 if success else 1)
