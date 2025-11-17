#!/bin/bash

###############################################################################
# Development Server Launcher
###############################################################################
#
# Start the backend with debugging enabled and optionally launch dev tools.
#
# Usage:
#   ./dev-tools/scripts/dev_server.sh [options]
#
# Options:
#   --backend-only    Start only the backend (no dev tools)
#   --with-inspector  Also start the database inspector
#   --with-profiler   Also start the performance profiler
#   --port PORT       Backend port (default: 8000)
#   --help            Show this help message
#
# Examples:
#   ./dev-tools/scripts/dev_server.sh
#   ./dev-tools/scripts/dev_server.sh --with-inspector
#   ./dev-tools/scripts/dev_server.sh --port 8080
#
###############################################################################

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
BACKEND_ONLY=false
WITH_INSPECTOR=false
WITH_PROFILER=false
BACKEND_PORT=8000

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --backend-only)
            BACKEND_ONLY=true
            shift
            ;;
        --with-inspector)
            WITH_INSPECTOR=true
            shift
            ;;
        --with-profiler)
            WITH_PROFILER=true
            shift
            ;;
        --port)
            BACKEND_PORT="$2"
            shift 2
            ;;
        --help)
            head -n 25 "$0" | tail -n 20
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Get project root directory
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
BACKEND_DIR="$PROJECT_ROOT/backend"
DEV_TOOLS_DIR="$PROJECT_ROOT/dev-tools"

# Check if backend directory exists
if [ ! -d "$BACKEND_DIR" ]; then
    echo -e "${RED}Error: Backend directory not found at $BACKEND_DIR${NC}"
    exit 1
fi

# Print banner
echo ""
echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║${NC}  ${GREEN}Icelandic Chemistry AI - Development Server${NC}               ${BLUE}║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Function to check if a port is available
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 1
    else
        return 0
    fi
}

# Function to kill background processes on exit
cleanup() {
    echo ""
    echo -e "${YELLOW}Shutting down...${NC}"

    # Kill all background jobs
    jobs -p | xargs -r kill 2>/dev/null

    echo -e "${GREEN}Done!${NC}"
    exit 0
}

trap cleanup SIGINT SIGTERM EXIT

# Check if backend port is available
if ! check_port $BACKEND_PORT; then
    echo -e "${RED}Error: Port $BACKEND_PORT is already in use${NC}"
    echo "Please stop the existing process or use a different port with --port"
    exit 1
fi

# Check if inspector port is available (if needed)
if [ "$WITH_INSPECTOR" = true ]; then
    if ! check_port 5001; then
        echo -e "${RED}Error: Port 5001 (Database Inspector) is already in use${NC}"
        exit 1
    fi
fi

# Set development environment variables
export DEBUG=true
export LOG_LEVEL=DEBUG
export PYTHONUNBUFFERED=1

# Check for .env file
if [ -f "$BACKEND_DIR/.env" ]; then
    echo -e "${GREEN}✓${NC} Found .env file"
    export $(cat "$BACKEND_DIR/.env" | grep -v '^#' | xargs)
else
    echo -e "${YELLOW}⚠${NC} No .env file found. Make sure API keys are set in environment."
fi

# Check if virtual environment exists
if [ -d "$BACKEND_DIR/venv" ]; then
    echo -e "${GREEN}✓${NC} Activating virtual environment"
    source "$BACKEND_DIR/venv/bin/activate"
elif [ -d "$BACKEND_DIR/.venv" ]; then
    echo -e "${GREEN}✓${NC} Activating virtual environment"
    source "$BACKEND_DIR/.venv/bin/activate"
else
    echo -e "${YELLOW}⚠${NC} No virtual environment found. Using system Python."
fi

# Check if required packages are installed
echo -e "${BLUE}→${NC} Checking dependencies..."
if ! python -c "import fastapi, anthropic, chromadb" 2>/dev/null; then
    echo -e "${YELLOW}⚠${NC} Some dependencies are missing. Installing..."
    pip install -q -r "$BACKEND_DIR/requirements.txt"
fi
echo -e "${GREEN}✓${NC} Dependencies OK"

echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}Starting Services...${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
echo ""

# Start backend server
echo -e "${GREEN}→${NC} Starting backend server on port $BACKEND_PORT..."
cd "$BACKEND_DIR"
uvicorn src.main:app --reload --log-level debug --port $BACKEND_PORT --host 0.0.0.0 &
BACKEND_PID=$!

# Wait for backend to start
sleep 3

if ps -p $BACKEND_PID > /dev/null; then
    echo -e "${GREEN}✓${NC} Backend running (PID: $BACKEND_PID)"
    echo -e "  ${BLUE}→${NC} API: http://localhost:$BACKEND_PORT"
    echo -e "  ${BLUE}→${NC} Docs: http://localhost:$BACKEND_PORT/docs"
else
    echo -e "${RED}✗${NC} Backend failed to start"
    exit 1
fi

# Start database inspector if requested
if [ "$WITH_INSPECTOR" = true ]; then
    echo ""
    echo -e "${GREEN}→${NC} Starting database inspector on port 5001..."
    python "$DEV_TOOLS_DIR/backend/db_inspector.py" &
    INSPECTOR_PID=$!

    sleep 2

    if ps -p $INSPECTOR_PID > /dev/null; then
        echo -e "${GREEN}✓${NC} Database Inspector running (PID: $INSPECTOR_PID)"
        echo -e "  ${BLUE}→${NC} Inspector: http://localhost:5001"
    else
        echo -e "${RED}✗${NC} Database Inspector failed to start"
    fi
fi

# Show available dev tools
if [ "$BACKEND_ONLY" = false ]; then
    echo ""
    echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}Available Dev Tools${NC}"
    echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
    echo ""
    echo -e "${YELLOW}RAG Debugger:${NC}"
    echo "  python dev-tools/backend/rag_debugger.py"
    echo ""
    echo -e "${YELLOW}Search Visualizer:${NC}"
    echo "  python dev-tools/backend/search_visualizer.py"
    echo ""
    echo -e "${YELLOW}Token Tracker:${NC}"
    echo "  python dev-tools/backend/token_tracker.py --summary"
    echo ""
    echo -e "${YELLOW}Performance Profiler:${NC}"
    echo "  python dev-tools/backend/performance_profiler.py"
    echo ""

    if [ "$WITH_INSPECTOR" = false ]; then
        echo -e "${YELLOW}Database Inspector:${NC}"
        echo "  python dev-tools/backend/db_inspector.py"
        echo "  (or restart with --with-inspector)"
        echo ""
    fi
fi

# Show status
echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}Server Status${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${GREEN}✓${NC} All services running"
echo -e "${YELLOW}Press Ctrl+C to stop all services${NC}"
echo ""

# Keep script running
wait
