#!/bin/bash
#
# run_maintenance.sh - Documentation Maintenance Runner
# Convenient script to run documentation maintenance tasks
#

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Default configuration
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
TOOLS_DIR="$PROJECT_ROOT/tools/docs-maintenance"
FORCE_ALL=false
SPECIFIC_TASKS=""
QUIET=false

# Help function
show_help() {
    echo -e "${BLUE}PdaNet Linux - Documentation Maintenance Runner${NC}"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -h, --help              Show this help message"
    echo "  -p, --project PATH      Project root directory (default: auto-detected)"
    echo "  -t, --tasks TASKS       Comma-separated list of tasks to run"
    echo "  -f, --force-all         Run all tasks including disabled ones"
    echo "  -q, --quiet             Suppress verbose output"
    echo "  -c, --check-deps        Check and install dependencies"
    echo "  -s, --setup             Initial setup of maintenance system"
    echo ""
    echo "Available tasks:"
    echo "  audit               Comprehensive documentation audit"
    echo "  link_validation     Validate internal and external links"
    echo "  style_check         Check documentation style and consistency"
    echo "  sync_check          Check documentation synchronization"
    echo ""
    echo "Examples:"
    echo "  $0                                    # Run all enabled tasks"
    echo "  $0 --tasks audit,link_validation      # Run specific tasks"
    echo "  $0 --force-all                       # Run all tasks"
    echo "  $0 --check-deps                      # Check dependencies"
    echo ""
}

