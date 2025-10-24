#!/bin/bash

# ==============================================================================
# MOPA LASER COLOR REPRODUCTION - ONE-CLICK TEST RUNNER
# ==============================================================================
# This script makes it trivial to test the Retinex-enhanced color reproduction.
# Just run: ./RUN_TESTS.sh
#
# What it does:
#   1. Generates color test patterns (gradients, patches, etc.)
#   2. Processes them with BOTH the original and Retinex algorithms
#   3. Creates side-by-side comparison images
#   4. Generates a summary report
#
# Options:
#   --clean    Remove all generated test files and directories
#   --help     Show this help message
#
# No configuration needed - just run and review the results!
# ==============================================================================

set -e  # Exit on error

# Handle command line arguments
if [ "$1" = "--clean" ]; then
    echo "════════════════════════════════════════════════════════════════════"
    echo "  CLEANING UP TEST OUTPUTS"
    echo "════════════════════════════════════════════════════════════════════"
    echo ""

    # Remove all generated test directories
    if [ -d "tests" ]; then
        echo "Removing: tests/"
        rm -rf tests
    fi

    if [ -d "test_patterns" ]; then
        echo "Removing: test_patterns/"
        rm -rf test_patterns
    fi

    if [ -d "test_outputs" ]; then
        echo "Removing: test_outputs/"
        rm -rf test_outputs
    fi

    if [ -d "comparison_results" ]; then
        echo "Removing: comparison_results/"
        rm -rf comparison_results
    fi

    # Remove any stray test SVGs and previews
    find . -maxdepth 1 -name "tiny_*.svg" -o -name "tiny_*_preview.png" 2>/dev/null | while read file; do
        echo "Removing: $file"
        rm -f "$file"
    done

    echo ""
    echo "✅ Cleanup complete!"
    echo ""
    exit 0
fi

if [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
    echo "Usage: ./run_retinex_tests.sh [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --generate    Generate and process test patterns"
    echo "  --clean       Remove all generated test files and directories"
    echo "  --help        Show this help message"
    echo ""
    exit 0
fi

# If no arguments, show what will happen and exit
if [ -z "$1" ]; then
    echo "════════════════════════════════════════════════════════════════════"
    echo "  MOPA LASER COLOR REPRODUCTION - RETINEX TEST SUITE"
    echo "════════════════════════════════════════════════════════════════════"
    echo ""
    echo "This script will:"
    echo "  1. Generate 19 color test patterns (gradients, patches, etc.)"
    echo "  2. Process each with 3 algorithms (original, retinex_floyd, retinex_atkinson)"
    echo "  3. Create 57 SVG files ready for LightBurn"
    echo "  4. Generate visual comparison previews"
    echo "  5. Organize everything in tests/ directory"
    echo ""
    echo "Estimated time: ~1-2 minutes"
    echo "Disk space: ~15-20 MB"
    echo ""
    echo "Usage:"
    echo "  ./run_retinex_tests.sh --generate    Run the test generation"
    echo "  ./run_retinex_tests.sh --clean       Clean up all test outputs"
    echo "  ./run_retinex_tests.sh --help        Show help"
    echo ""
    exit 0
fi

# Require explicit --generate flag
if [ "$1" != "--generate" ]; then
    echo "❌ Error: Unknown option '$1'"
    echo ""
    echo "Run './run_retinex_tests.sh' to see what this script does"
    echo "Run './run_retinex_tests.sh --help' for usage information"
    echo ""
    exit 1
fi

echo "════════════════════════════════════════════════════════════════════"
echo "  MOPA LASER COLOR REPRODUCTION - AUTOMATED TEST SUITE"
echo "════════════════════════════════════════════════════════════════════"
echo ""

# Check Python availability
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo "❌ Python not found. Please install Python 3.7+ to run this test."
    exit 1
fi

# Use python3 if available, otherwise python
PYTHON_CMD=$(command -v python3 || command -v python)
echo "✓ Using Python: $PYTHON_CMD"

# Check dependencies
echo ""
echo "Checking dependencies..."
$PYTHON_CMD -c "import PIL; import numpy; import scipy" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ Missing required Python packages."
    echo ""
    echo "Please install dependencies:"
    echo "  pip install Pillow numpy scipy"
    echo ""
    echo "Or if using a virtual environment:"
    echo "  python -m venv venv"
    echo "  source venv/bin/activate  # On Windows: venv\\Scripts\\activate"
    echo "  pip install -r requirements.txt"
    exit 1
fi
echo "✓ All dependencies installed"

echo ""
echo "════════════════════════════════════════════════════════════════════"
echo "  STARTING TEST SUITE"
echo "════════════════════════════════════════════════════════════════════"
echo ""

# Generate organized test patterns
echo "Step 1: Generating test patterns..."
$PYTHON_CMD generate_organized_tests.py

echo ""
echo "Step 2: Processing test patterns with all algorithms..."
$PYTHON_CMD process_organized_tests.py

echo ""
echo "════════════════════════════════════════════════════════════════════"
echo "  ✅ TESTS COMPLETE!"
echo "════════════════════════════════════════════════════════════════════"
echo ""
echo "📁 Organized test results:"
echo "   tests/"
echo "   ├── 01_quick_start/      ← START HERE"
echo "   ├── 02_gradients/"
echo "   ├── 03_color_accuracy/"
echo "   └── 04_advanced/"
echo ""
echo "Each category contains:"
echo "  • input/                Source test images"
echo "  • svg_for_laser/        SVG files for LightBurn (3 algorithms)"
echo "  • previews/             Visual comparisons"
echo "  • README.txt            Testing instructions"
echo ""
echo "🚀 QUICK START:"
echo "  1. Read:    tests/README.txt"
echo "  2. Go to:   tests/01_quick_start/svg_for_laser/"
echo "  3. Pick:    grayscale_gradient.svg from any algorithm folder"
echo "  4. Load:    Into LightBurn and engrave"
echo "  5. Compare: Try all three algorithms!"
echo ""
