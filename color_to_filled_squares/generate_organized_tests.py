"""
Generate organized test suite with hierarchical directory structure.

Directory Structure:
tests/
├── 01_quick_start/      ← START HERE! Fast tests showing clear improvements
├── 02_gradients/        ← Gradient smoothness and banding tests
├── 03_color_accuracy/   ← Color patches and palette validation
└── 04_advanced/         ← Complex tests (HSV space, radials)

Each test category contains:
- input/            : Source test images
- svg_for_laser/    : SVG files organized by algorithm (load into LightBurn)
  ├── original/
  ├── retinex_floyd/
  └── retinex_atkinson/
- previews/         : Visual comparison images (gitignored)
"""

import os
import sys
from pathlib import Path
import subprocess
from generate_test_patterns import *


# Test suite organization
TEST_CATEGORIES = {
    "01_quick_start": {
        "description": "🚀 START HERE - Quick visual comparison (5-10 min laser time)",
        "tests": [
            ("grayscale_gradient", lambda: create_linear_gradient(600, 100, (0, 0, 0), (255, 255, 255))),
            ("smooth_gradients", lambda: create_smooth_gradient_test(400, 60)),  # Smaller for quick test
            ("color_patches", lambda: create_color_patches(patch_size=60, margin=8)),
        ]
    },
    "02_gradients": {
        "description": "📊 Gradient Tests - Shows banding reduction",
        "tests": [
            ("hue_sweep_full", lambda: create_hue_sweep(600, 100, saturation=1.0, value=1.0)),
            ("hue_sweep_desaturated", lambda: create_hue_sweep(600, 100, saturation=0.5, value=1.0)),
            ("saturation_gradient_red", lambda: create_saturation_gradient(600, 100, hue=0.0, value=1.0)),
            ("saturation_gradient_green", lambda: create_saturation_gradient(600, 100, hue=0.33, value=1.0)),
            ("saturation_gradient_blue", lambda: create_saturation_gradient(600, 100, hue=0.66, value=1.0)),
            ("value_gradient_red", lambda: create_value_gradient(600, 100, hue=0.0, saturation=1.0)),
            ("value_gradient_green", lambda: create_value_gradient(600, 100, hue=0.33, saturation=1.0)),
            ("value_gradient_blue", lambda: create_value_gradient(600, 100, hue=0.66, saturation=1.0)),
        ]
    },
    "03_color_accuracy": {
        "description": "🎨 Color Accuracy - Discrete color reproduction",
        "tests": [
            ("laser_palette", lambda: create_laser_palette_test(patch_size=80, margin=5)),
            ("skin_tones", lambda: create_skin_tone_patches(patch_size=80, margin=10)),
            ("color_patches_full", lambda: create_color_patches(patch_size=80, margin=10)),
        ]
    },
    "04_advanced": {
        "description": "🔬 Advanced Tests - Gamut and complex patterns",
        "tests": [
            ("hsv_colorspace", lambda: create_hsv_color_space(size=400)),  # Hue/Sat at full brightness
            ("hsv_value_ramp", lambda: create_hsv_value_ramp(size=400)),  # Value ramp to black
            ("radial_white_red", lambda: create_radial_gradient(300, 300, (255, 255, 255), (255, 0, 0))),
            ("radial_black_yellow", lambda: create_radial_gradient(300, 300, (0, 0, 0), (255, 255, 0))),
            ("radial_blue_green", lambda: create_radial_gradient(300, 300, (0, 0, 255), (0, 255, 0))),
        ]
    }
}


def create_directory_structure(base_dir="tests"):
    """
    Create organized test directory structure.

    Returns:
        Dictionary mapping category to paths
    """
    structure = {}

    for category in TEST_CATEGORIES.keys():
        cat_path = os.path.join(base_dir, category)
        structure[category] = {
            'base': cat_path,
            'input': os.path.join(cat_path, 'input'),
            'svg': {
                'original': os.path.join(cat_path, 'svg_for_laser', 'original'),
                'retinex_floyd': os.path.join(cat_path, 'svg_for_laser', 'retinex_floyd'),
                'retinex_atkinson': os.path.join(cat_path, 'svg_for_laser', 'retinex_atkinson'),
            },
            'previews': os.path.join(cat_path, 'previews'),
        }

        # Create all directories
        os.makedirs(structure[category]['input'], exist_ok=True)
        os.makedirs(structure[category]['svg']['original'], exist_ok=True)
        os.makedirs(structure[category]['svg']['retinex_floyd'], exist_ok=True)
        os.makedirs(structure[category]['svg']['retinex_atkinson'], exist_ok=True)
        os.makedirs(structure[category]['previews'], exist_ok=True)

    return structure


