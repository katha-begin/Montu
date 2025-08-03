# Phase 1 QA Quick Checklist

**Purpose**: Rapid verification of Phase 1 completion  
**Time Required**: 15-20 minutes  
**Target**: Quality assurance engineers and project managers  

---

## 🚀 Quick Start Commands

### 1. Infrastructure Check (2 minutes)
```bash
# Start backend services
python3 scripts/docker-manager.py start

# Verify services running
python3 scripts/docker-manager.py status
```
**Expected**: MongoDB running on assigned port, health check "Healthy"

### 2. Automated Test Suite (5 minutes)
```bash
# Run comprehensive test suite
python3 scripts/test-path-generation.py
```
**Expected**: `🎯 Test Results: 5/5 tests passed` and `🎉 All tests passed!`

### 3. Target Path Validation (3 minutes)
```python
python3 -c "
from src.montu.shared.json_database import JSONDatabase
db = JSONDatabase()
pb = db.get_path_builder('SWA')

# Test render output path
task1 = {'project': 'SWA', 'episode': 'Ep00', 'sequence': 'SWA_Ep00_sq0010', 'shot': 'SWA_Ep00_SH0020', 'task': 'comp'}
render = pb.generate_render_output_path(task1, '015')
print('Render:', render)
print('Match:', render.replace(chr(92), '/') == 'W:/SWA/all/scene/Ep00/sq0010/SH0020/comp/version/v015/')

# Test working file path  
task2 = {'project': 'SWA', 'episode': 'Ep00', 'sequence': 'SWA_Ep00_sq0020', 'shot': 'SWA_Ep00_SH0090', 'task': 'lighting'}
working = pb.generate_working_file_path(task2, '003', 'maya_scene')
print('Working:', working)
print('Match:', working.replace(chr(92), '/') == 'V:/SWA/all/scene/Ep00/sq0020/SH0090/lighting/version/Ep00_sq0020_SH0090_lighting_master_v003.ma')
"
```
**Expected**: Both `Match: True`

### 4. Database Operations Check (2 minutes)
```python
python3 -c "
from src.montu.shared.json_database import JSONDatabase
db = JSONDatabase()
stats = db.get_stats()
print('Database Stats:', stats)
print('SWA Config Valid:', db.validate_project_config('SWA')['valid'])
"
```
**Expected**: 42+ tasks, 1 project_config, validation `True`

### 5. CSV Integration Verification (3 minutes)
```bash
# Test CSV conversion
python3 scripts/convert-csv-to-json.py
```
**Expected**: `✅ 42 valid tasks ready for conversion` and `🎉 Conversion completed successfully!`

---

## ✅ Pass/Fail Criteria

### ✅ PASS Requirements
- [ ] **Infrastructure**: Docker services running, MongoDB healthy
- [ ] **Automated Tests**: 5/5 test suites pass without errors
- [ ] **Target Paths**: Both render output and working file paths match exactly
- [ ] **Database**: 42+ tasks, valid SWA configuration, CRUD operations working
- [ ] **CSV Integration**: 42 tasks converted successfully with 0 validation errors

### ❌ FAIL Indicators
- Any Docker service not running or unhealthy
- Less than 5/5 automated tests passing
- Target path mismatches (Match: False)
- Database validation errors or missing data
- CSV conversion errors or validation failures

---

## 🔧 Quick Troubleshooting

### Docker Issues
```bash
# Restart services
python3 scripts/docker-manager.py stop
python3 scripts/docker-manager.py start

# Check logs
docker logs montu-mongodb
```

### Path Generation Issues
```python
# Check project configuration
python3 -c "from src.montu.shared.json_database import JSONDatabase; print(JSONDatabase().validate_project_config('SWA'))"
```

### Database Issues
```python
# Reinitialize database
python3 -c "
from src.montu.shared.json_database import JSONDatabase
db = JSONDatabase()
print('Collections:', list(db.collections.keys()))
"
```

---

## 📋 QA Sign-off

**Infrastructure**: ✅ / ❌  
**Automated Tests**: ✅ / ❌  
**Target Paths**: ✅ / ❌  
**Database Operations**: ✅ / ❌  
**CSV Integration**: ✅ / ❌  

**Overall Status**: ✅ PASS / ❌ FAIL  

**QA Engineer**: ________________  
**Date**: ________________  
**Phase 2 Approved**: ✅ / ❌  

---

## 📚 Reference Documents

- **Detailed Testing**: `Doc/Phase1_QA_Testing_Procedure.md`
- **Technical Reference**: `Doc/Phase1_Completion_Report.md`
- **Developer Guide**: `Doc/Phase2_Developer_Quick_Reference.md`
- **Executive Summary**: `Doc/Phase1_Executive_Summary.md`
