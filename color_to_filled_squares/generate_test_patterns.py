"""
Generate comprehensive color test patterns for evaluating MOPA laser color reproduction.

This script creates standard test charts used in color science and printing:
- Linear gradients (RGB channels, grayscale)
- Hue sweeps at various saturation/value levels
- Color patches (pure colors, intermediate blends)
- Radial gradients
- Skin tone patches
- Gamut boundary visualization

The output images can be processed with both the original and Retinex-enhanced
algorithms to compare color reproduction quality.
"""

import numpy as np
from PIL import Image, ImageDraw, ImageFont
import colorsys
import os


def create_linear_gradient(width, height, start_color, end_color, vertical=False):
    """
    Create a smooth linear gradient between two colors.

    Args:
        width, height: Image dimensions
        start_color: RGB tuple (r, g, b) for start
        end_color: RGB tuple (r, g, b) for end
        vertical: If True, gradient runs top-to-bottom; else left-to-right

    Returns:
        PIL Image
    """
    img = Image.new('RGB', (width, height))
    draw = ImageDraw.Draw(img)

    start = np.array(start_color, dtype=float)
    end = np.array(end_color, dtype=float)

    if vertical:
        for y in range(height):
            t = y / height
            color = tuple((start * (1 - t) + end * t).astype(int))
            draw.line([(0, y), (width, y)], fill=color)
    else:
        for x in range(width):
            t = x / width
            color = tuple((start * (1 - t) + end * t).astype(int))
            draw.line([(x, 0), (x, height)], fill=color)

    return img


def create_hue_sweep(width, height, saturation=1.0, value=1.0):
    """
    Create a full hue sweep (0-360 degrees) at constant saturation and value.

    Args:
        width, height: Image dimensions
        saturation: HSV saturation (0.0-1.0)
        value: HSV value/brightness (0.0-1.0)

    Returns:
        PIL Image
    """
    img = Image.new('RGB', (width, height))
    pixels = img.load()

    for x in range(width):
        hue = x / width  # 0.0 to 1.0
        r, g, b = colorsys.hsv_to_rgb(hue, saturation, value)
        color = (int(r * 255), int(g * 255), int(b * 255))
        for y in range(height):
            pixels[x, y] = color

    return img


def create_saturation_gradient(width, height, hue=0.0, value=1.0):
    """
    Create a saturation gradient from gray to full color at a specific hue.

    Args:
        width, height: Image dimensions
        hue: HSV hue (0.0-1.0, where 0=red, 0.33=green, 0.66=blue)
        value: HSV value/brightness (0.0-1.0)

    Returns:
        PIL Image
    """
    img = Image.new('RGB', (width, height))
    pixels = img.load()

    for x in range(width):
        saturation = x / width
        r, g, b = colorsys.hsv_to_rgb(hue, saturation, value)
        color = (int(r * 255), int(g * 255), int(b * 255))
        for y in range(height):
            pixels[x, y] = color

    return img


def create_value_gradient(width, height, hue=0.0, saturation=1.0):
    """
    Create a value/brightness gradient from black to full brightness.

    Args:
        width, height: Image dimensions
        hue: HSV hue (0.0-1.0)
        saturation: HSV saturation (0.0-1.0)

    Returns:
        PIL Image
    """
    img = Image.new('RGB', (width, height))
    pixels = img.load()

    for x in range(width):
        value = x / width
        r, g, b = colorsys.hsv_to_rgb(hue, saturation, value)
        color = (int(r * 255), int(g * 255), int(b * 255))
        for y in range(height):
            pixels[x, y] = color

    return img


def create_radial_gradient(width, height, center_color, edge_color):
    """
    Create a radial gradient from center to edges.

    Args:
        width, height: Image dimensions
        center_color: RGB tuple for center
        edge_color: RGB tuple for edges

    Returns:
        PIL Image
    """
    img = Image.new('RGB', (width, height))
    pixels = img.load()

    center_x, center_y = width / 2, height / 2
    max_dist = np.sqrt(center_x**2 + center_y**2)

    center = np.array(center_color, dtype=float)
    edge = np.array(edge_color, dtype=float)

    for y in range(height):
        for x in range(width):
            dx, dy = x - center_x, y - center_y
            dist = np.sqrt(dx**2 + dy**2)
            t = min(dist / max_dist, 1.0)
            color = tuple((center * (1 - t) + edge * t).astype(int))
            pixels[x, y] = color

    return img


