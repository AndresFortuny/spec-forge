#!/bin/bash
# spec-forge — Verification Script
# Run this before starting work to ensure everything is in place.

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

ERRORS=0
WARNINGS=0

echo "========================================="
echo "  spec-forge — Verification"
echo "========================================="
echo ""

# --- Check required files ---
check_file() {
    if [ -f "$1" ]; then
        echo -e "  ${GREEN}✓${NC} $1"
    else
        echo -e "  ${RED}✗${NC} $1 — MISSING"
        ERRORS=$((ERRORS + 1))
    fi
}

check_dir() {
    if [ -d "$1" ]; then
        echo -e "  ${GREEN}✓${NC} $1/"
    else
        echo -e "  ${RED}✗${NC} $1/ — MISSING"
        ERRORS=$((ERRORS + 1))
    fi
}

echo "Core files:"
check_file "AGENTS.md"
check_file "CHECKPOINTS.md"
check_file "feature_list.json"
check_file "init.sh"
echo ""

echo "Agent definitions:"
check_dir ".claude/agents"
check_file ".claude/agents/leader.md"
check_file ".claude/agents/business_analyst.md"
check_file ".claude/agents/product_owner.md"
check_file ".claude/agents/tech_architect.md"
check_file ".claude/agents/qa_lead.md"
check_file ".claude/agents/ux_designer.md"
check_file ".claude/agents/security_analyst.md"
echo ""

echo "Documentation:"
check_dir "docs"
check_file "docs/process.md"
check_file "docs/ears.md"
check_file "docs/stakeholder-map.md"
check_file "docs/quality-gates.md"
echo ""

echo "State directories:"
check_dir "specs"
check_dir "progress"
check_dir "memory"
check_file "memory/decisions.md"
check_file "memory/stakeholders.md"
check_file "memory/patterns.md"
check_file "memory/context.md"
echo ""

# --- Validate feature_list.json ---
echo "Validating feature_list.json..."
if command -v python3 &> /dev/null; then
    if python3 -c "import json; json.load(open('feature_list.json'))" 2>/dev/null; then
        echo -e "  ${GREEN}✓${NC} Valid JSON"
    else
        echo -e "  ${RED}✗${NC} Invalid JSON"
        ERRORS=$((ERRORS + 1))
    fi
elif command -v node &> /dev/null; then
    if node -e "JSON.parse(require('fs').readFileSync('feature_list.json','utf8'))" 2>/dev/null; then
        echo -e "  ${GREEN}✓${NC} Valid JSON"
    else
        echo -e "  ${RED}✗${NC} Invalid JSON"
        ERRORS=$((ERRORS + 1))
    fi
else
    echo -e "  ${YELLOW}⚠${NC} Cannot validate JSON (no python3 or node found)"
    WARNINGS=$((WARNINGS + 1))
fi
echo ""

# --- Check for in_progress features ---
echo "Checking feature states..."
if command -v python3 &> /dev/null; then
    ANALYZING=$(python3 -c "
import json
data = json.load(open('feature_list.json'))
count = sum(1 for f in data['features'] if f['status'] == 'analyzing')
print(count)
" 2>/dev/null || echo "0")
    if [ "$ANALYZING" -gt 1 ]; then
        echo -e "  ${RED}✗${NC} Multiple features in 'analyzing' state ($ANALYZING found — only 1 allowed)"
        ERRORS=$((ERRORS + 1))
    else
        echo -e "  ${GREEN}✓${NC} Feature state check passed"
    fi
else
    echo -e "  ${YELLOW}⚠${NC} Cannot check feature states (no python3)"
    WARNINGS=$((WARNINGS + 1))
fi
echo ""

# --- Summary ---
echo "========================================="
if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "  ${GREEN}ALL CHECKS PASSED${NC}"
    echo "  Ready to start spec-forge."
elif [ $ERRORS -eq 0 ]; then
    echo -e "  ${YELLOW}PASSED WITH $WARNINGS WARNING(S)${NC}"
    echo "  You can proceed, but check the warnings above."
else
    echo -e "  ${RED}$ERRORS ERROR(S), $WARNINGS WARNING(S)${NC}"
    echo "  Fix the errors above before proceeding."
    exit 1
fi
echo "========================================="
