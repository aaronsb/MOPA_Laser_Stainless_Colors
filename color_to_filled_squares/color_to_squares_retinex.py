import sys
import os
from PIL import Image, ImageFilter
import colorsys
import numpy as np
from scipy.ndimage import gaussian_filter

# --- Configuration ---
# Target colors and their corresponding RGB values for the laser
# These are the physical colors achievable with the MOPA laser settings
TARGET_COLORS = {
    "Black":   (0, 0, 0),
    "White":   (180, 180, 180),  # Light gray
    "Gray":    (128, 128, 128),
    "Purple":  (128, 0, 128),
    "Blue":    (0, 0, 255),
    "Green":   (0, 224, 0),
    "Yellow":  (208, 208, 0),
    "Orange":  (255, 128, 0),
    "Red":     (255, 0, 0),
    "Brown":   (139, 69, 19),
}

# Convert to numpy array for faster processing
PALETTE = np.array(list(TARGET_COLORS.values()), dtype=np.float32)
COLOR_NAMES = list(TARGET_COLORS.keys())

def retinex_enhancement(img_array, sigma_list=[15, 80, 250]):
    """
    Apply Multi-Scale Retinex (MSR) to enhance local color contrasts.
    This separates illumination from reflectance, improving color perception.

    Args:
        img_array: numpy array of shape (H, W, 3) with float values 0-255
        sigma_list: list of Gaussian kernel sizes for multi-scale processing

    Returns:
        Enhanced image array (H, W, 3) with improved color contrast
    """
    img_float = img_array.astype(np.float32) + 1.0  # Add 1 to avoid log(0)

    retinex = np.zeros_like(img_float)

    # Apply multi-scale Retinex
    for sigma in sigma_list:
        # Apply Gaussian blur to each channel
        for i in range(3):
            blurred = gaussian_filter(img_float[:, :, i], sigma=sigma)
            # Compute log ratio (reflectance / illumination)
            retinex[:, :, i] += np.log10(img_float[:, :, i]) - np.log10(blurred + 1.0)

    # Average across scales
    retinex = retinex / len(sigma_list)

    # Normalize to 0-255 range
    for i in range(3):
        channel = retinex[:, :, i]
        min_val, max_val = channel.min(), channel.max()
        if max_val > min_val:
            retinex[:, :, i] = 255 * (channel - min_val) / (max_val - min_val)
        else:
            retinex[:, :, i] = 128

    return np.clip(retinex, 0, 255).astype(np.uint8)

def enhance_color_differential(img_array, strength=1.5):
    """
    Enhance color differentials to maximize perceptual separation.
    Increases saturation while preserving hue relationships.

    Args:
        img_array: numpy array (H, W, 3)
        strength: enhancement factor (1.0 = no change, >1.0 = more saturation)

    Returns:
        Enhanced image array
    """
    img_hsv = np.zeros_like(img_array, dtype=np.float32)

    # Convert to HSV
    for y in range(img_array.shape[0]):
        for x in range(img_array.shape[1]):
            r, g, b = img_array[y, x] / 255.0
            h, s, v = colorsys.rgb_to_hsv(r, g, b)

            # Enhance saturation with adaptive strength based on value
            # Don't oversaturate very dark or very bright pixels
            adaptive_strength = strength * (1.0 - abs(v - 0.5) * 0.5)
            s = min(1.0, s * adaptive_strength)

            # Convert back to RGB
            r, g, b = colorsys.hsv_to_rgb(h, s, v)
            img_hsv[y, x] = [r * 255, g * 255, b * 255]

    return np.clip(img_hsv, 0, 255).astype(np.uint8)

def find_closest_palette_color(pixel):
    """
    Find the closest color in the target palette using perceptual color distance.

    Args:
        pixel: RGB tuple (3,) as numpy array

    Returns:
        Index of closest palette color
    """
    # Use weighted Euclidean distance in RGB space
    # Weight green more as human vision is more sensitive to it
    weights = np.array([0.299, 0.587, 0.114])  # Luminance weights

    diff = PALETTE - pixel
    distances = np.sqrt(np.sum((diff ** 2) * weights, axis=1))

    return np.argmin(distances)