# Check dependencies
check_dependencies() {
    echo -e "${BLUE}Checking dependencies...${NC}"

    local missing_deps=()

    # Check Python 3
    if ! command -v python3 &> /dev/null; then
        missing_deps+=("python3")
    fi

    # Check pip
    if ! command -v pip3 &> /dev/null && ! command -v pip &> /dev/null; then
        missing_deps+=("pip")
    fi

    # Check Python packages
    local python_packages=("aiohttp" "pyspellchecker")
    for package in "${python_packages[@]}"; do
        if ! python3 -c "import $package" &> /dev/null; then
            missing_deps+=("python3-$package")
        fi
    done

    # Check git (optional)
    if ! command -v git &> /dev/null; then
        echo -e "${YELLOW}Warning: git not found. Synchronization features will be limited.${NC}"
    fi

    if [ ${#missing_deps[@]} -eq 0 ]; then
        echo -e "${GREEN}✓ All dependencies are satisfied${NC}"
        return 0
    else
        echo -e "${RED}✗ Missing dependencies:${NC}"
        for dep in "${missing_deps[@]}"; do
            echo "  • $dep"
        done
        echo ""
        echo "To install missing Python packages:"
        echo "  pip3 install aiohttp pyspellchecker"
        echo ""
        return 1
    fi
}

# Install dependencies
install_dependencies() {
    echo -e "${BLUE}Installing Python dependencies...${NC}"

    pip3 install aiohttp pyspellchecker

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Dependencies installed successfully${NC}"
    else
        echo -e "${RED}✗ Failed to install dependencies${NC}"
        exit 1
    fi
}

# Setup maintenance system
setup_maintenance() {
    echo -e "${BLUE}Setting up documentation maintenance system...${NC}"

    # Create directories
    mkdir -p "$TOOLS_DIR/reports"
    mkdir -p "$PROJECT_ROOT/.maintenance"

    # Create configuration file if it doesn't exist
    local config_file="$TOOLS_DIR/maintenance_config.json"
    if [ ! -f "$config_file" ]; then
        echo "Creating default configuration..."
        cat > "$config_file" << 'EOF'
{
  "version": "1.0",
  "last_updated": "2025-01-15T00:00:00",
  "tasks": [
    {
      "name": "audit",
      "description": "Comprehensive documentation audit",
      "script": "docs_auditor.py",
      "enabled": true,
      "frequency": "weekly",
      "dependencies": [],
      "timeout": 300,
      "critical": true
    },
    {
      "name": "link_validation",
      "description": "Validate all internal and external links",
      "script": "link_validator.py",
      "enabled": true,
      "frequency": "daily",
      "dependencies": [],
      "timeout": 600,
      "critical": false
    },
    {
      "name": "style_check",
      "description": "Check documentation style and consistency",
      "script": "style_checker.py",
      "enabled": true,
      "frequency": "weekly",
      "dependencies": [],
      "timeout": 180,
      "critical": false
    },
    {
      "name": "sync_check",
      "description": "Check documentation synchronization",
      "script": "sync_manager.py",
      "enabled": true,
      "frequency": "daily",
      "dependencies": [],
      "timeout": 120,
      "critical": false
    }
  ]
}
EOF
    fi

    # Make scripts executable
    chmod +x "$TOOLS_DIR"/*.py

    # Create cron job example
    cat > "$PROJECT_ROOT/.maintenance/cron_example.txt" << EOF
# Example cron jobs for documentation maintenance
# Add these to your crontab (crontab -e)

# Daily maintenance at 2 AM
0 2 * * * cd "$TOOLS_DIR" && ./run_maintenance.sh --quiet

# Weekly comprehensive audit on Sundays at 3 AM
0 3 * * 0 cd "$TOOLS_DIR" && ./run_maintenance.sh --force-all --quiet

# Quick check before work hours
30 8 * * 1-5 cd "$TOOLS_DIR" && ./run_maintenance.sh --tasks link_validation --quiet
EOF

    echo -e "${GREEN}✓ Maintenance system setup complete${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Review configuration: $config_file"
    echo "2. Consider adding cron jobs: $PROJECT_ROOT/.maintenance/cron_example.txt"
    echo "3. Run initial maintenance: $0"
}

# Run maintenance
run_maintenance() {
    echo -e "${BLUE}Starting documentation maintenance...${NC}"
    echo "Project root: $PROJECT_ROOT"
    echo "Tools directory: $TOOLS_DIR"
    echo ""

    # Change to tools directory
    cd "$TOOLS_DIR"

    # Build command
    local cmd="python3 maintenance_orchestrator.py '$PROJECT_ROOT'"

    if [ "$FORCE_ALL" = true ]; then
        cmd="$cmd --force-all"
    fi

    if [ -n "$SPECIFIC_TASKS" ]; then
        # Convert comma-separated to space-separated
        local tasks=$(echo "$SPECIFIC_TASKS" | tr ',' ' ')
        cmd="$cmd --tasks $tasks"
    fi

    # Execute maintenance
    if [ "$QUIET" = true ]; then
        eval "$cmd" > /dev/null 2>&1
        local exit_code=$?
        if [ $exit_code -eq 0 ]; then
            echo -e "${GREEN}✓ Maintenance completed successfully${NC}"
        else
            echo -e "${RED}✗ Maintenance failed (exit code: $exit_code)${NC}"
        fi
    else
        eval "$cmd"
    fi

    # Show latest reports
    if [ "$QUIET" != true ]; then
        echo ""
        echo -e "${BLUE}Latest reports:${NC}"
        find "$TOOLS_DIR/reports" -name "*.json" -type f -printf '%T@ %p\n' | sort -n | tail -5 | while read timestamp file; do
            echo "  • $(basename "$file")"
        done
    fi
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -p|--project)
            PROJECT_ROOT="$2"
            shift 2
            ;;
        -t|--tasks)
            SPECIFIC_TASKS="$2"
            shift 2
            ;;
        -f|--force-all)
            FORCE_ALL=true
            shift
            ;;
        -q|--quiet)
            QUIET=true
            shift
            ;;
        -c|--check-deps)
            check_dependencies
            exit $?
            ;;
        --install-deps)
            install_dependencies
            exit $?
            ;;
        -s|--setup)
            setup_maintenance
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Validate project root
if [ ! -d "$PROJECT_ROOT" ]; then
    echo -e "${RED}Error: Project root directory not found: $PROJECT_ROOT${NC}"
    exit 1
fi

# Update tools directory based on project root
TOOLS_DIR="$PROJECT_ROOT/tools/docs-maintenance"

# Check if tools directory exists
if [ ! -d "$TOOLS_DIR" ]; then
    echo -e "${RED}Error: Tools directory not found: $TOOLS_DIR${NC}"
    echo "Run: $0 --setup"
    exit 1
fi

# Check dependencies
if ! check_dependencies; then
    echo ""
    read -p "Install missing dependencies now? [Y/n] " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]] || [[ -z $REPLY ]]; then
        install_dependencies
    else
        echo -e "${YELLOW}Skipping dependency installation. Some features may not work.${NC}"
    fi
fi

# Run maintenance
run_maintenance