def generate_test_patterns(base_dir="tests"):
    """
    Generate all test patterns organized by category.

    Returns:
        Dictionary mapping category -> list of (name, input_path)
    """
    print("=" * 70)
    print("GENERATING ORGANIZED TEST SUITE")
    print("=" * 70)
    print()

    # Create directory structure
    print("📁 Creating directory structure...")
    structure = create_directory_structure(base_dir)
    print("   ✓ Created organized test directories\n")

    # Generate test patterns
    generated = {}

    for category, info in TEST_CATEGORIES.items():
        print(f"{info['description']}")
        print("-" * 70)

        generated[category] = []
        input_dir = structure[category]['input']

        for test_name, generator_func in info['tests']:
            filename = f"{test_name}.png"
            filepath = os.path.join(input_dir, filename)

            # Generate the test pattern
            img = generator_func()
            img.save(filepath)

            generated[category].append((test_name, filepath))

            # Get image dimensions for display
            width, height = img.size
            file_size = os.path.getsize(filepath) / 1024  # KB

            print(f"  ✓ {test_name:30s} ({width}x{height}, {file_size:.1f}KB)")

        print()

    # Count totals
    total_tests = sum(len(tests) for tests in generated.values())

    print("=" * 70)
    print(f"✅ Generated {total_tests} test patterns in {len(TEST_CATEGORIES)} categories")
    print("=" * 70)
    print()

    return generated, structure


def create_category_readme(category, info, cat_path):
    """Create a README for each test category explaining what to test."""

    readme_path = os.path.join(cat_path, "README.txt")

    with open(readme_path, 'w') as f:
        f.write("=" * 70 + "\n")
        f.write(f"{category.upper()} - {info['description']}\n")
        f.write("=" * 70 + "\n\n")

        f.write("DIRECTORY STRUCTURE:\n")
        f.write("-" * 70 + "\n")
        f.write("  input/                  Source test images\n")
        f.write("  svg_for_laser/          SVG files to load into LightBurn\n")
        f.write("    ├── original/         Original nearest-color algorithm\n")
        f.write("    ├── retinex_floyd/    Retinex + Floyd-Steinberg dithering\n")
        f.write("    └── retinex_atkinson/ Retinex + Atkinson dithering\n")
        f.write("  previews/               Visual comparisons (for reference)\n\n")

        f.write("HOW TO TEST:\n")
        f.write("-" * 70 + "\n")
        f.write("1. Pick a test pattern from svg_for_laser/\n")
        f.write("2. Load the SVG file into LightBurn\n")
        f.write("3. Engrave it on stainless steel\n")
        f.write("4. Compare results from all three algorithms\n\n")

        if category == "01_quick_start":
            f.write("RECOMMENDATION:\n")
            f.write("-" * 70 + "\n")
            f.write("START WITH THESE FILES:\n\n")
            f.write("  1. grayscale_gradient\n")
            f.write("     - Shows smooth grayscale reproduction\n")
            f.write("     - Easy to see banding vs smooth transitions\n")
            f.write("     - Fast to engrave (~2-3 minutes)\n\n")
            f.write("  2. smooth_gradients\n")
            f.write("     - Shows color gradient smoothness\n")
            f.write("     - Reveals banding in original vs dithered\n")
            f.write("     - Medium engrave time (~5-7 minutes)\n\n")
            f.write("  3. color_patches\n")
            f.write("     - Shows discrete color accuracy\n")
            f.write("     - Compare color reproduction quality\n")
            f.write("     - Fast to engrave (~2-3 minutes)\n\n")
            f.write("EXPECTED RESULTS:\n")
            f.write("  - original/           : Hard color transitions, visible banding\n")
            f.write("  - retinex_floyd/      : Smooth gradients, richer colors\n")
            f.write("  - retinex_atkinson/   : Sharp details, good gradients\n\n")

        f.write(f"TEST PATTERNS IN THIS CATEGORY: {len(info['tests'])}\n")
        for idx, (test_name, _) in enumerate(info['tests'], 1):
            f.write(f"  {idx}. {test_name}\n")

        f.write("\n")


