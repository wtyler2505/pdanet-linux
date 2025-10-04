#!/bin/bash
#
# validate-hooks.sh - Validate and install Claude Code hook dependencies
#
# This script checks if all required development tools for Claude Code hooks
# are installed and offers to install them if missing.

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}PdaNet Linux - Hook Dependencies Validator${NC}"
echo "================================================"
echo ""

# Required tools for hooks
REQUIRED_TOOLS=(
    "black"
    "isort"
    "flake8"
    "mypy"
    "pytest"
    "pytest-cov"
)

MISSING_TOOLS=()

echo -e "${YELLOW}Checking hook dependencies...${NC}"
echo ""

# Check each tool
for tool in "${REQUIRED_TOOLS[@]}"; do
    if pip show "$tool" &>/dev/null; then
        VERSION=$(pip show "$tool" | grep Version | awk '{print $2}')
        echo -e "  ✓ ${GREEN}$tool${NC} (v$VERSION)"
    else
        echo -e "  ✗ ${RED}$tool${NC} - NOT INSTALLED"
        MISSING_TOOLS+=("$tool")
    fi
done

echo ""

# Summary
if [ ${#MISSING_TOOLS[@]} -eq 0 ]; then
    echo -e "${GREEN}✓ All hook dependencies are installed!${NC}"
    echo ""
    echo "Hook system is ready:"
    echo "  • black     - Code formatting"
    echo "  • isort     - Import sorting"
    echo "  • flake8    - Linting (blocks on errors)"
    echo "  • mypy      - Type checking (blocks on errors)"
    echo "  • pytest    - Test runner"
    echo "  • pytest-cov - Coverage reporting"
    exit 0
else
    echo -e "${YELLOW}Missing ${#MISSING_TOOLS[@]} dependencies:${NC}"
    for tool in "${MISSING_TOOLS[@]}"; do
        echo "  • $tool"
    done
    echo ""

    # Offer to install
    read -p "Install missing dependencies now? [Y/n] " -n 1 -r
    echo ""

    if [[ $REPLY =~ ^[Yy]$ ]] || [[ -z $REPLY ]]; then
        echo ""
        echo -e "${BLUE}Installing dependencies from requirements.txt...${NC}"

        # Check if requirements.txt exists
        if [ ! -f "requirements.txt" ]; then
            echo -e "${RED}Error: requirements.txt not found${NC}"
            exit 1
        fi

        # Install with --break-system-packages flag (for system Python)
        pip install --break-system-packages -r requirements.txt

        echo ""
        echo -e "${GREEN}✓ Dependencies installed successfully!${NC}"
        echo ""
        echo "Hook system is now ready. The following hooks will run automatically:"
        echo ""
        echo "PreToolUse hooks:"
        echo "  • print() detection - Warns if print() used instead of logging"
        echo "  • Dependency audit   - Checks for vulnerable dependencies"
        echo ""
        echo "PostToolUse hooks:"
        echo "  • black     - Auto-formats Python files"
        echo "  • isort     - Auto-sorts imports"
        echo "  • flake8    - Lints code (blocks on errors)"
        echo "  • mypy      - Type checks (blocks on errors)"
        echo "  • pytest    - Runs tests for modified modules"
        echo ""
        echo "Stop hooks:"
        echo "  • Final lint       - Runs flake8/pylint on all changed files"
        echo "  • Final type check - Runs mypy on all changed files"
    else
        echo ""
        echo -e "${YELLOW}Skipping installation.${NC}"
        echo ""
        echo "To install manually, run:"
        echo "  pip install --break-system-packages -r requirements.txt"
        exit 1
    fi
fi
