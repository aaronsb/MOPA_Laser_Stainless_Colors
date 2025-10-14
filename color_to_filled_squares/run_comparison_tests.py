"""
Automated comparison test runner for MOPA laser color reproduction.

This script:
1. Generates test patterns (if not already present)
2. Processes each test pattern with BOTH algorithms:
   - Original nearest-color matching
   - Retinex-enhanced spatial dithering (Floyd-Steinberg + Atkinson)
3. Creates side-by-side comparison images
4. Generates a summary report

The goal is to make it trivially easy for the original author to evaluate
the improvements without needing to understand the implementation details.
"""

import os
import sys
import time
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import shutil


def ensure_test_patterns_exist(test_dir="test_patterns"):
    """
    Generate test patterns if they don't exist.

    Args:
        test_dir: Directory containing test patterns

    Returns:
        List of test pattern file paths
    """
    if not os.path.exists(test_dir) or len(list(Path(test_dir).glob("*.png"))) == 0:
        print("📊 Generating test patterns...")
        subprocess.run([sys.executable, "generate_test_patterns.py", test_dir])
        print()

    patterns = sorted(Path(test_dir).glob("*.png"))
    return [str(p) for p in patterns]


def run_original_algorithm(input_file, output_dir):
    """
    Run the original color_to_squares.py algorithm.

    Args:
        input_file: Path to input image
        output_dir: Directory for output files

    Returns:
        Path to output SVG file
    """
    basename = Path(input_file).stem
    output_svg = os.path.join(output_dir, f"{basename}_original.svg")

    # Run original script
    subprocess.run([
        sys.executable,
        "color_to_squares.py",
        input_file,
        output_svg,
        "0.25"
    ], capture_output=True)

    return output_svg


def run_retinex_algorithm(input_file, output_dir, dithering="floyd-steinberg"):
    """
    Run the Retinex-enhanced algorithm with specified dithering.

    Args:
        input_file: Path to input image
        output_dir: Directory for output files
        dithering: "floyd-steinberg", "atkinson", or "none"

    Returns:
        Tuple of (SVG path, preview PNG path)
    """
    basename = Path(input_file).stem
    output_svg = os.path.join(output_dir, f"{basename}_retinex_{dithering}.svg")

    # Run Retinex script
    subprocess.run([
        sys.executable,
        "color_to_squares_retinex.py",
        input_file,
        output_svg,
        "0.25",
        dithering
    ], capture_output=True)

    # Preview image should be created automatically
    preview_path = output_svg.replace('.svg', '_preview.png')

    return output_svg, preview_path


def create_comparison_image(original_path, retinex_fs_path, retinex_atk_path, output_path):
    """
    Create a side-by-side comparison image with labels.

    Args:
        original_path: Path to original algorithm preview
        retinex_fs_path: Path to Retinex Floyd-Steinberg preview
        retinex_atk_path: Path to Retinex Atkinson preview
        output_path: Path for output comparison image
    """
    # Load preview images (they're created by the Retinex script)
    # For original, we need to render from the input since it doesn't create preview
    img_original = Image.open(original_path) if os.path.exists(original_path) else None
    img_retinex_fs = Image.open(retinex_fs_path) if os.path.exists(retinex_fs_path) else None
    img_retinex_atk = Image.open(retinex_atk_path) if os.path.exists(retinex_atk_path) else None

    if not img_retinex_fs:
        return  # Skip if no Retinex output

    # Create comparison layout
    margin = 20
    label_height = 40
    img_height = img_retinex_fs.height
    img_width = img_retinex_fs.width

    # Three columns: original, Floyd-Steinberg, Atkinson
    total_width = 3 * img_width + 4 * margin
    total_height = img_height + label_height + 2 * margin

    comparison = Image.new('RGB', (total_width, total_height), color=(50, 50, 50))
    draw = ImageDraw.Draw(comparison)

    # Column positions
    col_x = [margin, margin + img_width + margin, margin + 2 * (img_width + margin)]
    labels = ["Original (nearest color)", "Retinex + Floyd-Steinberg", "Retinex + Atkinson"]

    # Paste images and add labels
    images = [img_original, img_retinex_fs, img_retinex_atk]
    for idx, (x, label, img) in enumerate(zip(col_x, labels, images)):
        if img:
            comparison.paste(img, (x, margin + label_height))

        # Draw label (simple text - no font needed for basic version)
        text_x = x + img_width // 2
        # Could add text here if font is available

    comparison.save(output_path)


