# PdaNet Linux - Architecture Documentation Makefile
# Automates documentation building, validation, and publishing

.PHONY: docs diagrams validate-docs publish-docs clean-docs help
.DEFAULT_GOAL := help

# Directories
DOCS_DIR := docs
ARCHITECTURE_DIR := $(DOCS_DIR)/architecture
BUILD_DIR := $(DOCS_DIR)/build
SCRIPTS_DIR := scripts

# Tools
PYTHON := python3
PLANTUML_JAR := tools/plantuml.jar

# Colors for output
GREEN := \033[0;32m
YELLOW := \033[1;33m
RED := \033[0;31m
NC := \033[0m # No Color

help: ## Show this help message
	@echo "PdaNet Linux Documentation Build System"
	@echo "========================================="
	@echo ""
	@echo "Available targets:"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  $(GREEN)%-15s$(NC) %s\n", $$1, $$2}' $(MAKEFILE_LIST)

docs: diagrams ## Generate complete documentation
	@echo "$(GREEN)Building complete PdaNet Linux documentation...$(NC)"
	@mkdir -p $(BUILD_DIR)
	@if [ -f "$(SCRIPTS_DIR)/build-docs.sh" ]; then \
		chmod +x $(SCRIPTS_DIR)/build-docs.sh && $(SCRIPTS_DIR)/build-docs.sh; \
	else \
		echo "$(YELLOW)Warning: build-docs.sh not found, running basic build$(NC)"; \
		$(MAKE) diagrams; \
	fi
	@echo "$(GREEN)Documentation build complete. Output in: $(BUILD_DIR)$(NC)"

diagrams: ## Generate architecture diagrams from PlantUML files
	@echo "$(GREEN)Generating architecture diagrams...$(NC)"
	@chmod +x $(SCRIPTS_DIR)/generate-diagrams.sh
	@$(SCRIPTS_DIR)/generate-diagrams.sh
	@echo "$(GREEN)Diagrams generated successfully$(NC)"

validate-docs: ## Validate documentation for errors and consistency
	@echo "$(GREEN)Validating documentation...$(NC)"
	@if [ -f "$(SCRIPTS_DIR)/validate-docs.py" ]; then \
		$(PYTHON) $(SCRIPTS_DIR)/validate-docs.py; \
	else \
		echo "$(YELLOW)Warning: validate-docs.py not found, skipping validation$(NC)"; \
	fi

check-links: ## Check for broken internal links
	@echo "$(GREEN)Checking documentation links...$(NC)"
	@if [ -f "$(SCRIPTS_DIR)/check-links.py" ]; then \
		$(PYTHON) $(SCRIPTS_DIR)/check-links.py; \
	else \
		echo "$(YELLOW)Warning: check-links.py not found, skipping link check$(NC)"; \
	fi

publish-docs: docs validate-docs ## Build, validate, and publish documentation
	@echo "$(GREEN)Publishing documentation...$(NC)"
	@if [ -f "$(SCRIPTS_DIR)/publish-docs.sh" ]; then \
		chmod +x $(SCRIPTS_DIR)/publish-docs.sh && $(SCRIPTS_DIR)/publish-docs.sh; \
	else \
		echo "$(YELLOW)Warning: publish-docs.sh not found, copying to build directory$(NC)"; \
		cp -r $(ARCHITECTURE_DIR)/*.md $(BUILD_DIR)/ 2>/dev/null || true; \
	fi

clean-docs: ## Clean generated documentation files
	@echo "$(GREEN)Cleaning generated documentation...$(NC)"
	@rm -rf $(BUILD_DIR)
	@rm -rf $(ARCHITECTURE_DIR)/generated
	@echo "$(GREEN)Cleanup complete$(NC)"

serve-docs: docs ## Build docs and serve locally on port 8080
	@echo "$(GREEN)Starting documentation server on http://localhost:8080$(NC)"
	@cd $(BUILD_DIR) && $(PYTHON) -m http.server 8080

watch-docs: ## Watch for changes and rebuild diagrams automatically
	@echo "$(GREEN)Watching for documentation changes...$(NC)"
	@echo "$(YELLOW)Install 'entr' for file watching: sudo apt install entr$(NC)"
	@if command -v entr >/dev/null 2>&1; then \
		find $(DOCS_DIR) -name "*.md" -o -name "*.puml" | entr $(MAKE) diagrams; \
	else \
		echo "$(RED)Error: 'entr' not installed. Install with: sudo apt install entr$(NC)"; \
		exit 1; \
	fi

new-adr: ## Create new ADR (Usage: make new-adr TITLE="Your Title")
	@if [ -z "$(TITLE)" ]; then \
		echo "$(RED)Error: Please provide a title. Usage: make new-adr TITLE=\"Your Title\"$(NC)"; \
		exit 1; \
	fi
	@if [ -f "$(SCRIPTS_DIR)/new-adr.sh" ]; then \
		chmod +x $(SCRIPTS_DIR)/new-adr.sh && $(SCRIPTS_DIR)/new-adr.sh "$(TITLE)"; \
	else \
		echo "$(RED)Error: new-adr.sh script not found$(NC)"; \
		exit 1; \
	fi

metrics: ## Generate documentation metrics
	@echo "$(GREEN)Generating documentation metrics...$(NC)"
	@if [ -f "$(SCRIPTS_DIR)/doc-metrics.py" ]; then \
		$(PYTHON) $(SCRIPTS_DIR)/doc-metrics.py $(DOCS_DIR) $(BUILD_DIR)/metrics.json; \
		cat $(BUILD_DIR)/metrics.json | $(PYTHON) -m json.tool; \
	else \
		echo "$(YELLOW)Warning: doc-metrics.py not found$(NC)"; \
	fi

install-deps: ## Install documentation build dependencies
	@echo "$(GREEN)Installing documentation dependencies...$(NC)"
	@sudo apt-get update
	@sudo apt-get install -y pandoc default-jre entr
	@if [ -f "$(SCRIPTS_DIR)/requirements.txt" ]; then \
		pip3 install --user -r $(SCRIPTS_DIR)/requirements.txt; \
	fi
	@echo "$(GREEN)Dependencies installed$(NC)"

test-docs: validate-docs check-links ## Run all documentation tests
	@echo "$(GREEN)Running all documentation tests...$(NC)"
	@echo "$(GREEN)All documentation tests passed$(NC)"

update-diagrams: ## Update only changed diagrams (faster than full rebuild)
	@echo "$(GREEN)Updating changed diagrams...$(NC)"
	@if [ -f "$(SCRIPTS_DIR)/update-diagrams.py" ]; then \
		$(PYTHON) $(SCRIPTS_DIR)/update-diagrams.py; \
	else \
		echo "$(YELLOW)Warning: update-diagrams.py not found, running full diagram generation$(NC)"; \
		$(MAKE) diagrams; \
	fi

status: ## Show documentation status and metrics
	@echo "$(GREEN)PdaNet Linux Documentation Status$(NC)"
	@echo "=================================="
	@echo "Documentation directory: $(DOCS_DIR)"
	@echo "Build directory: $(BUILD_DIR)"
	@echo ""
	@echo "Files:"
	@find $(DOCS_DIR) -name "*.md" | wc -l | xargs echo "  Markdown files:"
	@find $(DOCS_DIR) -name "*.puml" | wc -l | xargs echo "  PlantUML diagrams:"
	@if [ -d "$(BUILD_DIR)" ]; then \
		find $(BUILD_DIR) -name "*.html" | wc -l | xargs echo "  Generated HTML files:"; \
		find $(BUILD_DIR) -name "*.png" | wc -l | xargs echo "  Generated PNG diagrams:"; \
	else \
		echo "  Generated files: 0 (run 'make docs' to build)"; \
	fi

# Development targets
dev-setup: install-deps ## Setup development environment
	@echo "$(GREEN)Setting up development environment...$(NC)"
	@mkdir -p $(DOCS_DIR)/{architecture/{adrs,generated},build}
	@mkdir -p $(SCRIPTS_DIR)
	@mkdir -p tools
	@echo "$(GREEN)Development environment ready$(NC)"

dev-docs: ## Development mode: build and serve with file watching
	@echo "$(GREEN)Starting development documentation server...$(NC)"
	@echo "$(YELLOW)This will build docs, start server, and watch for changes$(NC)"
	@$(MAKE) docs
	@echo "$(GREEN)Opening browser and starting file watcher...$(NC)"
	@(sleep 2 && command -v xdg-open >/dev/null && xdg-open http://localhost:8080) &
	@(cd $(BUILD_DIR) && $(PYTHON) -m http.server 8080) &
	@SERVER_PID=$$!; \
	find $(DOCS_DIR) -name "*.md" -o -name "*.puml" | entr -r $(MAKE) diagrams; \
	kill $$SERVER_PID

# Quality assurance
qa: test-docs metrics ## Run quality assurance checks
	@echo "$(GREEN)Quality assurance complete$(NC)"

# Maintenance
maintenance: ## Run maintenance tasks
	@echo "$(GREEN)Running documentation maintenance...$(NC)"
	@if [ -f "$(SCRIPTS_DIR)/weekly-maintenance.sh" ]; then \
		chmod +x $(SCRIPTS_DIR)/weekly-maintenance.sh && $(SCRIPTS_DIR)/weekly-maintenance.sh; \
	else \
		$(MAKE) clean-docs && $(MAKE) docs && $(MAKE) validate-docs; \
	fi

# Check if required tools are installed
check-deps: ## Check if required dependencies are installed
	@echo "$(GREEN)Checking documentation dependencies...$(NC)"
	@command -v java >/dev/null 2>&1 || (echo "$(RED)✗ Java not found$(NC)" && exit 1)
	@command -v $(PYTHON) >/dev/null 2>&1 || (echo "$(RED)✗ Python 3 not found$(NC)" && exit 1)
	@command -v pandoc >/dev/null 2>&1 || echo "$(YELLOW)⚠ Pandoc not found (optional)$(NC)"
	@command -v entr >/dev/null 2>&1 || echo "$(YELLOW)⚠ entr not found (optional, for watch mode)$(NC)"
	@echo "$(GREEN)✓ Core dependencies satisfied$(NC)"

# Print useful information
info: ## Show build information and paths
	@echo "$(GREEN)PdaNet Linux Documentation Build Information$(NC)"
	@echo "=============================================="
	@echo "Build system: GNU Make"
	@echo "Python: $(shell $(PYTHON) --version 2>/dev/null || echo 'Not found')"
	@echo "Java: $(shell java -version 2>&1 | head -n1 || echo 'Not found')"
	@echo "PlantUML: $(if $(wildcard $(PLANTUML_JAR)),Available,Not downloaded)"
	@echo ""
	@echo "Directories:"
	@echo "  Documentation: $(DOCS_DIR)"
	@echo "  Architecture: $(ARCHITECTURE_DIR)"
	@echo "  Build output: $(BUILD_DIR)"
	@echo "  Scripts: $(SCRIPTS_DIR)"
	@echo ""
	@echo "Quick start:"
	@echo "  make docs      # Build all documentation"
	@echo "  make serve     # Build and serve on localhost:8080"
	@echo "  make help      # Show all available targets"