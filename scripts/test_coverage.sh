#!/bin/bash

# ============================================================================
# Test Coverage Report Generator - Icelandic Chemistry AI Tutor
# ============================================================================
#
# This script generates comprehensive test coverage reports with the
# following outputs:
# - HTML coverage report
# - Terminal coverage summary
# - XML coverage report (for CI/CD)
# - JSON coverage report
# - Coverage badge data
#
# Usage:
#   ./scripts/test_coverage.sh [options]
#
# Options:
#   --threshold PERCENT    Fail if coverage below threshold (default: 80)
#   --open                 Open HTML report in browser after generation
#   --upload               Upload coverage to codecov (requires token)
#   --check                Only check coverage, don't fail on low coverage
#
# ============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Default options
COVERAGE_THRESHOLD=80
OPEN_REPORT=false
UPLOAD_COVERAGE=false
CHECK_ONLY=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --threshold)
            COVERAGE_THRESHOLD="$2"
            shift 2
            ;;
        --open)
            OPEN_REPORT=true
            shift
            ;;
        --upload)
            UPLOAD_COVERAGE=true
            shift
            ;;
        --check)
            CHECK_ONLY=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Print header
echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║          Test Coverage Report Generator                    ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# ============================================================================
# Run Tests with Coverage
# ============================================================================

echo -e "${YELLOW}Running tests with coverage tracking...${NC}"
echo ""

cd backend

# Run tests with coverage
pytest tests/ \
    --cov=src \
    --cov-report=html:htmlcov \
    --cov-report=term-missing \
    --cov-report=xml:coverage.xml \
    --cov-report=json:coverage.json \
    --cov-fail-under=$COVERAGE_THRESHOLD \
    -v

COVERAGE_EXIT_CODE=$?

cd ..

