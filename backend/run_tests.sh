#!/bin/bash

#######################################################################
# Automated Test Script for Icelandic Chemistry AI Tutor
#
# This script:
# 1. Creates virtual environment
# 2. Installs dependencies
# 3. Runs content ingestion
# 4. Starts FastAPI server in background
# 5. Runs integration tests
# 6. Outputs results
# 7. Cleanup
#######################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print header
echo -e "${BLUE}======================================${NC}"
echo -e "${BLUE}Icelandic Chemistry AI Tutor${NC}"
echo -e "${BLUE}Automated Test Suite${NC}"
echo -e "${BLUE}======================================${NC}\n"

# Check Python version
echo -e "${YELLOW}Checking Python version...${NC}"
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo -e "Python version: ${python_version}\n"

# Step 1: Create virtual environment
echo -e "${YELLOW}Step 1: Setting up virtual environment...${NC}"
if [ -d "venv" ]; then
    echo "Virtual environment already exists, skipping creation"
else
    python3 -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
fi

# Activate virtual environment
source venv/bin/activate
echo -e "${GREEN}✓ Virtual environment activated${NC}\n"

# Step 2: Install dependencies
echo -e "${YELLOW}Step 2: Installing dependencies...${NC}"
pip install -q --upgrade pip
pip install -q -r requirements.txt
echo -e "${GREEN}✓ Dependencies installed${NC}\n"

# Step 3: Check environment variables
echo -e "${YELLOW}Step 3: Checking environment variables...${NC}"
if [ ! -f ".env" ]; then
    echo -e "${RED}✗ .env file not found!${NC}"
    echo "Please copy .env.example to .env and add your API keys:"
    echo "  cp .env.example .env"
    echo "  # Then edit .env with your keys"
    exit 1
fi

# Load environment variables
set -a
source .env
set +a

if [ -z "$ANTHROPIC_API_KEY" ] || [ "$ANTHROPIC_API_KEY" = "your_anthropic_api_key_here" ]; then
    echo -e "${RED}✗ ANTHROPIC_API_KEY not set in .env${NC}"
    exit 1
fi

if [ -z "$OPENAI_API_KEY" ] || [ "$OPENAI_API_KEY" = "your_openai_api_key_here" ]; then
    echo -e "${RED}✗ OPENAI_API_KEY not set in .env${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Environment variables configured${NC}\n"

# Step 4: Run ingestion
echo -e "${YELLOW}Step 4: Ingesting chemistry content...${NC}"
python -m src.ingest --data-dir ./data/sample --reset
echo -e "${GREEN}✓ Content ingested${NC}\n"

# Step 5: Verify database
echo -e "${YELLOW}Step 5: Verifying database...${NC}"
python -m src.inspect_db stats
echo ""

# Step 6: Start FastAPI server in background
echo -e "${YELLOW}Step 6: Starting FastAPI server...${NC}"
uvicorn src.main:app --host 0.0.0.0 --port 8000 --log-level warning > server.log 2>&1 &
SERVER_PID=$!
echo "Server PID: $SERVER_PID"

# Wait for server to start
echo "Waiting for server to start..."
sleep 5

# Check if server is running
if ps -p $SERVER_PID > /dev/null; then
    echo -e "${GREEN}✓ Server started successfully${NC}\n"
else
    echo -e "${RED}✗ Server failed to start${NC}"
    cat server.log
    exit 1
fi

# Step 7: Run tests
echo -e "${YELLOW}Step 7: Running integration tests...${NC}"
echo -e "${BLUE}======================================${NC}\n"

# Run the test suite
TEST_EXIT_CODE=0
python -m tests.test_rag || TEST_EXIT_CODE=$?

echo -e "\n${BLUE}======================================${NC}\n"

# Step 8: Check API endpoint
echo -e "${YELLOW}Step 8: Testing API endpoint...${NC}"
HEALTH_CHECK=$(curl -s http://localhost:8000/health || echo "failed")

if [[ $HEALTH_CHECK == *"ok"* ]] || [[ $HEALTH_CHECK == *"healthy"* ]]; then
    echo -e "${GREEN}✓ API health check passed${NC}"
    echo "Response: $HEALTH_CHECK"
else
    echo -e "${RED}✗ API health check failed${NC}"
    echo "Response: $HEALTH_CHECK"
    TEST_EXIT_CODE=1
fi
echo ""

# Step 9: Cleanup
echo -e "${YELLOW}Step 9: Cleaning up...${NC}"

# Stop server
if ps -p $SERVER_PID > /dev/null; then
    kill $SERVER_PID
    echo "Server stopped (PID: $SERVER_PID)"
fi

# Wait for server to stop
sleep 2

echo -e "${GREEN}✓ Cleanup complete${NC}\n"

# Final results
echo -e "${BLUE}======================================${NC}"
echo -e "${BLUE}TEST RESULTS${NC}"
echo -e "${BLUE}======================================${NC}"

if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}✓ ALL TESTS PASSED${NC}"
    echo -e "${GREEN}The Icelandic Chemistry AI Tutor is working correctly!${NC}"
else
    echo -e "${RED}✗ SOME TESTS FAILED${NC}"
    echo -e "${RED}Please check the output above for details${NC}"
fi

echo -e "${BLUE}======================================${NC}\n"

# Deactivate virtual environment
deactivate 2>/dev/null || true

# Exit with test result code
exit $TEST_EXIT_CODE