def create_color_patches(patch_size=100, margin=10):
    """
    Create a grid of color patches showing primary, secondary, and tertiary colors.

    Args:
        patch_size: Size of each square patch
        margin: Margin between patches

    Returns:
        PIL Image
    """
    # Define standard color patches
    colors = [
        # Row 1: Primaries and secondaries
        [(255, 0, 0), (255, 127, 0), (255, 255, 0), (0, 255, 0), (0, 255, 255), (0, 0, 255), (255, 0, 255)],
        # Row 2: Desaturated versions (50% saturation)
        [(255, 127, 127), (255, 191, 127), (255, 255, 127), (127, 255, 127), (127, 255, 255), (127, 127, 255), (255, 127, 255)],
        # Row 3: Dark versions (50% value)
        [(127, 0, 0), (127, 63, 0), (127, 127, 0), (0, 127, 0), (0, 127, 127), (0, 0, 127), (127, 0, 127)],
        # Row 4: Grayscale
        [(0, 0, 0), (32, 32, 32), (64, 64, 64), (96, 96, 96), (128, 128, 128), (192, 192, 192), (255, 255, 255)],
    ]

    rows = len(colors)
    cols = len(colors[0])

    width = cols * patch_size + (cols + 1) * margin
    height = rows * patch_size + (rows + 1) * margin

    img = Image.new('RGB', (width, height), color=(40, 40, 40))
    draw = ImageDraw.Draw(img)

    for row_idx, row in enumerate(colors):
        for col_idx, color in enumerate(row):
            x = margin + col_idx * (patch_size + margin)
            y = margin + row_idx * (patch_size + margin)
            draw.rectangle([x, y, x + patch_size, y + patch_size], fill=color)

    return img


def create_skin_tone_patches(patch_size=100, margin=10):
    """
    Create patches representing various skin tones - critical for portrait work.

    Returns:
        PIL Image
    """
    # Skin tones from very light to very dark (approximate Fitzpatrick scale)
    skin_tones = [
        (255, 224, 196),  # Very light
        (255, 209, 178),  # Light
        (241, 194, 155),  # Light-medium
        (224, 172, 128),  # Medium
        (198, 134, 90),   # Medium-dark
        (141, 85, 36),    # Dark
        (90, 49, 20),     # Very dark
    ]

    cols = len(skin_tones)
    width = cols * patch_size + (cols + 1) * margin
    height = patch_size + 2 * margin

    img = Image.new('RGB', (width, height), color=(40, 40, 40))
    draw = ImageDraw.Draw(img)

    for idx, color in enumerate(skin_tones):
        x = margin + idx * (patch_size + margin)
        y = margin
        draw.rectangle([x, y, x + patch_size, y + patch_size], fill=color)

    return img


def create_laser_palette_test(patch_size=80, margin=5):
    """
    Create patches showing the exact 10 colors achievable with the MOPA laser.

    Returns:
        PIL Image with labels
    """
    # Colors from the laser settings
    laser_colors = [
        ("Black", (0, 0, 0)),
        ("White", (180, 180, 180)),
        ("Gray", (128, 128, 128)),
        ("Purple", (128, 0, 128)),
        ("Blue", (0, 0, 255)),
        ("Green", (0, 224, 0)),
        ("Yellow", (208, 208, 0)),
        ("Orange", (255, 128, 0)),
        ("Red", (255, 0, 0)),
        ("Brown", (139, 69, 19)),
    ]

    cols = 5
    rows = 2

    width = cols * patch_size + (cols + 1) * margin
    height = rows * (patch_size + 20) + (rows + 1) * margin

    img = Image.new('RGB', (width, height), color=(40, 40, 40))
    draw = ImageDraw.Draw(img)

    for idx, (name, color) in enumerate(laser_colors):
        row = idx // cols
        col = idx % cols

        x = margin + col * (patch_size + margin)
        y = margin + row * (patch_size + 20 + margin)

        # Draw color patch
        draw.rectangle([x, y, x + patch_size, y + patch_size], fill=color)

        # Draw label (simplified - no font needed)
        # In actual use, could add text if PIL has font access

    return img