def create_master_readme(base_dir, structure):
    """Create master README explaining the entire test suite."""

    readme_path = os.path.join(base_dir, "README.txt")

    with open(readme_path, 'w') as f:
        f.write("=" * 70 + "\n")
        f.write("MOPA LASER COLOR REPRODUCTION - TEST SUITE\n")
        f.write("=" * 70 + "\n\n")

        f.write("This organized test suite helps you evaluate the Retinex-enhanced\n")
        f.write("color reproduction algorithm compared to the original approach.\n\n")

        f.write("🚀 QUICK START:\n")
        f.write("-" * 70 + "\n")
        f.write("1. Go to:  01_quick_start/svg_for_laser/\n")
        f.write("2. Pick:   grayscale_gradient.svg from any algorithm folder\n")
        f.write("3. Load:   Into LightBurn\n")
        f.write("4. Engrave: On stainless steel\n")
        f.write("5. Compare: Engrave the same pattern from all three folders\n\n")

        f.write("📁 DIRECTORY ORGANIZATION:\n")
        f.write("-" * 70 + "\n\n")

        for category, info in TEST_CATEGORIES.items():
            f.write(f"{category}/\n")
            f.write(f"  {info['description']}\n")
            f.write(f"  Tests: {len(info['tests'])}\n")
            f.write(f"  See {category}/README.txt for details\n\n")

        f.write("\n")
        f.write("🎯 WHAT TO LOOK FOR:\n")
        f.write("-" * 70 + "\n")
        f.write("Original Algorithm:\n")
        f.write("  • Sharp color transitions (banding)\n")
        f.write("  • Limited color palette (10 discrete colors)\n")
        f.write("  • Loss of subtle gradients\n\n")

        f.write("Retinex + Floyd-Steinberg:\n")
        f.write("  • Smooth gradients with no banding\n")
        f.write("  • 2-3x more perceived colors through dithering\n")
        f.write("  • Best for photos and smooth color transitions\n\n")

        f.write("Retinex + Atkinson:\n")
        f.write("  • Sharp detail preservation\n")
        f.write("  • Good gradient reproduction\n")
        f.write("  • Best for logos, text, and line art\n\n")

        f.write("\n")
        f.write("⏱️  ESTIMATED ENGRAVE TIMES (per test pattern):\n")
        f.write("-" * 70 + "\n")
        f.write("  Quick start tests:    2-7 minutes each\n")
        f.write("  Gradient tests:       2-5 minutes each\n")
        f.write("  Color accuracy:       2-4 minutes each\n")
        f.write("  Advanced tests:       5-10 minutes each\n\n")

        f.write("Note: Times vary based on image size and laser settings\n\n")

        f.write("\n")
        f.write("💡 RECOMMENDATION:\n")
        f.write("-" * 70 + "\n")
        f.write("Start with 01_quick_start/ to quickly see the improvements.\n")
        f.write("If you like what you see, try tests from other categories.\n\n")

        f.write("The 'previews/' folders contain PNG images showing what the\n")
        f.write("dithered output looks like, so you can preview before engraving.\n\n")


if __name__ == "__main__":
    base_dir = "tests"
    if len(sys.argv) > 1:
        base_dir = sys.argv[1]

    # Generate test patterns
    generated, structure = generate_test_patterns(base_dir)

    # Create README files
    print("📝 Creating documentation...")
    create_master_readme(base_dir, structure)
    for category, info in TEST_CATEGORIES.items():
        create_category_readme(category, info, structure[category]['base'])
    print("   ✓ Created README files\n")

    # Summary
    print("=" * 70)
    print("✅ TEST SUITE READY")
    print("=" * 70)
    print()
    print(f"Location: {base_dir}/")
    print()
    print("Next steps:")
    print("  1. Run process_organized_tests.py to generate SVG files")
    print("  2. Read tests/README.txt for testing instructions")
    print("  3. Start with 01_quick_start/ for fastest validation")
    print()
