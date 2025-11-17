#!/bin/bash
# Quick Test Setup for Icelandic Chemistry AI Tutor
# Generates sample content and sets up the system for testing

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  Icelandic Chemistry AI Tutor - Quick Test Setup          ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check for ANTHROPIC_API_KEY
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo -e "${YELLOW}⚠️  ANTHROPIC_API_KEY not set${NC}"
    echo -e "${YELLOW}   Content will be generated using templates only${NC}"
    echo -e "${YELLOW}   Set ANTHROPIC_API_KEY for AI-generated content${NC}"
    echo ""
    NO_API="--no-api"
else
    echo -e "${GREEN}✅ ANTHROPIC_API_KEY found${NC}"
    NO_API=""
fi

# Default values
DOC_COUNT=${1:-50}
CHAPTERS=${2:-"1,2,3,4,5"}

echo -e "${BLUE}Configuration:${NC}"
echo -e "  Documents: ${GREEN}${DOC_COUNT}${NC}"
echo -e "  Chapters: ${GREEN}${CHAPTERS}${NC}"
echo ""

# Step 1: Generate sample content
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}Step 1: Generating Sample Content${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

cd "$PROJECT_ROOT"

python3 tools/content_generator.py \
    --count "$DOC_COUNT" \
    --chapters "$CHAPTERS" \
    --output tools/generated \
    $NO_API

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Content generation failed${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}✅ Content generation complete${NC}"
echo ""

# Step 2: Ingest content (optional, requires backend setup)
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}Step 2: Ingesting Content (Optional)${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

if [ -f "$PROJECT_ROOT/backend/src/ingest.py" ]; then
    read -p "$(echo -e ${YELLOW}Do you want to ingest the generated content? [y/N]: ${NC})" -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        cd "$PROJECT_ROOT/backend"

        # Check if virtual environment exists
        if [ -d "venv" ]; then
            source venv/bin/activate
        fi

        python src/batch_ingest.py --input ../tools/generated/ --batch-size 10

        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✅ Content ingestion complete${NC}"
        else
            echo -e "${RED}❌ Content ingestion failed${NC}"
        fi
    else
        echo -e "${YELLOW}⏭️  Skipping ingestion${NC}"
        echo -e "   You can run it later with:"
        echo -e "   ${BLUE}cd backend && python src/batch_ingest.py --input ../tools/generated/${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  Ingest script not found${NC}"
    echo -e "   Skipping ingestion step"
fi

echo ""

# Step 3: Summary and next steps
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✅ Quick Test Setup Complete!${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${BLUE}📁 Generated Content Location:${NC}"
echo -e "   $PROJECT_ROOT/tools/generated/"
echo ""
echo -e "${BLUE}🚀 Next Steps:${NC}"
echo ""
echo -e "1. Review generated content:"
echo -e "   ${GREEN}ls -la tools/generated/${NC}"
echo ""
echo -e "2. Start the backend (in a new terminal):"
echo -e "   ${GREEN}cd backend${NC}"
echo -e "   ${GREEN}uvicorn src.main:app --reload${NC}"
echo ""
echo -e "3. Start the frontend (in another terminal):"
echo -e "   ${GREEN}npm run dev${NC}"
echo ""
echo -e "4. Test with Icelandic queries:"
echo -e "   ${GREEN}curl -X POST http://localhost:8000/api/chat \\${NC}"
echo -e "   ${GREEN}  -H 'Content-Type: application/json' \\${NC}"
echo -e "   ${GREEN}  -d '{\"question\": \"Hvað er atóm?\",\"language\": \"is\"}'${NC}"
echo ""
echo -e "5. Run backend tests:"
echo -e "   ${GREEN}cd backend && pytest tests/${NC}"
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