def create_hsv_color_space(size=400, value=1.0):
    """
    Create a 2D visualization of HSV color space (Hue vs Saturation).

    Args:
        size: Size of the square image
        value: HSV value (1.0 = bright/saturated, 0.0 = dark/black)

    Returns:
        PIL Image
    """
    img = Image.new('RGB', (size, size))
    pixels = img.load()

    center = size / 2

    for y in range(size):
        for x in range(size):
            dx = x - center
            dy = y - center

            # Calculate saturation from distance to center
            dist = np.sqrt(dx**2 + dy**2)
            saturation = min(dist / center, 1.0)

            # Calculate hue from angle
            angle = np.arctan2(dy, dx)
            hue = (angle + np.pi) / (2 * np.pi)

            # Convert to RGB
            r, g, b = colorsys.hsv_to_rgb(hue, saturation, value)
            pixels[x, y] = (int(r * 255), int(g * 255), int(b * 255))

    return img


def create_hsv_value_ramp(size=400):
    """
    Create HSV color space with value ramp from full color (edge) to black (center).
    This is the "dark" version - ramps TO black instead of FROM black.

    Args:
        size: Size of the square image

    Returns:
        PIL Image
    """
    img = Image.new('RGB', (size, size))
    pixels = img.load()

    center = size / 2

    for y in range(size):
        for x in range(size):
            dx = x - center
            dy = y - center

            # Calculate value from distance to center (inverted - center is dark)
            dist = np.sqrt(dx**2 + dy**2)
            value = min(dist / center, 1.0)  # 0 at center (black), 1 at edge (full color)

            # Calculate hue from angle
            angle = np.arctan2(dy, dx)
            hue = (angle + np.pi) / (2 * np.pi)

            # Full saturation
            saturation = 1.0

            # Convert to RGB
            r, g, b = colorsys.hsv_to_rgb(hue, saturation, value)
            pixels[x, y] = (int(r * 255), int(g * 255), int(b * 255))

    return img


def create_smooth_gradient_test(width=600, height=100):
    """
    Create a series of smooth gradients to test banding/posterization.

    Returns:
        PIL Image
    """
    tests = [
        # (name, start_color, end_color)
        ("Red", (0, 0, 0), (255, 0, 0)),
        ("Green", (0, 0, 0), (0, 255, 0)),
        ("Blue", (0, 0, 0), (0, 0, 255)),
        ("Yellow", (0, 0, 0), (255, 255, 0)),
        ("Cyan", (0, 0, 0), (0, 255, 255)),
        ("Magenta", (0, 0, 0), (255, 0, 255)),
    ]

    margin = 5
    total_height = len(tests) * (height + margin) + margin

    img = Image.new('RGB', (width, total_height), color=(40, 40, 40))

    for idx, (name, start, end) in enumerate(tests):
        gradient = create_linear_gradient(width, height, start, end)
        img.paste(gradient, (0, margin + idx * (height + margin)))

    return img


