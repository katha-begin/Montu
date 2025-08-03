# Montu Manager Ecosystem

A comprehensive DCC-agnostic file, task, and media management system for VFX/animation studios, consisting of four integrated applications that share a common MongoDB backend.

## 🏗️ Application Architecture

### 1. **Project Launcher** (Standalone Desktop Application)
- **Primary Role**: Central project management and file operations
- **Target Users**: All personas (Artists, Pipeline TDs, Supervisors)
- **Key Features**: Project navigation, task assignment, version control, file operations

### 2. **Task Creator** (CSV Import Tool)
- **Primary Role**: Bulk task creation and project setup
- **Target Users**: Pipeline TDs and supervisors
- **Key Features**: CSV parsing, data validation, batch task creation, error handling

### 3. **DCC Integration Suite** (Plugin System)
- **Primary Role**: In-application workflows for artists
- **Target Users**: Artists working within DCCs (Maya, Nuke, etc.)
- **Key Features**: Save/load/publish workflows, version management, artist utilities

### 4. **Review Application** (Media Browser)
- **Primary Role**: Media review and approval workflows
- **Target Users**: Supervisors and clients
- **Key Features**: Media playback, version comparison, annotation tools, approval tracking

## 🚀 Development Status

**Current Phase**: Phase 1 - Project Foundation & Backend Setup

### Development Phases
- **Phase 1**: Foundation & Backend Setup ⏳
- **Phase 2**: Core Application Development 📋
- **Phase 3**: DCC Integration Suite Development 🔧
- **Phase 4**: Advanced Features & Polish ✨

## 🛠️ Technology Stack

- **GUI Framework**: PySide6 (Qt for Python)
- **Database**: MongoDB with PyMongo
- **Data Processing**: Pandas (CSV handling)
- **Media Processing**: OpenCV, Pillow
- **Build System**: PyInstaller
- **Testing**: Pytest with Qt support
- **Documentation**: Sphinx

## 📋 Project Structure

```
montu/
├── src/montu/                    # Main package
│   ├── project_launcher/         # Project Launcher application
│   ├── task_creator/            # Task Creator application
│   ├── dcc_integration/         # DCC Integration Suite
│   ├── review_app/              # Review Application
│   ├── shared/                  # Shared components
│   └── cli/                     # Command-line interface
├── tests/                       # Test suites
├── docs/                        # Documentation
├── config/                      # Configuration files
├── data/                        # Sample data and schemas
├── scripts/                     # Development scripts
└── Doc/                         # Project documentation
```

## 🌳 Git Branching Strategy

This project follows a multi-application branching strategy with phase-based development:

### Branch Structure
- **Main Branches**: `main`, `develop`
- **Phase Integration**: `integration/phase-1`, `integration/phase-2`, etc.
- **Feature Branches**: `feature/{app-prefix}/{feature-name}`

### Application Prefixes
- `pl/` - Project Launcher
- `tc/` - Task Creator
- `dcc/` - DCC Integration Suite
- `ra/` - Review Application
- `shared/` - Shared components
- `infra/` - Infrastructure/DevOps

See [Git Branching Strategy](Doc/Git_Branching_Strategy.md) for complete details.

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- MongoDB (local or cloud)
- Git

### Installation
```bash
# Clone the repository
git clone https://github.com/katha-begin/Montu.git
cd Montu

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .
```

### Development Setup
```bash
# Create a feature branch (using our branch management script)
./scripts/branch-management.sh create-feature project-launcher gui-mockup 2

# Run tests
pytest

# Format code
black src/

# Type checking
mypy src/
```

## 📚 Documentation

- [Product Requirements Document](Doc/PRD_draft.md)
- [Git Branching Strategy](Doc/Git_Branching_Strategy.md)
- [API Documentation](docs/) (Coming soon)
- [User Guides](docs/) (Coming soon)

## 🤝 Contributing

1. Follow the Git branching strategy outlined in the documentation
2. Create feature branches using the provided naming conventions
3. Ensure all tests pass before submitting PRs
4. Follow the code style guidelines (Black formatting)
5. Update documentation as needed

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🔗 Links

- **Repository**: https://github.com/katha-begin/Montu
- **Issues**: https://github.com/katha-begin/Montu/issues
- **Documentation**: https://montu-manager.readthedocs.io/ (Coming soon)

---

**Montu Manager Ecosystem** - Streamlining VFX/Animation Production Workflows