def floyd_steinberg_dithering(img_array):
    """
    Apply Floyd-Steinberg error diffusion dithering with the target palette.
    This creates spatial color mixing that expands the effective gamut.

    Args:
        img_array: numpy array (H, W, 3) of the input image

    Returns:
        Tuple of (output_array, color_indices) where:
            output_array: dithered image as (H, W, 3)
            color_indices: (H, W) array of palette indices for SVG generation
    """
    height, width = img_array.shape[:2]

    # Work with float for error accumulation
    working_image = img_array.astype(np.float32).copy()
    output_indices = np.zeros((height, width), dtype=np.int32)
    output_image = np.zeros_like(img_array)

    # Floyd-Steinberg error diffusion matrix
    # Distributes error to:  [ ] [X] [ ]
    #                        [ ] [7] [5] [3] [1]  (divided by 16)

    for y in range(height):
        for x in range(width):
            old_pixel = working_image[y, x]

            # Find closest palette color
            palette_idx = find_closest_palette_color(old_pixel)
            new_pixel = PALETTE[palette_idx]

            output_indices[y, x] = palette_idx
            output_image[y, x] = new_pixel

            # Calculate quantization error
            quant_error = old_pixel - new_pixel

            # Distribute error to neighboring pixels (Floyd-Steinberg)
            if x + 1 < width:
                working_image[y, x + 1] += quant_error * 7/16

            if y + 1 < height:
                if x > 0:
                    working_image[y + 1, x - 1] += quant_error * 3/16
                working_image[y + 1, x] += quant_error * 5/16
                if x + 1 < width:
                    working_image[y + 1, x + 1] += quant_error * 1/16

    return output_image, output_indices

def atkinson_dithering(img_array):
    """
    Apply Atkinson dithering - produces sharper results with less error diffusion.
    Good for preserving fine details while still achieving color mixing.

    Error distribution pattern:
        [ ] [X] [1] [1]
        [1] [1] [1] [ ]
        [ ] [1] [ ] [ ]  (all divided by 8)
    """
    height, width = img_array.shape[:2]
    working_image = img_array.astype(np.float32).copy()
    output_indices = np.zeros((height, width), dtype=np.int32)
    output_image = np.zeros_like(img_array)

    for y in range(height):
        for x in range(width):
            old_pixel = working_image[y, x]
            palette_idx = find_closest_palette_color(old_pixel)
            new_pixel = PALETTE[palette_idx]

            output_indices[y, x] = palette_idx
            output_image[y, x] = new_pixel

            quant_error = old_pixel - new_pixel

            # Atkinson dithering pattern - distributes 6/8 of error
            # (keeps images slightly brighter)
            if x + 1 < width:
                working_image[y, x + 1] += quant_error * 1/8
            if x + 2 < width:
                working_image[y, x + 2] += quant_error * 1/8

            if y + 1 < height:
                if x > 0:
                    working_image[y + 1, x - 1] += quant_error * 1/8
                working_image[y + 1, x] += quant_error * 1/8
                if x + 1 < width:
                    working_image[y + 1, x + 1] += quant_error * 1/8

            if y + 2 < height:
                working_image[y + 2, x] += quant_error * 1/8

    return output_image, output_indices

