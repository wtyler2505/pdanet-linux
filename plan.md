# PdaNet Linux – Professional-Grade Roadmap

Last updated: 2025-10-13 (22:40 UTC)
Reference: COMPREHENSIVE_QUALITY_AUDIT_REPORT.md (330+ issues)
Priority Order: P0 Security → P1 Critical Functionality → P2 UX → P3 Code Quality → P4 Testing → P5 Documentation → P6 Features → P7 Polish

**Current Phase:** P1 - Critical Functionality (P0 COMPLETED ✅)

---

## 1) Executive Summary

Mission: Elevate PdaNet Linux from "works-for-basic-use" to a secure, robust, and professionally engineered desktop application. We will resolve all P0/P1 issues first, then harden UX, code quality, tests, and documentation, followed by advanced features and polish.

Approach: Execute in phases tightly aligned to the audit priority. Each phase has concrete deliverables, acceptance criteria, and test coverage additions. Security changes include immediate elimination of plaintext secrets and shell-injection risks. Engineering changes emphasize thread safety, error recovery, and modularization. UX changes focus on real metrics, reduced modal friction, and accessible defaults.

Outcomes: Zero P0 vulnerabilities, zero P1 broken features, deterministic behavior across reconnects, strong test coverage with automated checks (linting, security, and regression), and clear, user-friendly documentation.

**Progress Update:**
- ✅ Phase P0 (Security) - COMPLETED
- 🔄 Phase P1 (Critical Functionality) - IN PROGRESS
- ⏳ Phase P2 (UX) - PENDING
- ⏳ Phase P3 (Code Quality) - PENDING
- ⏳ Phase P4 (Testing) - PENDING
- ⏳ Phase P5 (Documentation) - PENDING
- ⏳ Phase P6 (Features) - PENDING
- ⏳ Phase P7 (Polish) - PENDING

---

## 2) Objectives

### ✅ Security Hardening (P0) - COMPLETED

