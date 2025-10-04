# Visual Testing Makefile for PdaNet Linux
# Professional automation for visual regression testing

.PHONY: help install test test-all test-regression test-responsive test-accessibility test-components
.PHONY: baselines update-baselines clean reports serve-reports ci setup-headless
.PHONY: validate-environment check-dependencies

# Default target
.DEFAULT_GOAL := help

# Configuration
PYTHON := python3
PIP := pip3
VENV_DIR := .venv
TEST_DIR := tests/visual
REPORTS_DIR := $(TEST_DIR)/reports
BASELINE_DIR := $(TEST_DIR)/baseline
DISPLAY := :99
RESOLUTION := 1920x1080x24

# Colors for output (cyberpunk theme)
GREEN := \033[0;32m
RED := \033[0;31m
YELLOW := \033[1;33m
CYAN := \033[0;36m
NC := \033[0m # No Color

help: ## Show this help message
	@echo "$(CYAN)PdaNet Linux Visual Testing Suite$(NC)"
	@echo "$(YELLOW)Cyberpunk-themed GUI visual regression testing$(NC)"
	@echo ""
	@echo "$(GREEN)Available targets:$(NC)"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  $(CYAN)%-20s$(NC) %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo ""
	@echo "$(YELLOW)Examples:$(NC)"
	@echo "  make install          # Install dependencies"
	@echo "  make test-all         # Run all visual tests"
	@echo "  make baselines        # Create new baselines"
	@echo "  make ci               # Run CI-style tests"

install: ## Install all dependencies for visual testing
	@echo "$(YELLOW)Installing visual testing dependencies...$(NC)"
	@sudo apt-get update -qq
	@sudo apt-get install -y \
		xvfb \
		gnome-screenshot \
		scrot \
		imagemagick \
		python3-gi \
		python3-gi-cairo \
		gir1.2-gtk-3.0 \
		gir1.2-appindicator3-0.1 \
		libcairo2-dev \
		libgirepository1.0-dev \
		jq \
		bc
	@$(PIP) install --break-system-packages -r requirements.txt
	@$(PIP) install --break-system-packages pytest pytest-xvfb pytest-timeout pillow numpy
	@echo "$(GREEN)✓ Dependencies installed$(NC)"

setup-headless: ## Set up headless display environment
	@echo "$(YELLOW)Setting up headless display...$(NC)"
	@pkill Xvfb || true
	@sleep 1
	@Xvfb $(DISPLAY) -screen 0 $(RESOLUTION) -ac +extension GLX +render -noreset &
	@sleep 3
	@DISPLAY=$(DISPLAY) xdpyinfo > /dev/null && echo "$(GREEN)✓ Virtual display ready$(NC)" || (echo "$(RED)✗ Virtual display failed$(NC)" && exit 1)

validate-environment: ## Validate testing environment
	@echo "$(YELLOW)Validating environment...$(NC)"
	@command -v $(PYTHON) >/dev/null 2>&1 || (echo "$(RED)✗ Python not found$(NC)" && exit 1)
	@command -v gnome-screenshot >/dev/null 2>&1 || command -v scrot >/dev/null 2>&1 || (echo "$(RED)✗ Screenshot tools not found$(NC)" && exit 1)
	@$(PYTHON) -c "import gi; gi.require_version('Gtk', '3.0'); from gi.repository import Gtk" 2>/dev/null || (echo "$(RED)✗ GTK3 Python bindings not found$(NC)" && exit 1)
	@test -n "$(DISPLAY)" || (echo "$(RED)✗ DISPLAY not set$(NC)" && exit 1)
	@DISPLAY=$(DISPLAY) xdpyinfo >/dev/null 2>&1 || (echo "$(RED)✗ Display not accessible$(NC)" && exit 1)
	@echo "$(GREEN)✓ Environment validated$(NC)"

check-dependencies: ## Check if all dependencies are available
	@echo "$(YELLOW)Checking dependencies...$(NC)"
	@echo "Python: $$($(PYTHON) --version 2>&1)"
	@echo "Display: $(DISPLAY)"
	@echo "Screenshots: $$(command -v gnome-screenshot || command -v scrot || echo 'MISSING')"
	@echo "GTK3: $$($(PYTHON) -c 'import gi; print("Available")' 2>/dev/null || echo 'MISSING')"
	@echo "$(GREEN)✓ Dependency check complete$(NC)"

test: test-all ## Alias for test-all

test-all: validate-environment ## Run complete visual test suite
	@echo "$(YELLOW)Running complete visual test suite...$(NC)"
	@cd $(TEST_DIR) && DISPLAY=$(DISPLAY) $(PYTHON) visual_test_runner.py --all --output-dir $(REPORTS_DIR)
	@echo "$(GREEN)✓ All visual tests completed$(NC)"
	@$(MAKE) --no-print-directory summary

test-regression: validate-environment ## Run visual regression tests only
	@echo "$(YELLOW)Running visual regression tests...$(NC)"
	@cd $(TEST_DIR) && DISPLAY=$(DISPLAY) $(PYTHON) visual_test_runner.py --regression --output-dir $(REPORTS_DIR)
	@echo "$(GREEN)✓ Regression tests completed$(NC)"

test-responsive: validate-environment ## Run responsive design tests only
	@echo "$(YELLOW)Running responsive design tests...$(NC)"
	@cd $(TEST_DIR) && DISPLAY=$(DISPLAY) $(PYTHON) visual_test_runner.py --responsive --output-dir $(REPORTS_DIR)
	@echo "$(GREEN)✓ Responsive tests completed$(NC)"

test-accessibility: validate-environment ## Run accessibility tests only
	@echo "$(YELLOW)Running accessibility tests...$(NC)"
	@cd $(TEST_DIR) && DISPLAY=$(DISPLAY) $(PYTHON) visual_test_runner.py --accessibility --output-dir $(REPORTS_DIR)
	@echo "$(GREEN)✓ Accessibility tests completed$(NC)"

test-components: validate-environment ## Run component tests only
	@echo "$(YELLOW)Running component tests...$(NC)"
	@cd $(TEST_DIR) && DISPLAY=$(DISPLAY) $(PYTHON) visual_test_runner.py --components --output-dir $(REPORTS_DIR)
	@echo "$(GREEN)✓ Component tests completed$(NC)"

baselines: validate-environment ## Create new visual baselines
	@echo "$(YELLOW)Creating new visual baselines...$(NC)"
	@echo "$(RED)WARNING: This will replace existing baselines!$(NC)"
	@read -p "Continue? [y/N] " -n 1 -r; echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		cd $(TEST_DIR) && DISPLAY=$(DISPLAY) $(PYTHON) visual_test_runner.py --all --create-baselines --output-dir $(REPORTS_DIR); \
		echo "$(GREEN)✓ New baselines created$(NC)"; \
	else \
		echo "$(YELLOW)Baseline creation cancelled$(NC)"; \
	fi

update-baselines: validate-environment ## Update existing baselines
	@echo "$(YELLOW)Updating visual baselines...$(NC)"
	@cd $(TEST_DIR) && DISPLAY=$(DISPLAY) $(PYTHON) visual_test_runner.py --all --update-baselines --output-dir $(REPORTS_DIR)
	@echo "$(GREEN)✓ Baselines updated$(NC)"

pytest: validate-environment ## Run tests using pytest
	@echo "$(YELLOW)Running visual tests with pytest...$(NC)"
	@cd $(TEST_DIR) && DISPLAY=$(DISPLAY) pytest -v --tb=short
	@echo "$(GREEN)✓ Pytest completed$(NC)"

pytest-verbose: validate-environment ## Run tests using pytest with verbose output
	@echo "$(YELLOW)Running visual tests with pytest (verbose)...$(NC)"
	@cd $(TEST_DIR) && DISPLAY=$(DISPLAY) pytest -v -s --tb=long
	@echo "$(GREEN)✓ Pytest completed$(NC)"

ci: setup-headless ## Run CI-style tests (headless, comprehensive)
	@echo "$(YELLOW)Running CI-style visual tests...$(NC)"
	@export CI=true && export VISUAL_TEST_MODE=ci && \
	cd $(TEST_DIR) && DISPLAY=$(DISPLAY) $(PYTHON) visual_test_runner.py --all --output-dir $(REPORTS_DIR)
	@echo "$(GREEN)✓ CI tests completed$(NC)"
	@$(MAKE) --no-print-directory summary

summary: ## Show test results summary
	@echo "$(CYAN)Visual Test Results Summary$(NC)"
	@echo "=========================="
	@if [ -f "$(REPORTS_DIR)/comprehensive_visual_test_report.json" ]; then \
		TOTAL=$$(jq -r '.summary.total_tests' $(REPORTS_DIR)/comprehensive_visual_test_report.json); \
		PASSED=$$(jq -r '.summary.total_passed' $(REPORTS_DIR)/comprehensive_visual_test_report.json); \
		RATE=$$(jq -r '.summary.overall_pass_rate' $(REPORTS_DIR)/comprehensive_visual_test_report.json); \
		echo "Total Tests: $$TOTAL"; \
		echo "Passed Tests: $$PASSED"; \
		echo "Pass Rate: $$RATE%"; \
		if (( $$(echo "$$RATE >= 95" | bc -l) )); then \
			echo "$(GREEN)Status: EXCELLENT ✓$(NC)"; \
		elif (( $$(echo "$$RATE >= 80" | bc -l) )); then \
			echo "$(YELLOW)Status: NEEDS ATTENTION ⚠$(NC)"; \
		else \
			echo "$(RED)Status: FAILING ✗$(NC)"; \
		fi; \
	else \
		echo "$(RED)No test results found$(NC)"; \
	fi

reports: ## Generate and display test reports
	@echo "$(YELLOW)Available test reports:$(NC)"
	@find $(REPORTS_DIR) -name "*.json" -o -name "*.html" | sort | while read report; do \
		echo "  $$(basename $$report)"; \
	done
	@echo ""
	@echo "$(CYAN)View HTML report:$(NC)"
	@echo "  make serve-reports"

serve-reports: ## Serve test reports via HTTP
	@echo "$(YELLOW)Serving test reports at http://localhost:8080$(NC)"
	@echo "$(CYAN)Press Ctrl+C to stop$(NC)"
	@cd $(REPORTS_DIR) && $(PYTHON) -m http.server 8080

clean: ## Clean up test artifacts and temporary files
	@echo "$(YELLOW)Cleaning up test artifacts...$(NC)"
	@rm -rf $(REPORTS_DIR)/*.json
	@rm -rf $(REPORTS_DIR)/*.html
	@rm -rf $(TEST_DIR)/screenshots/*_test_*.png
	@rm -rf $(TEST_DIR)/diff/*_test_*.png
	@rm -rf /tmp/pdanet_visual_test_*
	@rm -rf /tmp/component_contrast_test.png
	@echo "$(GREEN)✓ Cleanup completed$(NC)"

clean-all: clean ## Clean everything including baselines (DANGEROUS)
	@echo "$(RED)WARNING: This will delete all baselines!$(NC)"
	@read -p "Continue? [y/N] " -n 1 -r; echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		rm -rf $(BASELINE_DIR)/*; \
		rm -rf $(TEST_DIR)/components/baseline/*; \
		rm -rf $(TEST_DIR)/responsive/baseline/*; \
		echo "$(GREEN)✓ All artifacts cleaned$(NC)"; \
	else \
		echo "$(YELLOW)Cleanup cancelled$(NC)"; \
	fi

backup-baselines: ## Backup current baselines
	@echo "$(YELLOW)Backing up baselines...$(NC)"
	@BACKUP_DIR="$(TEST_DIR)/baseline_backup_$$(date +%Y%m%d_%H%M%S)"; \
	mkdir -p "$$BACKUP_DIR"; \
	cp -r $(BASELINE_DIR)/* "$$BACKUP_DIR/" 2>/dev/null || true; \
	cp -r $(TEST_DIR)/components/baseline/* "$$BACKUP_DIR/components/" 2>/dev/null || true; \
	cp -r $(TEST_DIR)/responsive/baseline/* "$$BACKUP_DIR/responsive/" 2>/dev/null || true; \
	echo "$(GREEN)✓ Baselines backed up to $$BACKUP_DIR$(NC)"

restore-baselines: ## Restore baselines from backup
	@echo "$(YELLOW)Available baseline backups:$(NC)"
	@ls -1 $(TEST_DIR)/baseline_backup_* 2>/dev/null | sed 's/.*baseline_backup_/  /' || echo "  No backups found"
	@echo ""
	@read -p "Enter backup timestamp (YYYYMMDD_HHMMSS): " backup; \
	BACKUP_DIR="$(TEST_DIR)/baseline_backup_$$backup"; \
	if [ -d "$$BACKUP_DIR" ]; then \
		cp -r "$$BACKUP_DIR"/* $(BASELINE_DIR)/ 2>/dev/null || true; \
		echo "$(GREEN)✓ Baselines restored from $$backup$(NC)"; \
	else \
		echo "$(RED)✗ Backup not found$(NC)"; \
	fi

debug: validate-environment ## Run visual tests in debug mode
	@echo "$(YELLOW)Running visual tests in debug mode...$(NC)"
	@cd $(TEST_DIR) && DISPLAY=$(DISPLAY) PDANET_LOG_LEVEL=DEBUG PDANET_KEEP_TEMP=1 $(PYTHON) visual_test_runner.py --all --output-dir $(REPORTS_DIR)

lint-tests: ## Lint visual test code
	@echo "$(YELLOW)Linting visual test code...$(NC)"
	@$(PYTHON) -m flake8 $(TEST_DIR)/*.py --max-line-length=120 --ignore=E501,W503
	@$(PYTHON) -m mypy $(TEST_DIR)/*.py --ignore-missing-imports || true
	@echo "$(GREEN)✓ Linting completed$(NC)"

format-tests: ## Format visual test code
	@echo "$(YELLOW)Formatting visual test code...$(NC)"
	@$(PYTHON) -m black $(TEST_DIR)/*.py --line-length=120
	@$(PYTHON) -m isort $(TEST_DIR)/*.py
	@echo "$(GREEN)✓ Formatting completed$(NC)"

quick-test: validate-environment ## Quick visual test (regression only)
	@echo "$(YELLOW)Running quick visual test...$(NC)"
	@cd $(TEST_DIR) && DISPLAY=$(DISPLAY) $(PYTHON) visual_test_runner.py --regression --output-dir $(REPORTS_DIR)
	@if [ -f "$(REPORTS_DIR)/regression_report.json" ]; then \
		PASSED=$$(jq -r '.passed_tests' $(REPORTS_DIR)/regression_report.json); \
		TOTAL=$$(jq -r '.total_tests' $(REPORTS_DIR)/regression_report.json); \
		echo "Quick test: $$PASSED/$$TOTAL passed"; \
	fi

status: ## Show current test environment status
	@echo "$(CYAN)Visual Testing Environment Status$(NC)"
	@echo "================================="
	@echo "Display: $(DISPLAY)"
	@echo "Python: $$($(PYTHON) --version 2>&1)"
	@echo "Working Dir: $$(pwd)"
	@echo "Test Dir: $(TEST_DIR)"
	@echo "Reports Dir: $(REPORTS_DIR)"
	@echo ""
	@echo "$(YELLOW)Recent test results:$(NC)"
	@ls -lt $(REPORTS_DIR)/*.json 2>/dev/null | head -3 | awk '{print "  " $$9 " (" $$6 " " $$7 " " $$8 ")"}' || echo "  No recent results"
	@echo ""
	@echo "$(YELLOW)Baseline status:$(NC)"
	@BASELINE_COUNT=$$(find $(BASELINE_DIR) -name "*.png" 2>/dev/null | wc -l); \
	echo "  Baseline images: $$BASELINE_COUNT"

# Development targets
dev-setup: install setup-headless ## Complete development setup
	@echo "$(GREEN)✓ Development environment ready$(NC)"
	@$(MAKE) --no-print-directory status

dev-test: format-tests lint-tests quick-test ## Development testing workflow
	@echo "$(GREEN)✓ Development testing completed$(NC)"

# Performance monitoring
benchmark: validate-environment ## Benchmark visual test performance
	@echo "$(YELLOW)Benchmarking visual test performance...$(NC)"
	@time $(MAKE) --no-print-directory test-regression > /dev/null
	@echo "$(GREEN)✓ Benchmark completed$(NC)"

# Documentation
docs: ## Generate testing documentation
	@echo "$(YELLOW)Visual testing documentation available:$(NC)"
	@echo "  README.md - Comprehensive testing guide"
	@echo "  $(TEST_DIR)/ - Source code with docstrings"
	@echo "  Reports - Generated after test runs"

info: ## Show detailed project information
	@echo "$(CYAN)PdaNet Linux Visual Testing Suite$(NC)"
	@echo "=================================="
	@echo ""
	@echo "$(YELLOW)Purpose:$(NC) Automated visual regression testing for cyberpunk GTK GUI"
	@echo "$(YELLOW)Coverage:$(NC) Visual regression, responsive design, accessibility, components"
	@echo "$(YELLOW)Theme:$(NC) Cyberpunk aesthetic validation (black, green, red, yellow)"
	@echo "$(YELLOW)Standards:$(NC) WCAG AA accessibility compliance"
	@echo ""
	@echo "$(YELLOW)Test Suites:$(NC)"
	@echo "  • Visual Regression - Screenshot comparison with baselines"
	@echo "  • Responsive Design - Multi-breakpoint layout validation"
	@echo "  • Accessibility - WCAG compliance and color analysis"
	@echo "  • Components - Individual UI element testing"
	@echo ""
	@echo "$(YELLOW)Key Features:$(NC)"
	@echo "  • Headless testing with Xvfb"
	@echo "  • CI/CD integration with GitHub Actions"
	@echo "  • Comprehensive HTML reporting"
	@echo "  • Baseline management and versioning"
	@echo "  • Professional cyberpunk theme validation"