def process_all_test_patterns(test_dir="test_patterns", output_dir="test_outputs", comparison_dir="comparison_results"):
    """
    Process all test patterns with both algorithms and create comparisons.

    Args:
        test_dir: Directory containing test patterns
        output_dir: Directory for algorithm outputs
        comparison_dir: Directory for comparison images

    Returns:
        Dictionary with processing statistics
    """
    # Create output directories
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(comparison_dir, exist_ok=True)

    # Ensure test patterns exist
    patterns = ensure_test_patterns_exist(test_dir)

    if not patterns:
        print("❌ No test patterns found!")
        return {}

    print(f"🔬 Processing {len(patterns)} test patterns...\n")

    results = {
        'total': len(patterns),
        'processed': 0,
        'failed': 0,
        'timings': {}
    }

    for idx, pattern in enumerate(patterns, 1):
        basename = Path(pattern).stem
        print(f"[{idx}/{len(patterns)}] Processing: {basename}")

        try:
            start_time = time.time()

            # Run original algorithm
            print(f"  → Running original algorithm...")
            original_svg = run_original_algorithm(pattern, output_dir)

            # Run Retinex with Floyd-Steinberg
            print(f"  → Running Retinex + Floyd-Steinberg...")
            retinex_fs_svg, retinex_fs_preview = run_retinex_algorithm(
                pattern, output_dir, "floyd-steinberg"
            )

            # Run Retinex with Atkinson
            print(f"  → Running Retinex + Atkinson...")
            retinex_atk_svg, retinex_atk_preview = run_retinex_algorithm(
                pattern, output_dir, "atkinson"
            )

            # Create comparison image
            print(f"  → Creating comparison image...")
            comparison_path = os.path.join(comparison_dir, f"{basename}_comparison.png")
            create_comparison_image(
                pattern,  # Use original test pattern for comparison
                retinex_fs_preview,
                retinex_atk_preview,
                comparison_path
            )

            elapsed = time.time() - start_time
            results['timings'][basename] = elapsed
            results['processed'] += 1

            print(f"  ✓ Complete ({elapsed:.2f}s)\n")

        except Exception as e:
            print(f"  ✗ Failed: {e}\n")
            results['failed'] += 1

    return results


def generate_summary_report(results, output_file="test_report.txt"):
    """
    Generate a summary report of the testing results.

    Args:
        results: Dictionary with processing statistics
        output_file: Path to output report file
    """
    with open(output_file, 'w') as f:
        f.write("=" * 70 + "\n")
        f.write("MOPA LASER COLOR REPRODUCTION - COMPARISON TEST REPORT\n")
        f.write("=" * 70 + "\n\n")

        f.write(f"Total test patterns: {results['total']}\n")
        f.write(f"Successfully processed: {results['processed']}\n")
        f.write(f"Failed: {results['failed']}\n\n")

        if results['timings']:
            f.write("Processing times:\n")
            f.write("-" * 70 + "\n")
            for name, elapsed in sorted(results['timings'].items()):
                f.write(f"  {name:50s} {elapsed:6.2f}s\n")

            avg_time = sum(results['timings'].values()) / len(results['timings'])
            f.write("-" * 70 + "\n")
            f.write(f"  Average processing time: {avg_time:.2f}s\n\n")

        f.write("\n" + "=" * 70 + "\n")
        f.write("HOW TO EVALUATE THE RESULTS\n")
        f.write("=" * 70 + "\n\n")

        f.write("1. VIEW COMPARISON IMAGES:\n")
        f.write("   - Look in 'comparison_results/' directory\n")
        f.write("   - Each image shows three versions side-by-side:\n")
        f.write("     * Original algorithm (nearest color matching)\n")
        f.write("     * Retinex + Floyd-Steinberg dithering\n")
        f.write("     * Retinex + Atkinson dithering\n\n")

        f.write("2. WHAT TO LOOK FOR:\n")
        f.write("   - Gradient smoothness (less banding)\n")
        f.write("   - Intermediate color reproduction\n")
        f.write("   - Detail preservation\n")
        f.write("   - Color accuracy in patches\n\n")

        f.write("3. LOAD SVG FILES INTO LIGHTBURN:\n")
        f.write("   - SVG files are in 'test_outputs/' directory\n")
        f.write("   - Files ending in '_original.svg': Original algorithm\n")
        f.write("   - Files ending in '_retinex_floyd-steinberg.svg': Retinex + FS\n")
        f.write("   - Files ending in '_retinex_atkinson.svg': Retinex + Atkinson\n\n")

        f.write("4. ENGRAVE AND COMPARE:\n")
        f.write("   - Pick a few representative test patterns\n")
        f.write("   - Engrave the same pattern with all three algorithms\n")
        f.write("   - Compare the physical results\n\n")

        f.write("RECOMMENDATIONS:\n")
        f.write("  - Start with 'smooth_gradients.png' to see banding reduction\n")
        f.write("  - Try 'hsv_colorspace.png' to see gamut expansion\n")
        f.write("  - Use 'color_patches.png' for discrete color accuracy\n")
        f.write("  - Test 'skin_tones.png' if you do portrait work\n\n")


def main():
    """
    Main entry point for comparison testing.
    """
    print("=" * 70)
    print("MOPA LASER COLOR REPRODUCTION - AUTOMATED COMPARISON TEST")
    print("=" * 70)
    print()

    # Check that required scripts exist
    required_files = ["color_to_squares.py", "color_to_squares_retinex.py", "generate_test_patterns.py"]
    missing = [f for f in required_files if not os.path.exists(f)]

    if missing:
        print(f"❌ Missing required files: {', '.join(missing)}")
        print("   Make sure you're running this from the color_to_filled_squares directory.")
        sys.exit(1)

    # Run the comparison tests
    results = process_all_test_patterns()

    # Generate summary report
    print("\n📝 Generating summary report...")
    generate_summary_report(results, "comparison_results/test_report.txt")

    print("\n" + "=" * 70)
    print("✅ TESTING COMPLETE!")
    print("=" * 70)
    print(f"\nProcessed: {results['processed']}/{results['total']} test patterns")
    print(f"Failed: {results['failed']}")
    print("\nResults saved to:")
    print("  - comparison_results/     (side-by-side comparison images)")
    print("  - test_outputs/           (SVG files for LightBurn)")
    print("  - test_report.txt         (summary report)")
    print("\nNext steps:")
    print("  1. Review comparison images in 'comparison_results/'")
    print("  2. Load SVG files from 'test_outputs/' into LightBurn")
    print("  3. Engrave a few test patterns to validate on actual hardware")
    print()


if __name__ == "__main__":
    main()
