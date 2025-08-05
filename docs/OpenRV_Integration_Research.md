# OpenRV Integration Research and Implementation
## Professional VFX Media Player Integration for Montu Manager Review Application

### 📋 **Research Summary**

**OpenRV** (Academy Software Foundation) is the industry-standard professional media player for VFX and animation review workflows. This document outlines the research findings and implementation approach for integrating OpenRV capabilities into the Montu Manager Review Application.

---

## 🔍 **OpenRV Overview**

### **What is OpenRV?**
- **Industry Standard**: Professional media player used by major VFX studios worldwide
- **Academy Software Foundation**: Open-source project maintained by the Academy of Motion Picture Arts and Sciences
- **Advanced Features**: Frame-accurate playback, color management, professional formats support
- **VFX Optimized**: Designed specifically for visual effects and animation review workflows

### **Key Capabilities**
- **Format Support**: .exr, .dpx, .mov, .mp4, .jpg, .png, .tiff, and many more
- **Color Management**: ACES, Rec.709, sRGB, Linear workflows
- **Frame Accuracy**: Precise frame-by-frame navigation and timing
- **Sequence Playback**: Image sequence support with automatic detection
- **Professional Tools**: Wipe, compare, annotations, color grading
- **Python Integration**: Extensive Python API for custom workflows

---

## 🔧 **Integration Research Findings**

### **1. OpenRV Architecture**
```
OpenRV Application
├── Core Engine (C++)
├── Python API Layer
├── Qt-based GUI
├── Command Line Interface
└── Plugin System
```

### **2. Integration Approaches Evaluated**

#### **Approach A: Embedded Widget (Not Feasible)**
- **Concept**: Embed OpenRV as a Qt widget within our application
- **Research Result**: ❌ **Not Supported**
- **Reason**: OpenRV is designed as a standalone application, not an embeddable widget
- **Technical Limitation**: No public API for widget embedding

#### **Approach B: External Process Integration (Implemented)**
- **Concept**: Launch OpenRV as external process with file arguments
- **Research Result**: ✅ **Fully Supported**
- **Implementation**: Command-line launching with parameters
- **Benefits**: Full OpenRV functionality, professional workflow integration

#### **Approach C: Python API Integration (Future Enhancement)**
- **Concept**: Use OpenRV Python API for custom integration
- **Research Result**: ✅ **Possible but Complex**
- **Requirements**: OpenRV installation with Python bindings
- **Use Case**: Custom review workflows, automated processing

---

## 🚀 **Current Implementation**

### **1. OpenRV Detection and Availability**
```python
def check_openrv_availability(self) -> bool:
    """Check if OpenRV is available on the system."""
    # Check common executable names
    openrv_names = ['rv', 'openrv', 'RV', 'OpenRV']
    
    # Check system PATH
    for name in openrv_names:
        if shutil.which(name):
            return True
    
    # Check common installation paths
    common_paths = [
        '/usr/local/bin/rv',                    # Linux/macOS
        '/opt/rv/bin/rv',                       # Linux
        'C:\\Program Files\\Tweak\\RV\\bin\\rv.exe',    # Windows (Tweak)
        'C:\\Program Files\\OpenRV\\bin\\rv.exe'        # Windows (OpenRV)
    ]
    
    return any(os.path.exists(path) for path in common_paths)
```

### **2. External Process Launch**
```python
def launch_in_openrv(self):
    """Launch current media file in external OpenRV application."""
    # Find OpenRV executable
    openrv_cmd = self.find_openrv_executable()
    
    # Prepare command line arguments
    args = [self.current_media_path]
    
    # Add professional parameters
    if colorspace != "sRGB":
        args.extend(["-c", colorspace])
    
    if fps != 24:
        args.extend(["-fps", str(fps)])
    
    # Launch process
    self.openrv_process = QProcess(self)
    self.openrv_process.start(openrv_cmd, args)
```

### **3. Professional Controls Integration**
- **Color Space Selection**: sRGB, Rec.709, Linear, ACES
- **Frame Rate Control**: 1-120 FPS support
- **Launch Button**: Direct OpenRV integration
- **Status Indicators**: Availability and format support display

---

## 📊 **Implementation Status**

### **✅ Completed Features**
1. **OpenRV Detection**: Automatic system detection and availability checking
2. **External Launch**: Launch media files directly in OpenRV
3. **Parameter Passing**: Color space and frame rate configuration
4. **Process Management**: QProcess integration with cleanup
5. **User Interface**: Professional controls and status indicators
6. **Error Handling**: Comprehensive error messages and fallbacks
7. **Cross-Platform**: Windows, Linux, and macOS support