**Completed Deliverables:**
- ✅ Password migration tool (`src/migrate_passwords.py`) with keyring support (#291, #117)
  - Automatic detection and migration of plaintext passwords
  - Backup creation before migration
  - Dry-run mode for safe testing
  - Comprehensive error handling and reporting
  
- ✅ Comprehensive input validation module (`src/input_validators.py`) (#292, #58-59)
  - SSID validation (length, character whitelist, shell-safe)
  - Password validation (length limits, unsafe character blocking)
  - IP address validation (format, type, private/loopback checks)
  - Port validation (range checking)
  - Hostname validation (RFC 1123 compliance)
  - Interface name validation (Linux naming rules)
  - Path validation (traversal prevention, null byte blocking)
  - Subprocess argument validation
  - 33 comprehensive security tests (all passing)
  
- ✅ Secure lockfile implementation (#1, #295)
  - XDG-compliant location (XDG_RUNTIME_DIR or ~/.cache)
  - Atomic creation with O_EXCL flag
  - Restrictive permissions (0600)
  - Stale lock detection and cleanup
  - PID-based validation
  
- ✅ Unified privilege model (#55, #293)
  - pkexec-only elevation (no silent sudo fallback)
  - Explicit error messages if pkexec unavailable
  - Input validation before privilege escalation
  - Clear user guidance on missing dependencies
  
- ✅ Security documentation and audit logging (#300-303)
  - Comprehensive SECURITY.md with threat model
  - Responsible disclosure policy
  - Security best practices for users
  - Audit logging for all privileged operations
  - Known limitations documented
  
- ✅ Security scanning (#P0-SEC-7)
  - Bandit scan: 0 HIGH severity issues
  - All subprocess calls validated
  - No shell=True usage
  - Input sanitization in place

**Acceptance Criteria Met:**
- ✅ No secrets in config.json (keyring preferred, secure fallback)
- ✅ Bandit clean (0 High severity)
- ✅ Ruff clean (0 errors in modified files)
- ✅ All subprocess calls use list-args (no shell=True)
- ✅ Input validation prevents injection attacks (33 tests passing)
- ✅ SECURITY.md complete with threat model and disclosure policy

### 🔄 Critical Reliability (P1) - IN PROGRESS

**Remaining Work:**
- ⏳ Fix configuration-driven log level application (#131)
  - Ensure logger respects config.log_level setting
  - Apply level changes without restart
  
- ⏳ Implement state transition validation (#56)
  - Define valid state machine transitions
  - Prevent illegal state changes (e.g., DISCONNECTED→CONNECTED without CONNECTING)
  - Add transition guards and logging
  
- ⏳ Fix thread leaks in monitoring (#96-102)
  - Proper thread join on shutdown
  - Cleanup monitoring threads on disconnect
  - Ensure no orphaned daemon threads
  
- ⏳ Replace fragile nmcli parsing (#73-75)
  - Use `nmcli -t -f FIELD1,FIELD2` for structured output
  - Add retry logic with exponential backoff
  - Handle edge cases (empty output, malformed data)
  
- ⏳ Consolidate connect/disconnect threading (#86-87, #94)
  - Merge duplicate logic in _connect_thread and _disconnect_thread
  - Extract common patterns into helper methods
  - Reduce code duplication by ~60%
  
- ⏳ Implement error recovery and cleanup (#1619, #289)
  - Cleanup iptables rules on connection failure
  - Stop redsocks on error
  - Clear stale current_mode and monitoring flags
  - Ensure clean state after errors
  
- ⏳ Add bounded ThreadPoolExecutor (#266)
  - Replace unlimited thread spawning with ThreadPoolExecutor
  - Set max_workers based on connection modes (e.g., 2-3)
  - Add proper shutdown handling
  
- ⏳ Fix stealth status display (#522)
  - Update stealth mode status dynamically
  - Remove "[AUTO]" placeholder
  - Show real-time iptables rule status

**Acceptance Criteria:**
- Connect/disconnect stable under 100 rapid toggles
- No orphaned threads after shutdown
- Consistent states after failures
- Logs reflect configured level
- nmcli parsing robust against edge cases
- Error paths leave system in clean state

### ⏳ UX & Accessibility (P2) - PENDING

- Replace fake quality bar with real metrics (latency, packet loss, throughput trend) (#12, #257)
- Persist window geometry and key view preferences; reduce modal dialogs; actionable errors (#245-250)
- Keyboard navigation/focus indicators; configurable font size; high-DPI support (#242-244, #201-204)

### ⏳ Code Quality & Architecture (P3) - PENDING

- Extract speedtest and network scanning to dedicated modules; remove duplication (#36, #39-43, #1000-1063)
- Introduce constants/enums; remove magic numbers; implement event bus/signals; reduce tight coupling (#12, #24-27, #320-330, #324)

### ⏳ Testing (P4) - PENDING

- Add unit, integration, performance, and visual tests for identified gaps (#187-218, #206-210, #201-205)
- Security and edge-case tests (special chars in SSID/password, flapping, suspend) (#211-218)

### ⏳ Documentation (P5) - PENDING

- Add CONTRIBUTING.md, CODE_OF_CONDUCT.md, API docs, troubleshooting/FAQ, disaster recovery, legal guidance notes (#156-181)
- Update README with accurate claims, coverage metrics, screenshots, and versioned CHANGELOG

### ⏳ Advanced Features (P6) & Polish (P7) - PENDING

- Bandwidth graphs and historical persistence (#315), first-run wizard, VPN handoff, profile enhancements, dark mode toggle, visual refinements

---

## 3) UI/UX Design Guidelines (GTK)

- Visual Identity & Theme
  - Default: Dark theme with neutral background (#0b0f14) and subtle surfaces (#10151b). Light theme parity provided.
  - Accent: Cyan/teal for primary actions (#14b8a6), Amber for warnings (#f59e0b), Rose for errors (#f43f5e), Emerald for success (#10b981). Ensure contrast ≥ WCAG AA.
  - Avoid pure black; prefer very-dark neutrals for comfort (#241).

- Typography
  - UI: Figtree (or system Sans fallback) for readability; Mono: Roboto Mono for logs/advanced text.
  - Establish a clear scale (11/13/15/20/24 px) and use semantic roles (Title/Header/Body/Caption).
  - User-configurable font size (+/-) for accessibility (#242).

- Layout & Navigation
  - Single primary window with HeaderBar + sidebar-style Preferences window (non-modal). Reduce modal chaining (#246).
  - Save and restore window size/position (#245). Provide keyboard shortcuts for common actions.

- Components & Patterns
  - Status: Real-time quality indicator using latency/packet loss colors; bandwidth graph via GtkDrawingArea + Cairo.
  - Logs: Efficient incremental append and filter; export actions. Clear error cards with guidance and retry.
  - Notifications: Libnotify with capped frequency and actionable text.

- States (Loading/Empty/Error)
  - Skeleton placeholders for stats; explicit "No data yet" empty states; descriptive error banners with next steps.

- Accessibility & Internationalization
  - Focus rings, consistent keyboard traversal, minimum touch targets ≈ 44 px.
  - Prepare strings for i18n; avoid hardcoded text scattered in code (#1026-1032).

- Motion & Performance
  - Subtle transitions only; animate transform/opacity if any; keep CPU overhead low.

---

## 4) Implementation Steps (Phased)

### ✅ Phase P0 – Security (COMPLETED)

**Completed Work:**

1. **Credentials & Migration**
   - ✅ Created `src/migrate_passwords.py` with full migration tool
   - ✅ Keyring backend integration (Secret Service/libsecret)
   - ✅ Automatic migration on startup (detect plaintext → keyring → backup)
   - ✅ Dry-run mode for safe testing
   - ✅ Comprehensive error handling and user feedback

2. **Input Validation**
   - ✅ Created `src/input_validators.py` with comprehensive validators
   - ✅ SSID validation (length, shell-safe characters)
   - ✅ Password validation (WPA2 limits, unsafe character blocking)
   - ✅ IP/port/hostname/interface validation
   - ✅ Subprocess argument validation
   - ✅ Created `tests/test_input_validators.py` with 33 security tests (all passing)
   - ✅ Integrated validators into `connection_manager.py`

3. **Privilege Model**
   - ✅ Updated `connection_manager._run_privileged()` to use pkexec only
   - ✅ Removed silent sudo fallback
   - ✅ Added explicit error messages for missing pkexec
   - ✅ Added input validation before privilege escalation
   - ✅ Added audit logging for all privileged operations

4. **Secure Lockfile**
   - ✅ Updated `pdanet_gui_v2.py` SingleInstance class
   - ✅ XDG-compliant location (XDG_RUNTIME_DIR or ~/.cache)
   - ✅ Atomic creation with O_EXCL flag
   - ✅ Restrictive permissions (0600)
   - ✅ Stale lock detection with PID validation
   - ✅ Proper cleanup on release

5. **Security Documentation**
   - ✅ Created comprehensive `SECURITY.md`
   - ✅ Threat model and attack surface analysis
   - ✅ Responsible disclosure policy
   - ✅ Security best practices for users
   - ✅ Known limitations documented
   - ✅ Audit and compliance sections

6. **Security Verification**
   - ✅ Bandit scan: 0 HIGH severity issues
   - ✅ Ruff linting: Clean (0 errors in modified files)
   - ✅ All subprocess calls audited (no shell=True)
   - ✅ Input validation tests: 33/33 passing

**Acceptance Criteria: ALL MET ✅**

### 🔄 Phase P1 – Critical Functionality (IN PROGRESS)

**Current Focus:**

1. **Config & Logging** (Next)
   - Apply config-specified log level (#131)
   - Implement rotating log file
   - Optional journal integration (#122-123)
   - Ensure logger respects runtime config changes

2. **State Machine Validation**
   - Define valid state transitions (#56)
   - Add transition guards in `connection_manager.py`
   - Prevent illegal state changes
   - Add comprehensive state transition logging

3. **Thread Management**
   - Fix monitoring thread leaks (#96-102)
   - Proper join/cleanup on disconnect
   - Add bounded ThreadPoolExecutor (#266)
   - Replace unlimited thread spawning

4. **nmcli Robustness**
   - Use `nmcli -t -f` for structured output (#73-75)
   - Add retry logic with exponential backoff
   - Handle edge cases (empty output, malformed data)
   - Improve error messages

5. **Code Consolidation**
   - Merge _connect_thread and _disconnect_thread logic (#86-87, #94)
   - Extract common patterns
   - Reduce duplication by ~60%

6. **Error Recovery**
   - Cleanup iptables/redsocks on failure (#1619, #289)
   - Clear stale state flags
   - Ensure clean system state after errors
   - Add recovery procedures

7. **Stealth Status**
   - Update stealth mode display dynamically (#522)
   - Query iptables rules in real-time
   - Remove "[AUTO]" placeholder
   - Show active/inactive status accurately

**Acceptance Criteria:**
- Connect/disconnect stable under 100 rapid toggles
- No orphaned threads after shutdown
- Consistent states after failures
- Logs reflect configured level
- nmcli parsing handles all edge cases
- Error paths leave system clean

### ⏳ Phase P2 – User Experience (PENDING)

- Real Quality Metrics
  - Replace placeholder progress with real latency/loss + throughput trend (#12, #257)
- Windows & Dialogs
  - Persist window geometry; convert stacked modals to Preferences window flows (#245-246)
- Messaging & Help
  - Actionable error dialogs, tooltips, inline help; keyboard shortcuts and focus indicators (#247-249, #243)
- Acceptance: Clear metrics visible; reduced modal friction; persisted UI prefs; accessibility checks pass

### ⏳ Phase P3 – Code Quality & Architecture (PENDING)

- Modularization
  - Extract speedtest and network scanning from GUI; add abstraction for subprocess/network ops (#36, #39-43, #1000-1063, #330)
- Constants & Config
  - Centralize strings/enums; remove magic numbers (timeouts, TTL) with config and sane defaults (#324)
- Eventing & DI
  - Simple event bus or GObject signals; limit globals/singletons; thread-safe singletons (#106-107, #325-329)
- Acceptance: Reduced duplication, isolated business logic, improved testability; static analysis cleaner

### ⏳ Phase P4 – Testing (PENDING)

- Unit
  - Add tests for threading/race, config corruption, monotonic time for stats, input validation (#187-190, #111-112, #211-218)
- Integration
  - Simulated connection flows with nmcli/iptables mocks; failover/network flapping; suspend/resume
- Visual/Performance
  - Visual snapshots across DPI/scales; CPU/memory/startup benchmarks (#201-210)
- Security Tests
  - Injection attempts; missing polkit; keyring unavailable fallback paths
- Acceptance: Coverage ≥ 80%; performance budgets met; visual tests stable

### ⏳ Phase P5 – Documentation (PENDING)

- Author CONTRIBUTING.md, CODE_OF_CONDUCT.md, API docs for modules, troubleshooting flowchart, FAQ, disaster recovery, legal guidance overview (#156-181)
- Update README with accurate claims, coverage metrics, screenshots, and versioned CHANGELOG
- Acceptance: Docs complete and accurate; links validated

### ⏳ Phase P6 – Advanced Features (PENDING)

- Bandwidth Graph & History
  - Time-series bandwidth graph with ring buffer; persist historical usage (#315, #112, #114)
- First-Run Setup Wizard
  - Guided onboarding for profiles, permissions, and defaults
- VPN Handoff & Profiles
  - Optional auto-VPN post-connect; improved profile quick-switch
- Acceptance: Features stable, documented, and tested

### ⏳ Phase P7 – Polish (PENDING)

- Theming & Icons
  - Dark/light toggle; symbolic icon set; fine spacing/contrast
- Accessibility
  - Larger touch targets; keyboard help overlay; i18n hooks
- Packaging
  - Deb/RPM/AppImage (time permitting) and install/uninstall safety improvements (#231-235, #219-230)
- Acceptance: Professional finish; installer/uninstaller safe; consistent cross-desktop behavior

---

## 5) Technical Details (Key Decisions)

### ✅ Implemented (P0)

- **Secure Secrets**
  - ✅ Using python-keyring with Secret Service backend on Linux
  - ✅ Store per-SSID credentials as service="pdanet-linux-wifi", username=ssid
  - ✅ Migration tool with backup, dry-run, and rollback capability
  - ✅ Secure fallback with 0600 permissions if keyring unavailable

- **Safe Subprocess**
  - ✅ Input validation module (`input_validators.py`) with comprehensive validators
  - ✅ All subprocess calls use list-args (no shell=True)
  - ✅ Validation before execution (SSID, password, IP/host)
  - ✅ Structured error handling and logging

- **Privilege Model**
  - ✅ pkexec-based elevation with clear user messaging
  - ✅ Explicit error if pkexec unavailable (no silent sudo fallback)
  - ✅ Input validation before privilege escalation
  - ✅ Audit logging for all privileged operations

- **Locking**
  - ✅ XDG_RUNTIME_DIR or ~/.cache/pdanet-linux location
  - ✅ Create lock with os.open(O_CREAT|O_EXCL) and 0o600
  - ✅ Stale lock detection with PID validation
  - ✅ Proper cleanup on release

### 🔄 In Progress (P1)

- **nmcli Parsing**
  - Use nmcli -t -f SSID,SECURITY,SIGNAL --escape no
  - Parse safely with error handling
  - Retry up to N with exponential backoff + jitter

- **Threading**
  - ThreadPoolExecutor for connection tasks (max_workers=3)
  - Events for cancellation
  - Proper joins on shutdown
  - Monitoring loop interval configurable

- **State Machine**
  - Define valid transitions (DISCONNECTED→CONNECTING→CONNECTED, etc.)
  - Add transition guards and validation
  - Comprehensive logging of state changes

### ⏳ Planned (P2+)

- **Stats & Time**
  - Use time.monotonic() for rate calc
  - Persist session summaries to JSONL or SQLite for history
  - Expose export/import

- **Logging**
  - Python logging with RotatingFileHandler
  - Optional journal integration
  - Log schema and correlation IDs

- **Config**
  - Versioned schema with migrations
  - JSON Schema validation
  - Automatic backup before writes
  - Import/export verified

- **UI Graphs**
  - GtkDrawingArea + Cairo for time-series bandwidth
  - Double-buffered, decimated redraws to keep CPU low

---

## 6) Next Actions (Current Sprint – P1 Critical Functionality)

### Immediate (Next 3 Tasks)

1. **Fix Config Log Level Application** (#131)
   - Update `logger.py` to respect config.log_level
   - Add dynamic log level changes without restart
   - Test with all log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)

2. **Implement State Transition Validation** (#56)
   - Define state transition matrix in `connection_manager.py`
   - Add `_validate_transition(from_state, to_state)` method
   - Prevent illegal transitions with clear error messages
   - Add comprehensive logging

3. **Fix Thread Leaks** (#96-102)
   - Add proper thread join in `stop_monitoring()`
   - Ensure monitoring thread cleanup on disconnect
   - Add ThreadPoolExecutor for connection tasks
   - Test thread count before/after connect/disconnect cycles

### This Week

4. Replace fragile nmcli parsing with -t -f field selection
5. Consolidate connect/disconnect thread logic
6. Implement error recovery and cleanup
7. Fix stealth status display
8. Run comprehensive testing of P1 fixes

---

## 7) Success Criteria (Objective, Measurable)

### ✅ Phase P0 (Security) - COMPLETED

- ✅ 0 open P0 issues
- ✅ No secrets in config.json (keyring preferred, secure fallback)
- ✅ Bandit: 0 High severity issues
- ✅ Ruff: 0 errors in modified files
- ✅ Subprocess calls audited (0 shell=True)
- ✅ Input validation: 33/33 tests passing
- ✅ SECURITY.md complete with threat model

### 🔄 Phase P1 (Critical Functionality) - IN PROGRESS

- Connect/disconnect stable under 100 rapid toggles
- No zombie threads (verified with threading.enumerate())
- Clean shutdown 100% (no orphaned processes/resources)
- Logs reflect configured level in real-time
- nmcli parsing handles edge cases (empty, malformed, timeout)
- Error paths leave system in clean state (iptables, redsocks, flags)

### ⏳ Phase P2+ (Pending)

- **UX**: Real quality metrics visible; window state persists; modal chains reduced; actionable errors with retry
- **Code Quality**: Duplications removed; business logic extracted; constants/enums in place; cyclomatic complexity reduced
- **Testing**: Coverage ≥ 80%; performance budgets: CPU idle < 3%, updates ≤ 1/sec stable; startup < 1.5s
- **Documentation**: CONTRIBUTING.md, API docs, troubleshooting/FAQ present and accurate; README reflects reality; CHANGELOG updated
- **Delivery**: All phases tracked; no regressions; issues mapped to audit IDs; artifacts stored in docs/

---

## 8) Audit Issue Tracking

### ✅ Resolved (P0)

| Issue # | Description | Resolution |
|---------|-------------|------------|
| #291, #117 | Plaintext passwords | ✅ Keyring + migration tool |
| #292, #58-59 | Command injection | ✅ Input validation module |
| #1, #295 | Insecure lockfile | ✅ XDG-compliant + O_EXCL |
| #55, #293 | Privilege escalation | ✅ pkexec-only, no sudo fallback |
| #300-303 | Security docs | ✅ SECURITY.md + audit logging |

### 🔄 In Progress (P1)

| Issue # | Description | Status |
|---------|-------------|--------|
| #131 | Log level not applied | 🔄 Next task |
| #56 | State transition validation | 🔄 Planned |
| #96-102 | Thread leaks | 🔄 Planned |
| #73-75 | Fragile nmcli parsing | 🔄 Planned |
| #86-87, #94 | Thread duplication | 🔄 Planned |
| #1619, #289 | Error recovery | 🔄 Planned |
| #266 | Unbounded threads | 🔄 Planned |
| #522 | Stealth status | 🔄 Planned |

### ⏳ Pending (P2+)

- 300+ remaining issues across UX, Code Quality, Testing, Documentation, Features, Polish

---

## 9) Files Modified/Created (P0 Completed)

### Created Files
- ✅ `src/migrate_passwords.py` - Password migration utility (268 lines)
- ✅ `src/input_validators.py` - Comprehensive input validation (331 lines)
- ✅ `tests/test_input_validators.py` - Security validation tests (420 lines, 33 tests)
- ✅ `SECURITY.md` - Security policy and threat model (450 lines)

### Modified Files
- ✅ `src/connection_manager.py` - Added input validation, improved privilege model
- ✅ `src/pdanet_gui_v2.py` - Secure lockfile implementation, fixed bare except

### Test Results
- ✅ Input validation tests: 33/33 passing
- ✅ Bandit security scan: 0 HIGH severity issues
- ✅ Ruff linting: Clean (0 errors in modified files)

---

*Last Updated: 2025-10-13 22:40 UTC*
*Next Update: After P1 completion*