def generate_all_test_patterns(output_dir="test_patterns"):
    """
    Generate all test patterns and save them to the output directory.

    Args:
        output_dir: Directory to save test pattern images

    Returns:
        List of generated file paths
    """
    os.makedirs(output_dir, exist_ok=True)
    generated_files = []

    print("Generating color test patterns...")

    # 1. Hue sweeps at different saturation/value levels
    print("  - Hue sweeps...")
    for v in [1.0, 0.75, 0.5]:
        for s in [1.0, 0.75, 0.5]:
            filename = f"hue_sweep_s{int(s*100)}_v{int(v*100)}.png"
            path = os.path.join(output_dir, filename)
            img = create_hue_sweep(600, 100, saturation=s, value=v)
            img.save(path)
            generated_files.append(path)
            print(f"    ✓ {filename}")

    # 2. Saturation gradients for primary hues
    print("  - Saturation gradients...")
    hues = [("red", 0.0), ("green", 0.33), ("blue", 0.66)]
    for name, hue in hues:
        filename = f"saturation_gradient_{name}.png"
        path = os.path.join(output_dir, filename)
        img = create_saturation_gradient(600, 100, hue=hue, value=1.0)
        img.save(path)
        generated_files.append(path)
        print(f"    ✓ {filename}")

    # 3. Value gradients for primary hues
    print("  - Value gradients...")
    for name, hue in hues:
        filename = f"value_gradient_{name}.png"
        path = os.path.join(output_dir, filename)
        img = create_value_gradient(600, 100, hue=hue, saturation=1.0)
        img.save(path)
        generated_files.append(path)
        print(f"    ✓ {filename}")

    # 4. Grayscale gradient
    print("  - Grayscale gradient...")
    filename = "grayscale_gradient.png"
    path = os.path.join(output_dir, filename)
    img = create_linear_gradient(600, 100, (0, 0, 0), (255, 255, 255))
    img.save(path)
    generated_files.append(path)
    print(f"    ✓ {filename}")

    # 5. Radial gradients
    print("  - Radial gradients...")
    radial_tests = [
        ("radial_white_red", (255, 255, 255), (255, 0, 0)),
        ("radial_black_yellow", (0, 0, 0), (255, 255, 0)),
        ("radial_blue_green", (0, 0, 255), (0, 255, 0)),
    ]
    for name, center, edge in radial_tests:
        filename = f"{name}.png"
        path = os.path.join(output_dir, filename)
        img = create_radial_gradient(400, 400, center, edge)
        img.save(path)
        generated_files.append(path)
        print(f"    ✓ {filename}")

    # 6. Color patches
    print("  - Color patches...")
    filename = "color_patches.png"
    path = os.path.join(output_dir, filename)
    img = create_color_patches(patch_size=80, margin=10)
    img.save(path)
    generated_files.append(path)
    print(f"    ✓ {filename}")

    # 7. Skin tone patches
    print("  - Skin tone patches...")
    filename = "skin_tones.png"
    path = os.path.join(output_dir, filename)
    img = create_skin_tone_patches(patch_size=80, margin=10)
    img.save(path)
    generated_files.append(path)
    print(f"    ✓ {filename}")

    # 8. Laser palette
    print("  - MOPA laser palette...")
    filename = "laser_palette.png"
    path = os.path.join(output_dir, filename)
    img = create_laser_palette_test(patch_size=80, margin=5)
    img.save(path)
    generated_files.append(path)
    print(f"    ✓ {filename}")

    # 9. HSV color space
    print("  - HSV color space...")
    filename = "hsv_colorspace.png"
    path = os.path.join(output_dir, filename)
    img = create_hsv_color_space(size=500)
    img.save(path)
    generated_files.append(path)
    print(f"    ✓ {filename}")

    # 10. Smooth gradient test
    print("  - Smooth gradient test...")
    filename = "smooth_gradients.png"
    path = os.path.join(output_dir, filename)
    img = create_smooth_gradient_test(width=600, height=80)
    img.save(path)
    generated_files.append(path)
    print(f"    ✓ {filename}")

    print(f"\n✅ Generated {len(generated_files)} test patterns in '{output_dir}/'")
    return generated_files


if __name__ == "__main__":
    import sys

    output_dir = "test_patterns"
    if len(sys.argv) > 1:
        output_dir = sys.argv[1]

    files = generate_all_test_patterns(output_dir)

    print("\nTest patterns ready for processing!")
    print("\nNext steps:")
    print("  1. Run run_comparison_tests.py to process all patterns")
    print("  2. Compare original vs. Retinex-enhanced outputs")
    print("  3. Load the SVG files into LightBurn for laser engraving")
