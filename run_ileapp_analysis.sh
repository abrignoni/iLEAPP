#!/bin/bash

# iLEAPP Automated Analysis Script for macOS
# This script runs forensic analysis on an iOS backup

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "================================================"
echo "iLEAPP iOS Forensic Analysis - Automated Script"
echo "================================================"
echo ""

# Configuration
ILEAPP_DIR="/Applications/GitHub/iLEAPP/Forensics/iLEAPP"
BACKUP_PATH="/Users/macbook/Desktop/library/Application Support/MobileSync/Backup/00008110-0001306901C0A01E"
OUTPUT_DIR="/Users/macbook/MVT-IOS/iLEAPP_Results_$(date +%Y%m%d_%H%M%S)"
MVT_DIR="/Users/macbook/MVT-IOS"

# Check if iLEAPP directory exists
if [ ! -d "$ILEAPP_DIR" ]; then
    echo -e "${RED}Error: iLEAPP directory not found at $ILEAPP_DIR${NC}"
    echo "Please update the ILEAPP_DIR variable in this script to point to the correct location."
    exit 1
fi

# Check if backup path exists
if [ ! -d "$BACKUP_PATH" ]; then
    echo -e "${RED}Error: iOS backup not found at $BACKUP_PATH${NC}"
    echo "Please verify the backup path and update the BACKUP_PATH variable if needed."
    exit 1
fi

# Check if MVT output directory exists, create if not
if [ ! -d "$MVT_DIR" ]; then
    echo -e "${YELLOW}Creating output directory: $MVT_DIR${NC}"
    mkdir -p "$MVT_DIR"
fi

# Create output directory for this run
echo -e "${GREEN}Creating output directory: $OUTPUT_DIR${NC}"
mkdir -p "$OUTPUT_DIR"

# Check for Python 3
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: python3 not found. Please install Python 3.10-3.12${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo -e "${GREEN}Found Python version: $PYTHON_VERSION${NC}"

# Check if requirements are installed
echo ""
echo "Checking dependencies..."
cd "$ILEAPP_DIR" || exit 1

if ! python3 -c "import pytz" 2>/dev/null; then
    echo -e "${YELLOW}Dependencies not installed. Installing required packages...${NC}"
    echo "This may take a few minutes..."
    python3 -m pip install -r requirements.txt

    if [ $? -ne 0 ]; then
        echo -e "${RED}Error: Failed to install dependencies${NC}"
        echo "Please run manually: cd $ILEAPP_DIR && python3 -m pip install -r requirements.txt"
        exit 1
    fi
    echo -e "${GREEN}Dependencies installed successfully${NC}"
else
    echo -e "${GREEN}Dependencies already installed${NC}"
fi

# Run iLEAPP analysis
echo ""
echo "================================================"
echo "Starting iLEAPP Analysis"
echo "================================================"
echo "Backup Path: $BACKUP_PATH"
echo "Output Path: $OUTPUT_DIR"
echo ""
echo "This may take several minutes depending on the backup size..."
echo ""

python3 "$ILEAPP_DIR/ileapp.py" \
    -t fs \
    -i "$BACKUP_PATH" \
    -o "$OUTPUT_DIR"

if [ $? -eq 0 ]; then
    echo ""
    echo "================================================"
    echo -e "${GREEN}Analysis completed successfully!${NC}"
    echo "================================================"
    echo ""
    echo "Results saved to: $OUTPUT_DIR"
    echo ""
    echo "To view the report, open:"
    echo "  $OUTPUT_DIR/index.html"
    echo ""

    # Attempt to open the report automatically
    if [ -f "$OUTPUT_DIR/index.html" ]; then
        echo "Opening report in browser..."
        open "$OUTPUT_DIR/index.html"
    fi
else
    echo ""
    echo -e "${RED}Analysis failed. Please check the error messages above.${NC}"
    exit 1
fi
