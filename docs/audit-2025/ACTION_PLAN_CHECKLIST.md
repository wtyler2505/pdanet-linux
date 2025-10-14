# Action Plan Checklist - PdaNet Linux

**Quick reference for implementing audit recommendations**

---

## 🔴 PRIORITY 1: CRITICAL (This Week - 4 hours)

### Security Fixes (1 hour)

- [ ] **Upgrade pymongo** (15 min)
  ```bash
  pip install --upgrade "pymongo>=4.6.3"
  pip freeze | grep pymongo >> requirements.txt.new
  # Verify version: 4.6.3 or higher
  ```

- [ ] **Upgrade starlette** (15 min)
  ```bash
  pip install --upgrade "starlette>=0.47.2"
  pip freeze | grep starlette >> requirements.txt.new
  # Or upgrade FastAPI: pip install --upgrade "fastapi>=0.110.3"
  ```

- [ ] **Update requirements.txt** (5 min)
  ```bash
  mv requirements.txt requirements.txt.old
  pip freeze > requirements.txt
  ```

- [ ] **Test after upgrades** (25 min)
  ```bash
  pytest tests/ -v
  # Ensure all tests still pass
  ```

### Script Fixes (1 hour)

- [ ] **Fix HTTPS string matching in stealth-mode.sh** (30 min)
  ```bash
  # Edit /app/scripts/stealth-mode.sh
  # DELETE or comment out lines 46-47, 49 (HTTPS string matching)
  # Add comment: "# HTTPS encrypted, string matching ineffective"
  ```

- [ ] **Fix hardcoded paths in install.sh** (30 min)
  ```bash
  # Edit /app/install.sh
  # Replace line 16:
  # OLD: PROJECT_DIR="/home/wtyler/pdanet-linux"
  # NEW: SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
  #      PROJECT_DIR="$SCRIPT_DIR"
  
  # Replace line 112:
  # OLD: REAL_USER="wtyler"
  # NEW: echo "Error: Cannot determine user" && exit 1
  ```

### Dependency Cleanup (2 hours)

- [ ] **Identify unused dependencies** (30 min)
  ```bash
  # Check if actually used
  grep -r "import fastapi" src/ tests/
  grep -r "import pymongo" src/ tests/
  grep -r "import boto3" src/ tests/
  grep -r "import pandas" src/ tests/
  # If no results, safe to remove
  ```

- [ ] **Remove unused dependencies** (30 min)
  ```bash
  pip uninstall -y fastapi uvicorn starlette motor pymongo boto3 botocore s3transfer pandas
  ```

- [ ] **Test after removal** (30 min)
  ```bash
  pytest tests/ -v
  python src/pdanet_gui_v2.py  # Quick GUI test
  ```

- [ ] **Update requirements.txt** (30 min)
  ```bash
  pip freeze > requirements.txt
  # Commit changes
  git add requirements.txt
  git commit -m "Remove unused dependencies, fix security vulnerabilities"
  ```

**Priority 1 Complete: 4 hours ✅**

---

## 🟡 PRIORITY 2: HIGH (Week 2-3 - 88 hours)

### Phase 1: Settings Dialog (40 hours)

#### Day 1-2: Structure & General Tab (16h)

- [ ] **Create directory structure** (1h)
  ```bash
  mkdir -p src/widgets
  touch src/settings_dialog.py
  touch src/widgets/setting_widgets.py
  touch src/widgets/profile_editor.py
  touch tests/test_settings_dialog.py
  ```

- [ ] **Implement SettingsDialog class** (6h)
  - [ ] Main dialog window
  - [ ] Notebook (tabbed interface)
  - [ ] Button handlers (OK, Cancel, Apply, Reset)
  - [ ] State management (original values for cancel)

- [ ] **Build General tab** (6h)
  - [ ] Auto-start toggle
  - [ ] Start minimized toggle
  - [ ] Notifications toggle
  - [ ] Data warning toggle
  - [ ] Warning threshold spinner
  - [ ] Update interval spinner
  - [ ] Theme selector

- [ ] **Wire up save/load** (3h)
  - [ ] `_load_settings()` - Load from config
  - [ ] `_save_settings()` - Save to config
  - [ ] Apply button handler
  - [ ] Reset to defaults

#### Day 3: Network & Stealth Tabs (8h)

- [ ] **Build Network tab** (4h)
  - [ ] Proxy IP entry
  - [ ] Proxy port spinner
  - [ ] Connection timeout spinner
  - [ ] Auto-reconnect toggle
  - [ ] Reconnect attempts spinner
  - [ ] Reconnect delay spinner