# ============================================================================
# Generate Coverage Summary
# ============================================================================

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}Coverage Summary${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Extract coverage percentage from JSON report
if [ -f "backend/coverage.json" ]; then
    COVERAGE_PERCENT=$(python3 -c "
import json
with open('backend/coverage.json') as f:
    data = json.load(f)
    print(f\"{data['totals']['percent_covered']:.2f}\")
")

    echo -e "${BLUE}Total Coverage: ${GREEN}${COVERAGE_PERCENT}%${NC}"
    echo -e "${BLUE}Coverage Threshold: ${YELLOW}${COVERAGE_THRESHOLD}%${NC}"
    echo ""

    # Check if coverage meets threshold
    if (( $(echo "$COVERAGE_PERCENT >= $COVERAGE_THRESHOLD" | bc -l) )); then
        echo -e "${GREEN}✓ Coverage meets threshold${NC}"
        THRESHOLD_MET=true
    else
        echo -e "${RED}✗ Coverage below threshold${NC}"
        THRESHOLD_MET=false
    fi
else
    echo -e "${YELLOW}⚠ Coverage data not found${NC}"
    THRESHOLD_MET=false
fi

echo ""

# ============================================================================
# Report Locations
# ============================================================================

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}Generated Reports${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

echo -e "${GREEN}HTML Report:${NC}    backend/htmlcov/index.html"
echo -e "${GREEN}XML Report:${NC}     backend/coverage.xml"
echo -e "${GREEN}JSON Report:${NC}    backend/coverage.json"
echo ""

# ============================================================================
# Open HTML Report
# ============================================================================

if [ "$OPEN_REPORT" = true ]; then
    echo -e "${YELLOW}Opening HTML coverage report...${NC}"

    # Detect OS and open browser
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        open backend/htmlcov/index.html
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        if command -v xdg-open &> /dev/null; then
            xdg-open backend/htmlcov/index.html
        else
            echo -e "${YELLOW}Could not open browser. Please open backend/htmlcov/index.html manually.${NC}"
        fi
    else
        echo -e "${YELLOW}OS not recognized. Please open backend/htmlcov/index.html manually.${NC}"
    fi

    echo ""
fi

# ============================================================================
# Upload to Codecov
# ============================================================================

if [ "$UPLOAD_COVERAGE" = true ]; then
    echo -e "${YELLOW}Uploading coverage to Codecov...${NC}"

    if [ -z "$CODECOV_TOKEN" ]; then
        echo -e "${RED}✗ CODECOV_TOKEN environment variable not set${NC}"
    else
        if command -v codecov &> /dev/null; then
            codecov -f backend/coverage.xml -t "$CODECOV_TOKEN"
            echo -e "${GREEN}✓ Coverage uploaded${NC}"
        else
            echo -e "${RED}✗ codecov CLI not installed${NC}"
            echo -e "${YELLOW}Install with: pip install codecov${NC}"
        fi
    fi

    echo ""
fi

# ============================================================================
# Coverage Badge
# ============================================================================

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}Coverage Badge${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

if [ -f "backend/coverage.json" ]; then
    # Determine badge color
    if (( $(echo "$COVERAGE_PERCENT >= 90" | bc -l) )); then
        BADGE_COLOR="brightgreen"
    elif (( $(echo "$COVERAGE_PERCENT >= 80" | bc -l) )); then
        BADGE_COLOR="green"
    elif (( $(echo "$COVERAGE_PERCENT >= 70" | bc -l) )); then
        BADGE_COLOR="yellowgreen"
    elif (( $(echo "$COVERAGE_PERCENT >= 60" | bc -l) )); then
        BADGE_COLOR="yellow"
    else
        BADGE_COLOR="red"
    fi

    echo -e "${GREEN}Badge URL:${NC}"
    echo "https://img.shields.io/badge/coverage-${COVERAGE_PERCENT}%25-${BADGE_COLOR}"
    echo ""
fi

# ============================================================================
# Detailed Module Coverage
# ============================================================================

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}Module Coverage Breakdown${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

if [ -f "backend/coverage.json" ]; then
    python3 << 'EOF'
import json
from pathlib import Path

with open('backend/coverage.json') as f:
    data = json.load(f)

print(f"{'Module':<40} {'Coverage':<10} {'Missing Lines':<15}")
print("-" * 70)

# Sort by coverage percentage
files = sorted(
    data['files'].items(),
    key=lambda x: x[1]['summary']['percent_covered'],
    reverse=True
)

for filepath, file_data in files:
    # Get relative path
    rel_path = Path(filepath).name

    # Get coverage stats
    summary = file_data['summary']
    coverage = summary['percent_covered']
    missing = summary['missing_lines']

    # Color code based on coverage
    if coverage >= 90:
        color = '\033[0;32m'  # Green
    elif coverage >= 80:
        color = '\033[1;33m'  # Yellow
    else:
        color = '\033[0;31m'  # Red

    reset = '\033[0m'

    print(f"{rel_path:<40} {color}{coverage:>6.2f}%{reset}    {missing:>5} lines")
EOF
else
    echo -e "${YELLOW}Coverage data not available${NC}"
fi

echo ""

# ============================================================================
# Exit Status
# ============================================================================

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}Final Result${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

if [ "$CHECK_ONLY" = true ]; then
    # Just checking, don't fail
    if [ "$THRESHOLD_MET" = true ]; then
        echo -e "${GREEN}✓ Coverage check passed${NC}"
    else
        echo -e "${YELLOW}⚠ Coverage below threshold (check only)${NC}"
    fi
    exit 0
else
    # Fail if threshold not met
    if [ "$THRESHOLD_MET" = true ] && [ "$COVERAGE_EXIT_CODE" -eq 0 ]; then
        echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
        echo -e "${GREEN}║              ✓ COVERAGE REQUIREMENTS MET ✓                 ║${NC}"
        echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
        exit 0
    else
        echo -e "${RED}╔════════════════════════════════════════════════════════════╗${NC}"
        echo -e "${RED}║             ✗ COVERAGE REQUIREMENTS NOT MET ✗              ║${NC}"
        echo -e "${RED}╚════════════════════════════════════════════════════════════╝${NC}"
        exit 1
    fi
fi
