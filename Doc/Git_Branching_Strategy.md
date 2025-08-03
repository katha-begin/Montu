# Montu Manager Ecosystem - Git Branching Strategy

## 🌳 Overview

This document defines the comprehensive Git branching strategy for the Montu Manager ecosystem, which consists of four integrated applications: Project Launcher, Task Creator, DCC Integration Suite, and Review Application.

## 🏗️ Core Branch Structure

### Main Branches
```
main                    # Production-ready code, stable releases
develop                 # Integration branch for all development
release/v1.0.0         # Release preparation branches
hotfix/critical-fix    # Emergency fixes for production
```

### Application-Specific Development Branches
```
feature/project-launcher/*     # Project Launcher features (pl/)
feature/task-creator/*         # Task Creator features (tc/)
feature/dcc-integration/*      # DCC Integration Suite features (dcc/)
feature/review-app/*           # Review Application features (ra/)
feature/shared/*               # Shared components (database, utils)
feature/infra/*                # Infrastructure/DevOps
```

### Phase-Based Integration Branches
```
integration/phase-1           # Foundation & Backend Setup
integration/phase-2           # Core Application Development
integration/phase-3           # DCC Integration Suite
integration/phase-4           # Advanced Features & Polish
```

## 📋 Branch Naming Conventions

### Feature Branches
```
feature/{app-prefix}/{task-description}

Examples:
feature/pl/project-selection-dropdown
feature/tc/csv-data-validation
feature/dcc/maya-shelf-integration
feature/ra/annotation-system
feature/shared/path-builder-engine
feature/infra/docker-compose-setup
```

### Application Prefixes
- `pl/` - Project Launcher
- `tc/` - Task Creator
- `dcc/` - DCC Integration Suite
- `ra/` - Review Application
- `shared/` - Shared components (database, utils, common libraries)
- `infra/` - Infrastructure/DevOps (Docker, CI/CD, deployment)

### Integration Branches
```
integration/phase-{number}
integration/phase-2-core-apps

app/{application-name}
app/project-launcher
app/task-creator
```

### Release Branches
```
release/v{major}.{minor}.{patch}
release/v1.0.0-project-launcher
release/v1.1.0-ecosystem
```

### Hotfix Branches
```
hotfix/{severity}-{description}
hotfix/critical-database-connection
hotfix/urgent-maya-plugin-crash
```

## 🔄 Development Workflow

### Phase-Based Development Process

1. **Phase Start**: Create `integration/phase-X` from `develop`
2. **Feature Development**: Create feature branches from phase integration branch
3. **Application Integration**: Merge features to application-level integration
4. **Phase Integration**: Test cross-application compatibility
5. **Phase Complete**: Merge phase integration to `develop`
6. **Release**: Create release branch when phase is stable

### Multi-Application Integration Hierarchy
```
develop                           # Final integration
├── integration/phase-2          # Current phase integration
│   ├── app/project-launcher     # Application-level integration
│   │   ├── feature/pl/gui-mockup
│   │   └── feature/pl/database-connection
│   ├── app/task-creator         # Application-level integration
│   │   ├── feature/tc/csv-import
│   │   └── feature/tc/validation
│   └── shared/database          # Shared component integration
│       ├── feature/shared/mongodb-schema
│       └── feature/shared/json-mock-db
```

## 👥 Team Collaboration Guidelines

### Branch Protection Rules

**main branch:**
- Require PR reviews: 3
- Require status checks: All CI/CD
- Restrict pushes: Team leads only
- Require up-to-date branches: true

**develop branch:**
- Require PR reviews: 2
- Require status checks: Integration tests
- Allow team leads direct push: false

**integration/* branches:**
- Require PR reviews: 1
- Require status checks: Application tests
- Allow app team leads: true

**feature/* branches:**
- No restrictions (developer freedom)
- Require CI checks: Basic tests

### Pull Request Strategy

**PR Requirements by Branch Type:**
- **Feature → App Integration**: 1 reviewer (app team lead)
- **App → Phase Integration**: 2 reviewers (cross-app validation)
- **Phase → Develop**: 3 reviewers (full team validation)
- **Release → Main**: All team leads approval

**Merge Strategy:**
- **Feature branches**: Squash and merge (clean history)
- **Integration branches**: Merge commit (preserve integration points)
- **Release branches**: Merge commit (preserve release history)
- **Hotfix branches**: Fast-forward merge (immediate deployment)

### Team-Based Workflow

**Role-Based Branch Access:**
- **Pipeline TDs**: Focus on `shared/`, `infra/`, and integration branches
- **Application Developers**: Work on specific `feature/{app}/` branches
- **Artists/Testers**: Create branches for testing and feedback
- **DevOps**: Manage `infra/`, release, and deployment branches

## 🚀 Environment Management

### Environment Branch Mapping
```
main branch          → production environment
release/* branches   → staging environment
develop branch       → development environment
integration/* branches → feature testing environments
```

### Docker Environment Configuration
- **Development**: Port 27017 (develop branch)
- **Staging**: Port 27018 (release branches)
- **Production**: Port 27019 (main branch)

## 🚨 Hotfix Procedures

### Critical Issues (Production Down)
1. Create `hotfix/critical-{description}` from `main`
2. Implement fix with minimal changes
3. Test in isolated environment
4. Direct merge to `main` with all-hands approval
5. Immediate deployment
6. Back-merge to `develop` and all active branches

### Urgent Issues (Functionality Broken)
1. Create `hotfix/urgent-{description}` from `main`
2. Implement fix and comprehensive testing
3. Create PR with expedited review process
4. Merge to `main` and deploy to staging first
5. Production deployment after staging validation

## 📊 Release Management

### Staggered Release Strategy
```
Phase 1: Foundation Release
├── Infrastructure components
├── Database schema
└── Basic project structure

Phase 2: Core Applications Release
├── Project Launcher v1.0
├── Task Creator v1.0
└── JSON Mock Database

Phase 3: DCC Integration Release
├── Maya Plugin v1.0
├── Nuke Plugin v1.0
└── DCC Integration Suite v1.0

Phase 4: Complete Ecosystem Release
├── Review Application v1.0
├── All applications integrated
└── Production deployment ready
```

### Release Process
1. Create `release/v1.0.0` from `develop`
2. Final testing and bug fixes on release branch
3. Tag release: `git tag -a v1.0.0 -m "Project Launcher v1.0.0"`
4. Merge to `main` and back-merge to `develop`
5. Deploy to production environment

## 🛠️ Recommended Tools

### Conventional Commits
```
feat(pl): add project selection dropdown
fix(tc): resolve CSV parsing error
docs(shared): update database schema documentation
test(ra): add media playback integration tests
ci(infra): update Docker configuration for staging
```

### Branch Management Scripts
Use provided scripts in `/scripts` directory for:
- Creating feature branches with proper naming
- Checking integration status
- Managing phase transitions
- Automated testing workflows

## 📈 Success Metrics

**Branch Health Metrics:**
- Feature branch lifetime (target: < 5 days)
- Integration branch stability (target: > 95% green builds)
- Cross-application compatibility score
- Release deployment success rate

**Team Collaboration Metrics:**
- PR review time (target: < 24 hours)
- Merge conflict frequency (target: < 5% of merges)
- Cross-team collaboration (PRs between app teams)
- Documentation coverage per application