- [ ] **Build Stealth tab** (4h)
  - [ ] Stealth level combo box
  - [ ] Custom TTL spinner
  - [ ] Block IPv6 toggle
  - [ ] DNS leak prevention toggle
  - [ ] Custom DNS entry
  - [ ] Traffic shaping toggle

#### Day 4: Advanced & Profiles Tabs (8h)

- [ ] **Build Advanced tab** (3h)
  - [ ] Log level combo box
  - [ ] Debug mode toggle
  - [ ] Performance monitoring toggle
  - [ ] Advanced network monitoring toggle
  - [ ] Intelligent QoS toggle

- [ ] **Build Profiles tab** (5h)
  - [ ] TreeView for profile list
  - [ ] New profile button
  - [ ] Edit profile button
  - [ ] Delete profile button
  - [ ] Import/Export buttons
  - [ ] Profile editor dialog

#### Day 5: Testing & Integration (8h)

- [ ] **Write unit tests** (4h)
  ```python
  # tests/test_settings_dialog.py
  def test_dialog_creation()
  def test_load_settings()
  def test_save_settings()
  def test_reset_to_defaults()
  def test_validation()
  def test_profile_management()
  ```

- [ ] **Integration with main GUI** (2h)
  - [ ] Add "Settings" menu item
  - [ ] Wire up settings button
  - [ ] Test settings apply immediately

- [ ] **Polish & bug fixes** (2h)
  - [ ] Fix any issues found during testing
  - [ ] Add keyboard shortcuts
  - [ ] Improve error messages

**Settings Dialog Complete: 40 hours ✅**

---

### Phase 2: First-Run Wizard (16 hours)

#### Day 6: Wizard Structure (8h)

- [ ] **Create FirstRunWizard class** (2h)
  ```bash
  touch src/first_run_wizard.py
  touch tests/test_first_run_wizard.py
  ```

- [ ] **Implement pages** (6h)
  - [ ] Welcome page
  - [ ] Requirements check page
  - [ ] Permissions page
  - [ ] Android setup page
  - [ ] Test connection page
  - [ ] Profile creation page
  - [ ] Completion page

#### Day 7: Implementation & Testing (8h)

- [ ] **Implement page logic** (4h)
  - [ ] Requirements checking
  - [ ] Permission validation
  - [ ] Connection testing
  - [ ] Profile creation

- [ ] **Wire up to main app** (2h)
  - [ ] Check if first run
  - [ ] Show wizard on first start
  - [ ] Set flag after completion

- [ ] **Test & polish** (2h)
  - [ ] Test all pages
  - [ ] Test navigation
  - [ ] Test error cases

**First-Run Wizard Complete: 16 hours ✅**

---

### Phase 3: Error Recovery UI (16 hours)

#### Day 8: Error System (8h)

- [ ] **Create error recovery module** (2h)
  ```bash
  touch src/error_recovery.py
  touch src/widgets/error_dialog.py
  touch tests/test_error_recovery.py
  ```

- [ ] **Build error database** (3h)
  - [ ] Define error types
  - [ ] Map errors to solutions
  - [ ] Create solution steps
  - [ ] Add auto-fix commands

- [ ] **Implement ErrorRecoveryDialog** (3h)
  - [ ] Show error details
  - [ ] Display solutions
  - [ ] Implement one-click fixes
  - [ ] Add copy to clipboard

#### Day 9: Integration & Testing (8h)

- [ ] **Integrate with error handling** (4h)
  - [ ] Update connection_manager errors
  - [ ] Update GUI error handlers
  - [ ] Show recovery dialog on errors

- [ ] **Test error scenarios** (4h)
  - [ ] Interface not found
  - [ ] Proxy not accessible
  - [ ] iptables failure
  - [ ] Permission denied

**Error Recovery Complete: 16 hours ✅**

---

### Phase 4: Data Usage Dashboard (16 hours)

#### Day 10: Dashboard Implementation (8h)

- [ ] **Create usage panel** (4h)
  - [ ] Circular progress meter widget
  - [ ] Session data label
  - [ ] Monthly data label
  - [ ] Threshold label
  - [ ] Reset button

- [ ] **Wire up to stats collector** (2h)
  - [ ] Real-time updates
  - [ ] Warning detection
  - [ ] Threshold checking

- [ ] **Add to main GUI** (2h)
  - [ ] Add panel to dashboard
  - [ ] Position appropriately
  - [ ] Test responsiveness

#### Day 11: Features & Testing (8h)

- [ ] **Add usage tracking** (3h)
  - [ ] Session tracking
  - [ ] Daily tracking
  - [ ] Monthly tracking
  - [ ] History storage

- [ ] **Add export functionality** (2h)
  - [ ] Export to CSV
  - [ ] Export to JSON
  - [ ] Date range selection

