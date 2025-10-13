import sys
import os
from PIL import Image
import colorsys

# --- Configuration ---
# Target colors and their corresponding Hues (0-360 degrees) for the quantization step.
# These hues are used to find the closest match to the input pixel's hue.
TARGET_COLORS = {
    # HEX: HUE (0-360)
    "#FF0000": 0,    # Red
    "#FF8000": 30,   # Orange (Approx)
    "#D0D000": 60,   # Yellow/Olive (Approx)
    "#00E000": 120,  # Green
    "#0000FF": 240,  # Blue
    "#FF00FF": 300,  # Magenta
}

def get_closest_color(r, g, b):
    """
    Determines the output color based on the input pixel's value (luminance) and hue.
    """
    # 1. Calculate Value (V) for thresholding (using max component for simplicity)
    V = max(r, g, b)

    # 2. Apply Luminance Threshold Rules
    if V < 25:
        return "#000000"  # Black
    
    #if (V > 200):
    #    return "#B4B4B4"  # Light Gray

    # 3. Apply Hue Matching Rule (between 25 and 200)
    
    # Normalize RGB to 0-1 range for colorsys
    r_norm, g_norm, b_norm = r / 255.0, g / 255.0, b / 255.0
    
    # Convert RGB to HSV. colorsys hue is 0-1, so multiply by 360
    h_float, s_float, v_float = colorsys.rgb_to_hsv(r_norm, g_norm, b_norm)
    pixel_hue = h_float * 360

    # Ensure the pixel has enough saturation/value to be considered a 'color'
    # If the pixel is too grayish or dark, the hue is meaningless.
    # We proceed with hue matching only if saturation/value is decent.
    if s_float < 0.45 or v_float < 0.15:
         # If not colorful enough, treat it as a shade of gray based on its value
         return "#B4B4B4" if v_float > 0.5 else "#000000"
         
    
    min_diff = 360
    closest_hex = ""

    # Iterate through target hues to find the minimum angular difference
    for hex_code, target_hue in TARGET_COLORS.items():
        # Calculate the angular difference, handling the wrap-around at 0/360 degrees
        diff = abs(pixel_hue - target_hue)
        
        # Check the shortest path around the circle (e.g., 350 vs 10 is 20, not 340)
        angular_diff = min(diff, 360 - diff)
        
        if angular_diff < min_diff:
            min_diff = angular_diff
            closest_hex = hex_code
            
    return closest_hex

def generate_pixel_svg(input_image_path, output_svg_path, square_size_mm=0.25):
    """
    Loads an image, processes pixels, and generates an SVG file.
    
    Args:
        input_image_path (str): Path to the source image file.
        output_svg_path (str): Path where the SVG file will be saved.
        square_size_mm (float): The size of each square in millimeters.
    """
    try:
        # Load the image and convert to RGB (to ensure consistent 3-channel access)
        img = Image.open(input_image_path).convert("RGB")
    except FileNotFoundError:
        print(f"Error: Input file not found at '{input_image_path}'")
        return
    except Exception as e:
        print(f"Error loading image: {e}")
        return

    width, height = img.size
    
    # Calculate the total SVG dimensions in millimeters
    svg_width_mm = width * square_size_mm
    svg_height_mm = height * square_size_mm
    
    # Constants for the SVG output
    STROKE_WIDTH_MM = 0.01

    print(f"Processing image: {width}x{height} pixels.")
    print(f"Output SVG size: {svg_width_mm:.2f}mm x {svg_height_mm:.2f}mm.")
    
    svg_content = []

    # 1. SVG Header
    svg_content.append(f"""<svg width="{svg_width_mm}mm" height="{svg_height_mm}mm" viewBox="0 0 {svg_width_mm} {svg_height_mm}" xmlns="http://www.w3.org/2000/svg">""")
    
    # 2. Generate Rectangles
    # Iterate over all pixels
    for y in range(height):
        for x in range(width):
            # Get RGB tuple for the current pixel
            r, g, b = img.getpixel((x, y))
            
            # Determine the color based on the rules
            color = get_closest_color(r, g, b)
            
            # Calculate the position of the square in millimeters
            x_mm = x * square_size_mm
            y_mm = y * square_size_mm
            
            # Generate the SVG <rect> element
            rect = (
                f'<rect x="{x_mm:.4f}" y="{y_mm:.4f}" width="{square_size_mm:.4f}" height="{square_size_mm:.4f}" '
                f'fill="{color}" stroke="{color}" stroke-width="{STROKE_WIDTH_MM:.4f}" />'
            )
            svg_content.append(rect)
            
    # 3. SVG Footer
    svg_content.append("</svg>")
    
    # Write the content to the file
    try:
        with open(output_svg_path, "w") as f:
            f.write("\n".join(svg_content))
        print(f"Success! SVG saved to '{output_svg_path}'")
    except Exception as e:
        print(f"Error writing SVG file: {e}")

if __name__ == "__main__":
    # --- Example Usage ---
    # The image path is hardcoded for demonstration. 
    # Replace 'input.png' with the actual path to your image file.
    # You can pass the square size as an argument if you want to change the default.
    
    INPUT_FILE = "input.png"
    OUTPUT_FILE = "output.svg"
    
    # Default size is 0.25mm
    square_mm = 0.25

    # Check command line arguments for input file, output file, and size
    if len(sys.argv) > 1:
        INPUT_FILE = sys.argv[1]
    
    if len(sys.argv) > 2:
        OUTPUT_FILE = sys.argv[2]

    if len(sys.argv) > 3:
        try:
            square_mm = float(sys.argv[3])
        except ValueError:
            print("Warning: Square size must be a number. Using default 0.25mm.")

    print(f"Using input: {INPUT_FILE}, output: {OUTPUT_FILE}, size: {square_mm}mm")
    
    generate_pixel_svg(INPUT_FILE, OUTPUT_FILE, square_mm)