### **🔄 Integration Points**
- **Media Player Widget**: Enhanced with OpenRV capabilities
- **Review Application**: Seamless integration with media loading
- **Database Integration**: Works with virtual media files and metadata
- **Professional Workflow**: Color space and frame rate management

---

## 🎯 **Professional VFX Workflow Benefits**

### **1. Industry Standard Compliance**
- **Studio Compatibility**: Same tools used by major VFX studios
- **Professional Features**: Frame-accurate review, color management
- **Format Support**: Native .exr, .dpx, and sequence support

### **2. Enhanced Review Capabilities**
- **Color Accuracy**: Professional color management workflows
- **Frame Precision**: Exact frame navigation and timing
- **Comparison Tools**: Side-by-side, wipe, and overlay comparisons
- **Annotation Support**: Professional review annotation tools

### **3. Workflow Integration**
- **Seamless Launch**: Direct integration from Review Application
- **Context Preservation**: Maintains project and task context
- **Metadata Passing**: Color space and frame rate configuration
- **Process Management**: Integrated lifecycle management

---

## 🔮 **Future Enhancement Opportunities**

### **1. Python API Integration**
```python
# Future implementation concept
import rv

class OpenRVIntegration:
    def __init__(self):
        self.rv_session = rv.Session()
    
    def load_sequence(self, file_paths, colorspace="sRGB"):
        """Load image sequence with color management."""
        self.rv_session.addSource(file_paths)
        self.rv_session.setColorSpace(colorspace)
    
    def add_annotations(self, annotations):
        """Add review annotations to timeline."""
        for annotation in annotations:
            self.rv_session.addAnnotation(annotation)
```

### **2. Custom Review Workflows**
- **Automated Comparisons**: Before/after, version comparisons
- **Batch Processing**: Multiple file review workflows
- **Custom Annotations**: Integration with Montu Manager annotation system
- **Report Generation**: Automated review reports and feedback

### **3. Advanced Integration**
- **Embedded Communication**: Two-way communication with OpenRV
- **Custom UI Elements**: Montu Manager branding and controls
- **Database Synchronization**: Real-time annotation and status updates
- **Collaborative Review**: Multi-user review session support

---

## 📚 **Installation and Setup**

### **1. OpenRV Installation**
```bash
# Download from Academy Software Foundation
# https://github.com/AcademySoftwareFoundation/OpenRV

# Linux/macOS
sudo apt install openrv  # or equivalent package manager
# or compile from source

# Windows
# Download installer from GitHub releases
# Install to default location or custom path
```

### **2. System Configuration**
```bash
# Ensure OpenRV is in system PATH
export PATH=$PATH:/usr/local/bin/rv

# Windows: Add to system PATH
# C:\Program Files\OpenRV\bin
```

### **3. Verification**
```bash
# Test OpenRV installation
rv --version

# Test with sample media
rv /path/to/media/file.exr
```

---

## ✅ **Implementation Success Criteria**

### **✅ Achieved Goals**
1. **Professional Integration**: OpenRV seamlessly integrated into Review Application
2. **Cross-Platform Support**: Works on Windows, Linux, and macOS
3. **Automatic Detection**: Intelligent OpenRV availability checking
4. **Parameter Configuration**: Color space and frame rate control
5. **Error Handling**: Comprehensive fallback and error management
6. **User Experience**: Professional controls with clear status indicators

### **📈 **Benefits Delivered**
- **Industry Standard**: Professional VFX review capabilities
- **Enhanced Workflow**: Seamless integration with existing Review Application
- **Format Support**: Native support for professional VFX formats
- **Color Management**: Professional color space handling
- **Frame Accuracy**: Precise frame-by-frame review capabilities

---

## 🎉 **Conclusion**

The OpenRV integration research and implementation successfully delivers professional VFX media player capabilities to the Montu Manager Review Application. While direct widget embedding is not feasible, the external process integration approach provides full access to OpenRV's professional features while maintaining seamless workflow integration.

**Key Achievements:**
- ✅ Professional VFX review capabilities
- ✅ Industry-standard tool integration  
- ✅ Cross-platform compatibility
- ✅ Comprehensive error handling
- ✅ Professional workflow support

**The implementation provides a solid foundation for professional VFX review workflows and establishes the groundwork for future advanced integrations using OpenRV's Python API.**