- [ ] **Test & polish** (3h)
  - [ ] Test accuracy
  - [ ] Test warnings
  - [ ] Test reset
  - [ ] Test export

**Data Usage Dashboard Complete: 16 hours ✅**

---

**Priority 2 Complete: 88 hours ✅**

**Score after Priority 2: 9.8/10**

---

## 🟢 PRIORITY 3: MEDIUM (Month 2 - 68 hours)

### Technical Debt Phase 1 (28 hours)

- [ ] **Split pdanet_gui_v2.py** (16h)
  - [ ] Create `src/gui/main_window.py`
  - [ ] Create panel modules
  - [ ] Create dialog modules
  - [ ] Create event handlers module
  - [ ] Update imports
  - [ ] Test everything still works

- [ ] **Create constants.py** (4h)
  - [ ] Move all magic numbers
  - [ ] Document each constant
  - [ ] Update all files to use constants
  - [ ] Test

- [ ] **Add config validation** (6h)
  - [ ] Create config schema
  - [ ] Implement validation
  - [ ] Add to config_manager
  - [ ] Test with invalid configs

- [ ] **Fix script portability** (2h)
  - [ ] Already done in Priority 1

### Test Improvements (40 hours)

- [ ] **Add P2-P4 module tests** (16h)
  - [ ] `test_performance_optimizer.py` (4h)
  - [ ] `test_reliability_manager.py` (4h)
  - [ ] `test_advanced_network_monitor.py` (4h)
  - [ ] `test_intelligent_bandwidth_manager.py` (4h)

- [ ] **Add iPhone bypass tests** (8h)
  - [ ] Test each bypass technique
  - [ ] Test effectiveness monitoring
  - [ ] Test cleanup
  - [ ] Test error handling

- [ ] **Add error recovery tests** (8h)
  - [ ] Interface loss recovery
  - [ ] Proxy crash recovery
  - [ ] Config corruption recovery
  - [ ] Network failure recovery

- [ ] **Add security tests** (8h)
  - [ ] Command injection prevention
  - [ ] Privilege escalation prevention
  - [ ] Sensitive data exposure
  - [ ] Keyring isolation

**Priority 3 Complete: 68 hours ✅**

---

## 🔵 PRIORITY 4: LOW (Month 3+ - Variable)

### Integration Tests (16 hours)

- [ ] Real network tests
- [ ] End-to-end GUI tests
- [ ] Multi-device tests

### Stress Tests (16 hours)

- [ ] 24-hour connection test
- [ ] High bandwidth test
- [ ] Rapid connect/disconnect test

### Polish (Variable)

- [ ] Documentation improvements
- [ ] Video tutorials
- [ ] Creative enhancements

---

## 📊 PROGRESS TRACKING

### Completion Status

| Phase | Hours | Status | Score Impact |
|-------|-------|--------|--------------|
| Priority 1 (Critical) | 4 | ☐ | 9.2 → 9.3 |
| Priority 2 (UX) | 88 | ☐ | 9.3 → 9.8 |
| Priority 3 (Debt) | 68 | ☐ | 9.8 → 9.8 |
| Priority 4 (Polish) | Variable | ☐ | 9.8 → 9.9 |

### Timeline

```
Week 1:  Priority 1 (4h)           ███ Complete
Week 2:  Settings Dialog (40h)     ████████████████ 
Week 3:  Wizards + Dashboards (48h)████████████████
Week 4:  Technical Debt (28h)      ███████████
Week 5:  Test Improvements (40h)   ████████████████
Week 6+: Integration/Stress Tests  ████████████████
```

---

## 🎯 SUCCESS CRITERIA

### After Priority 1
- [ ] No critical security vulnerabilities
- [ ] All tests pass
- [ ] Scripts work on any system

### After Priority 2
- [ ] Users can configure via GUI (no JSON editing)
- [ ] First-run experience guides new users
- [ ] Errors are actionable
- [ ] Data usage is visible

### After Priority 3
- [ ] Code is maintainable
- [ ] Test coverage >85%
- [ ] No critical tech debt

### After Priority 4
- [ ] Integration tests pass
- [ ] Can handle 24h+ connections
- [ ] World-class quality

---

## 📝 NOTES

### Before Starting
1. Backup your current code: `git commit -am "Pre-audit state"`
2. Create branch: `git checkout -b audit-improvements`
3. Read implementation guides in `/app/docs/audit-2025/`

### While Working
1. Commit after each checkbox
2. Run tests frequently: `pytest tests/ -v`
3. Test GUI after each change: `python src/pdanet_gui_v2.py`

### After Completing Each Priority
1. Merge to main branch
2. Tag release: `git tag v1.x.0`
3. Update documentation
4. Celebrate! 🎉

---

**Start with Priority 1 this week - just 4 hours to fix critical issues!**

