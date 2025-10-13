# PdaNet Linux – Professional-Grade Roadmap

Last updated: 2025-10-13
Reference: COMPREHENSIVE_QUALITY_AUDIT_REPORT.md (330+ issues)
Priority Order: P0 Security → P1 Critical Functionality → P2 UX → P3 Code Quality → P4 Testing → P5 Documentation → P6 Features → P7 Polish

---

## 1) Executive Summary

Mission: Elevate PdaNet Linux from “works-for-basic-use” to a secure, robust, and professionally engineered desktop application. We will resolve all P0/P1 issues first, then harden UX, code quality, tests, and documentation, followed by advanced features and polish.

Approach: Execute in phases tightly aligned to the audit priority. Each phase has concrete deliverables, acceptance criteria, and test coverage additions. Security changes include immediate elimination of plaintext secrets and shell-injection risks. Engineering changes emphasize thread safety, error recovery, and modularization. UX changes focus on real metrics, reduced modal friction, and accessible defaults.

Outcomes: Zero P0 vulnerabilities, zero P1 broken features, deterministic behavior across reconnects, strong test coverage with automated checks (linting, security, and regression), and clear, user-friendly documentation.

---

## 2) Objectives

- Security Hardening (P0):
  - Remove all plaintext password storage (#291, #117). Use system keyring (Secret Service/libsecret) via python-keyring.
  - Disallow shell injection by using subprocess list-args only; validate/escape inputs; never shell=True (#292, #55, #58-59).
  - Unify privilege model around pkexec/polkit; remove implicit sudo fallback or fail with guidance (#293).
  - Secure single-instance lock location and creation (XDG-compliant, O_EXCL, permissions) (#1, #295).
  - Add security documentation: threat model, disclosure policy, privileged operation logging (#300-303).

- Critical Reliability (P1):
  - Fix configuration-driven log level application (#131), update stealth status logic (#522), validate state transitions (#56), repair monitoring start/stop leaks (#63, #96-102), and cleanup on error (#1619).
  - Replace fragile nmcli parsing with robust field selection; add retries with backoff (#73, #75, #107).
  - Consolidate connect/disconnect threading and ensure bounded thread usage (#86-87, #94, #99, #266).

- UX & Accessibility (P2):
  - Replace fake quality bar with real metrics (latency, packet loss, throughput trend) (#12, #257).
  - Persist window geometry and key view preferences; reduce modal dialogs; actionable errors (#245-250).
  - Keyboard navigation/focus indicators; configurable font size; high-DPI support (#242-244, #201-204).

- Code Quality & Architecture (P3):
  - Extract speedtest and network scanning to dedicated modules; remove duplication (#36, #39-43, #1000-1063).
  - Introduce constants/enums; remove magic numbers; implement event bus/signals; reduce tight coupling (#12, #24-27, #320-330, #324).

- Testing (P4):
  - Add unit, integration, performance, and visual tests for identified gaps (#187-218, #206-210, #201-205).
  - Security and edge-case tests (special chars in SSID/password, flapping, suspend) (#211-218).

- Documentation (P5):
  - Add SECURITY.md, CONTRIBUTING.md, CODE_OF_CONDUCT.md, API docs, troubleshooting/FAQ, disaster recovery, legal guidance notes (#156-181).

- Advanced Features (P6) & Polish (P7):
  - Bandwidth graphs and historical persistence (#315), first-run wizard, VPN handoff, profile enhancements, dark mode toggle, visual refinements.

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
  - Skeleton placeholders for stats; explicit “No data yet” empty states; descriptive error banners with next steps.

- Accessibility & Internationalization
  - Focus rings, consistent keyboard traversal, minimum touch targets ≈ 44 px.
  - Prepare strings for i18n; avoid hardcoded text scattered in code (#1026-1032).

- Motion & Performance
  - Subtle transitions only; animate transform/opacity if any; keep CPU overhead low.

---

## 4) Implementation Steps (Phased)

### Phase P0 – Security (Immediate)
- Credentials
  - Introduce keyring backend (Secret Service/libsecret) for WiFi passwords (#291, #117).
  - Migration on startup: detect plaintext credentials → write to keyring → remove from config; backup config.
- Command & Privileges
  - Replace all shell invocations with subprocess list-args; input validation for SSID/password/hostnames (#292, #58-59, #72-75).
  - Centralize privileged execution around pkexec; explicit error if unavailable; remove silent sudo fallback (#55, #293).
- Locking & Filesystem
  - Move lock to XDG runtime or ~/.cache; create with O_EXCL, 0600 permissions (#1, #295).
- Security Docs & Logging
  - SECURITY.md, threat model, disclosure policy; audit log for privileged calls (#300-303).
- Acceptance: No secrets in config.json; bandit clean (no high); ruff clean; all commands run without shell; startup migration succeeds; manual pen-test of SSID/password injection.

### Phase P1 – Critical Functionality
- Config & Logging
  - Apply config-specified log level (#131); implement rotating log file; journal integration optional (#122-123).
- State & Threads
  - Validate state transitions (#56), consolidate connect/disconnect logic; bounded ThreadPool; proper join/stop (#86-87, #94, #96-102).
- nmcli & Interface Detection
  - Use nmcli -t -f with robust parsing and retries/backoff (#73-75, #90-93).
- Error Recovery
  - Cleanup iptables/redsocks on failure paths; clear stale current_mode and monitoring flags (#85, #1619, #289).
- Acceptance: Stable connect/disconnect under rapid toggles; no orphaned threads; consistent states after failures; logs reflect configured level.

### Phase P2 – User Experience
- Real Quality Metrics
  - Replace placeholder progress with real latency/loss + throughput trend (#12, #257).
- Windows & Dialogs
  - Persist window geometry; convert stacked modals to Preferences window flows (#245-246).
- Messaging & Help
  - Actionable error dialogs, tooltips, inline help; keyboard shortcuts and focus indicators (#247-249, #243).
- Acceptance: Clear metrics visible; reduced modal friction; persisted UI prefs; accessibility checks pass.

### Phase P3 – Code Quality & Architecture
- Modularization
  - Extract speedtest and network scanning from GUI; add abstraction for subprocess/network ops (#36, #39-43, #1000-1063, #330).
- Constants & Config
  - Centralize strings/enums; remove magic numbers (timeouts, TTL) with config and sane defaults (#324).
- Eventing & DI
  - Simple event bus or GObject signals; limit globals/singletons; thread-safe singletons (#106-107, #325-329).
- Acceptance: Reduced duplication, isolated business logic, improved testability; static analysis cleaner.

### Phase P4 – Testing
- Unit
  - Add tests for threading/race, config corruption, monotonic time for stats, input validation (#187-190, #111-112, #211-218).
- Integration
  - Simulated connection flows with nmcli/iptables mocks; failover/network flapping; suspend/resume.
- Visual/Performance
  - Visual snapshots across DPI/scales; CPU/memory/startup benchmarks (#201-210).
- Security Tests
  - Injection attempts; missing polkit; keyring unavailable fallback paths.
- Acceptance: Coverage ≥ 80%; performance budgets met; visual tests stable.

### Phase P5 – Documentation
- Author SECURITY.md, CONTRIBUTING.md, CODE_OF_CONDUCT.md, API docs for modules, troubleshooting flowchart, FAQ, disaster recovery, legal guidance overview (#156-181).
- Update README with accurate claims, coverage metrics, screenshots, and versioned CHANGELOG.
- Acceptance: Docs complete and accurate; links validated.

### Phase P6 – Advanced Features
- Bandwidth Graph & History
  - Time-series bandwidth graph with ring buffer; persist historical usage (#315, #112, #114).
- First-Run Setup Wizard
  - Guided onboarding for profiles, permissions, and defaults.
- VPN Handoff & Profiles
  - Optional auto-VPN post-connect; improved profile quick-switch.
- Acceptance: Features stable, documented, and tested.

### Phase P7 – Polish
- Theming & Icons
  - Dark/light toggle; symbolic icon set; fine spacing/contrast.
- Accessibility
  - Larger touch targets; keyboard help overlay; i18n hooks.
- Packaging
  - Deb/RPM/AppImage (time permitting) and install/uninstall safety improvements (#231-235, #219-230).
- Acceptance: Professional finish; installer/uninstaller safe; consistent cross-desktop behavior.

---

## 5) Technical Details (Key Decisions)

- Secure Secrets
  - Use python-keyring with Secret Service backend on Linux. Store per-SSID credentials as service="pdanet-linux", username=f"wifi:{ssid}". On migration, backup config, delete plaintext.
- Safe Subprocess
  - Common run_command(cmd: list[str], timeout, env) utility; never shell=True. Validate inputs (SSID, password, IP/host). Structured error handling and logging.
- Privilege Model
  - pkexec-based elevation with clear user messaging and error if unavailable; remove implicit sudo fallback.
- Locking
  - Use XDG_RUNTIME_DIR or ~/.cache/pdanet-linux; create lock with os.open(O_CREAT|O_EXCL) and 0o600; handle stale lock.
- nmcli Parsing
  - Use nmcli -t -f SSID,SECURITY,SIGNAL --escape no; parse safely; retry up to N with jitter.
- Threading
  - ThreadPoolExecutor for connection tasks; Events for cancellation; joins on shutdown; monitoring loop interval configurable.
- Stats & Time
  - Use time.monotonic() for rate calc; persist session summaries to JSONL or SQLite for history; expose export/import.
- Logging
  - Python logging with RotatingFileHandler; optional journal integration; log schema and correlation IDs.
- Config
  - Versioned schema with migrations; JSON Schema validation; automatic backup before writes; import/export verified.
- UI Graphs
  - GtkDrawingArea + Cairo for time-series bandwidth; double-buffered, decimated redraws to keep CPU low.

---

## 6) Next Actions (Week 1 Sprint – P0 Security)
1. Add python-keyring, implement credentials store + migration path.
2. Replace all shell usages with list-args; central run_command; validate inputs.
3. Unify privileged operations under pkexec; add clear error messages.
4. Secure lockfile path/creation; remove /tmp usage.
5. Add SECURITY.md + threat model + privileged ops audit log.
6. Run bandit/ruff; fix findings; manual injection tests; update CHANGELOG.

---

## 7) Success Criteria (Objective, Measurable)
- Security
  - 0 open P0 issues; no secrets in config; bandit: 0 High; ruff: 0 errors; subprocess calls audited (0 shell=True).
- Reliability
  - Connect/disconnect stable under 100 rapid toggles; no zombie threads; clean shutdown 100%.
- UX
  - Real quality metrics visible; window state persists; modal chains reduced; actionable errors with retry.
- Code Quality
  - Duplications removed; business logic extracted; constants/enums in place; cyclomatic complexity reduced in key modules.
- Testing
  - Coverage ≥ 80%; performance budgets: CPU idle < 3%, updates ≤ 1/sec stable; startup < 1.5s on reference VM.
- Documentation
  - SECURITY.md, CONTRIBUTING.md, API docs, troubleshooting/FAQ present and accurate; README reflects reality; CHANGELOG updated.
- Delivery
  - All phases tracked; no regressions; issues mapped to audit IDs; artifacts (reports/screenshots) stored in docs/.
