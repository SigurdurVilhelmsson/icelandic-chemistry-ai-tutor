#!/bin/bash

# ============================================================================
# Run All Tests - Icelandic Chemistry AI Tutor
# ============================================================================
#
# This script runs the complete test suite including:
# - Backend unit tests
# - Backend integration tests
# - E2E tests (mocked)
# - Code coverage reporting
#
# Usage:
#   ./scripts/run_all_tests.sh [options]
#
# Options:
#   --fast          Skip slow tests
#   --coverage      Generate coverage report
#   --verbose       Verbose output
#   --parallel      Run tests in parallel
#   --markers       Run specific test markers (e.g., --markers unit)
#
# ============================================================================

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default options
FAST_MODE=false
COVERAGE_MODE=false
VERBOSE_MODE=false
PARALLEL_MODE=false
TEST_MARKERS=""

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --fast)
            FAST_MODE=true
            shift
            ;;
        --coverage)
            COVERAGE_MODE=true
            shift
            ;;
        --verbose)
            VERBOSE_MODE=true
            shift
            ;;
        --parallel)
            PARALLEL_MODE=true
            shift
            ;;
        --markers)
            TEST_MARKERS="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Print header
echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║     Icelandic Chemistry AI Tutor - Test Suite Runner      ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Track overall success
ALL_TESTS_PASSED=true

# ============================================================================
# Backend Tests
# ============================================================================

echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}Running Backend Tests...${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

cd backend

# Build pytest command
PYTEST_CMD="pytest tests/"

# Add options
if [ "$VERBOSE_MODE" = true ]; then
    PYTEST_CMD="$PYTEST_CMD -v"
else
    PYTEST_CMD="$PYTEST_CMD -q"
fi

if [ "$FAST_MODE" = true ]; then
    PYTEST_CMD="$PYTEST_CMD -m 'not slow'"
fi

if [ "$PARALLEL_MODE" = true ]; then
    PYTEST_CMD="$PYTEST_CMD -n auto"
fi

if [ -n "$TEST_MARKERS" ]; then
    PYTEST_CMD="$PYTEST_CMD -m $TEST_MARKERS"
fi

if [ "$COVERAGE_MODE" = true ]; then
    PYTEST_CMD="$PYTEST_CMD --cov=src --cov-report=html --cov-report=term-missing"
fi

# Run backend tests
echo "Command: $PYTEST_CMD"
echo ""

if $PYTEST_CMD; then
    echo -e "${GREEN}✓ Backend tests passed${NC}"
else
    echo -e "${RED}✗ Backend tests failed${NC}"
    ALL_TESTS_PASSED=false
fi

echo ""

cd ..

# ============================================================================
# E2E Tests
# ============================================================================

if [ "$FAST_MODE" = false ]; then
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${YELLOW}Running E2E Tests...${NC}"
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""

    E2E_CMD="pytest tests/e2e/"

    if [ "$VERBOSE_MODE" = true ]; then
        E2E_CMD="$E2E_CMD -v"
    else
        E2E_CMD="$E2E_CMD -q"
    fi

    # Skip tests that require running server
    E2E_CMD="$E2E_CMD -m 'e2e and not skip'"

    echo "Command: $E2E_CMD"
    echo ""

    if $E2E_CMD; then
        echo -e "${GREEN}✓ E2E tests passed${NC}"
    else
        echo -e "${RED}✗ E2E tests failed${NC}"
        ALL_TESTS_PASSED=false
    fi

    echo ""
fi

# ============================================================================
# Summary
# ============================================================================

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}Test Summary${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

if [ "$COVERAGE_MODE" = true ]; then
    echo -e "${BLUE}Coverage report generated at: backend/htmlcov/index.html${NC}"
    echo ""
fi

if [ "$ALL_TESTS_PASSED" = true ]; then
    echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║                 ✓ ALL TESTS PASSED ✓                       ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
    exit 0
else
    echo -e "${RED}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${RED}║                 ✗ SOME TESTS FAILED ✗                      ║${NC}"
    echo -e "${RED}╚════════════════════════════════════════════════════════════╝${NC}"
    exit 1
fi