def generate_pixel_svg_retinex(input_image_path, output_svg_path, square_size_mm=0.25,
                                apply_retinex=True, enhance_saturation=True,
                                dithering_method='floyd-steinberg'):
    """
    Loads an image, applies Retinex enhancement and spatial dithering,
    then generates an SVG file with expanded color gamut.

    Args:
        input_image_path (str): Path to the source image file.
        output_svg_path (str): Path where the SVG file will be saved.
        square_size_mm (float): The size of each square in millimeters.
        apply_retinex (bool): Apply Multi-Scale Retinex enhancement
        enhance_saturation (bool): Enhance color saturation
        dithering_method (str): 'floyd-steinberg', 'atkinson', or 'none'
    """
    try:
        img = Image.open(input_image_path).convert("RGB")
    except FileNotFoundError:
        print(f"Error: Input file not found at '{input_image_path}'")
        return
    except Exception as e:
        print(f"Error loading image: {e}")
        return

    width, height = img.size
    print(f"Processing image: {width}x{height} pixels.")

    # Convert to numpy array for processing
    img_array = np.array(img)

    # Apply Retinex enhancement
    if apply_retinex:
        print("Applying Multi-Scale Retinex enhancement...")
        img_array = retinex_enhancement(img_array)

    # Enhance color differentials
    if enhance_saturation:
        print("Enhancing color saturation...")
        img_array = enhance_color_differential(img_array, strength=1.5)

    # Apply dithering
    if dithering_method == 'floyd-steinberg':
        print("Applying Floyd-Steinberg dithering...")
        output_img, color_indices = floyd_steinberg_dithering(img_array)
    elif dithering_method == 'atkinson':
        print("Applying Atkinson dithering...")
        output_img, color_indices = atkinson_dithering(img_array)
    else:
        print("No dithering - using nearest color matching...")
        color_indices = np.zeros((height, width), dtype=np.int32)
        output_img = np.zeros_like(img_array)
        for y in range(height):
            for x in range(width):
                idx = find_closest_palette_color(img_array[y, x])
                color_indices[y, x] = idx
                output_img[y, x] = PALETTE[idx]

    # Generate SVG
    svg_width_mm = width * square_size_mm
    svg_height_mm = height * square_size_mm
    STROKE_WIDTH_MM = 0.01

    print(f"Output SVG size: {svg_width_mm:.2f}mm x {svg_height_mm:.2f}mm.")
    print("Generating SVG...")

    svg_content = []
    svg_content.append(f"""<svg width="{svg_width_mm}mm" height="{svg_height_mm}mm" viewBox="0 0 {svg_width_mm} {svg_height_mm}" xmlns="http://www.w3.org/2000/svg">""")

    # Add comment with processing info
    svg_content.append(f"<!-- Generated with Retinex-enhanced spatial dithering -->")
    svg_content.append(f"<!-- Retinex: {apply_retinex}, Saturation: {enhance_saturation}, Dithering: {dithering_method} -->")

    # Generate rectangles
    for y in range(height):
        for x in range(width):
            palette_idx = color_indices[y, x]
            color_name = COLOR_NAMES[palette_idx]
            r, g, b = PALETTE[palette_idx].astype(int)
            color_hex = f"#{r:02X}{g:02X}{b:02X}"

            x_mm = x * square_size_mm
            y_mm = y * square_size_mm

            rect = (
                f'<rect x="{x_mm:.4f}" y="{y_mm:.4f}" '
                f'width="{square_size_mm:.4f}" height="{square_size_mm:.4f}" '
                f'fill="{color_hex}" stroke="{color_hex}" '
                f'stroke-width="{STROKE_WIDTH_MM:.4f}" />'
            )
            svg_content.append(rect)

    svg_content.append("</svg>")

    # Write SVG file
    try:
        with open(output_svg_path, "w") as f:
            f.write("\n".join(svg_content))
        print(f"Success! SVG saved to '{output_svg_path}'")

        # Also save a preview PNG
        preview_path = output_svg_path.replace('.svg', '_preview.png')
        Image.fromarray(output_img).save(preview_path)
        print(f"Preview image saved to '{preview_path}'")

    except Exception as e:
        print(f"Error writing output files: {e}")

if __name__ == "__main__":
    INPUT_FILE = "input.png"
    OUTPUT_FILE = "output_retinex.svg"
    square_mm = 0.25

    # Parse command line arguments
    if len(sys.argv) > 1:
        INPUT_FILE = sys.argv[1]

    if len(sys.argv) > 2:
        OUTPUT_FILE = sys.argv[2]

    if len(sys.argv) > 3:
        try:
            square_mm = float(sys.argv[3])
        except ValueError:
            print("Warning: Square size must be a number. Using default 0.25mm.")

    # Optional: dithering method argument
    dithering = 'floyd-steinberg'
    if len(sys.argv) > 4:
        if sys.argv[4] in ['floyd-steinberg', 'atkinson', 'none']:
            dithering = sys.argv[4]

    print(f"Using input: {INPUT_FILE}, output: {OUTPUT_FILE}, size: {square_mm}mm")
    print(f"Dithering method: {dithering}")

    generate_pixel_svg_retinex(
        INPUT_FILE,
        OUTPUT_FILE,
        square_mm,
        apply_retinex=True,
        enhance_saturation=True,
        dithering_method=dithering
    )
