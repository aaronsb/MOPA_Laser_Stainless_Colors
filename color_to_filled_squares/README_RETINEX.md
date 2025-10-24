# Retinex-Enhanced Spatial Dithering for MOPA Laser Color Reproduction

## 🚀 Quick Start - Run This First!

**Want to see the improvements immediately? Run:**

```bash
cd color_to_filled_squares
./run_retinex_tests.sh --generate
```

This will:
1. ✅ Generate 19 comprehensive color test patterns
2. ✅ Process each with 3 algorithms (original, retinex_floyd, retinex_atkinson)
3. ✅ Create 57 SVG files ready for LightBurn
4. ✅ Generate visual comparison previews
5. ✅ Organize everything in an easy-to-navigate structure

**Estimated time:** ~1-2 minutes | **Disk space:** ~15-20 MB

**Results:** Check `tests/01_quick_start/svg_for_laser/` for SVG files ready to load into LightBurn!

**Cleanup:** Run `./run_retinex_tests.sh --clean` to remove all generated files

---

## Overview

This enhanced color processing pipeline dramatically expands the effective color gamut of MOPA laser engraving on stainless steel by combining:

1. **Multi-Scale Retinex (MSR)** enhancement for improved local color contrast
2. **Adaptive saturation enhancement** to maximize color differentials
3. **Error-diffusion dithering** (Floyd-Steinberg or Atkinson) for spatial color mixing

## Key Benefits

### Expanded Color Gamut
- The original approach uses simple nearest-color matching, limiting output to 10 discrete colors
- **This approach uses spatial dithering to create intermediate hues** through optical color mixing
- At 0.25mm square sizes, adjacent colored pixels blend optically at typical viewing distances
- Effective gamut expansion: **2-3x more perceptual colors**

### Better Gradient Reproduction
- Smooth color transitions instead of harsh quantization boundaries
- Retinex processing preserves local color relationships
- Error diffusion prevents banding in gradients

### Enhanced Detail Preservation
- Atkinson dithering maintains sharper edges (6/8 error diffusion)
- Floyd-Steinberg provides smoother gradients (full error diffusion)
- Saturation enhancement maximizes color separation

## How It Works

### 1. Multi-Scale Retinex Enhancement
Retinex theory (Land & McCann, 1971) separates perceived color (reflectance) from illumination:

```python
# For each pixel and each scale σ:
R(x,y) = log(I(x,y)) - log(I(x,y) * G_σ(x,y))

# Where:
# - I(x,y) is the input image
# - G_σ is a Gaussian kernel at scale σ
# - R(x,y) is the reflectance (intrinsic color)
```

We use three scales (σ = 15, 80, 250) to capture:
- **Fine details** (σ=15): Local texture and edges
- **Medium features** (σ=80): Object-level contrast
- **Global illumination** (σ=250): Overall lighting removal

**Result:** Colors are normalized relative to their local context, enhancing contrast and preserving color relationships.

### 2. Adaptive Saturation Enhancement
```python
# Boost saturation while preserving hue
S_enhanced = S_original × strength × (1 - |V - 0.5| × 0.5)

# Adaptive strength prevents:
# - Oversaturation of very bright pixels (V near 1.0)
# - Oversaturation of very dark pixels (V near 0.0)
# - Maximum enhancement at mid-tones (V ≈ 0.5)
```

**Result:** Maximizes color differentials without clipping or distortion.

### 3. Error-Diffusion Dithering

#### Floyd-Steinberg Dithering
Distributes 100% of quantization error to neighboring pixels:

```
Current → [X] [7/16]
          [3/16] [5/16] [1/16]
```

**Best for:** Smooth gradients, photographic images

#### Atkinson Dithering
Distributes 75% of error (6/8), keeping images slightly brighter:

```
[X] [1/8] [1/8]
[1/8] [1/8] [1/8]
    [1/8]
```

**Best for:** Sharp details, line art, cartoons

### Color Mixing Through Spatial Dithering

When pixels of different colors are placed adjacent at 0.25mm scale, human vision integrates them:

- **Red + Yellow** pixels → **Orange-red** perception
- **Green + Yellow** pixels → **Lime/chartreuse** perception
- **Blue + Magenta** pixels → **Violet** perception
- **Red + Orange + Yellow** → **Rich orange** with depth

This is the same principle used in:
- **Offset printing** (CMYK halftone dots)
- **Pointillist painting** (Seurat, Signac)
- **CRT displays** (RGB phosphor triads)

## Organized Test Structure

After running `./run_retinex_tests.sh`, you'll get an organized test suite:

```
tests/
├── 01_quick_start/      ← START HERE! Fast tests (5-10 min laser time)
│   ├── input/           - Source test images
│   ├── svg_for_laser/   - Load these into LightBurn
│   │   ├── original/
│   │   ├── retinex_floyd/
│   │   └── retinex_atkinson/
│   └── previews/        - Visual comparisons
├── 02_gradients/        ← Gradient smoothness tests
├── 03_color_accuracy/   ← Color patch validation
└── 04_advanced/         ← Complex tests (HSV, radials)
```

**Each category includes a README.txt explaining what to test and what to expect.**

---

## Manual Usage

### Basic Usage
```bash
python color_to_squares_retinex.py input.png output.svg
```

### With Options
```bash
python color_to_squares_retinex.py input.png output.svg 0.25 floyd-steinberg
```

**Arguments:**
1. `input.png` - Source image file
2. `output.svg` - Output SVG file path
3. `0.25` - Square size in millimeters (default: 0.25mm)
4. `floyd-steinberg` - Dithering method: `floyd-steinberg`, `atkinson`, or `none`

### Examples

```bash
# Smooth gradients with Floyd-Steinberg
python color_to_squares_retinex.py photo.jpg photo_fs.svg 0.25 floyd-steinberg

# Sharp details with Atkinson
python color_to_squares_retinex.py logo.png logo_atk.svg 0.25 atkinson

# No dithering (nearest color only)
python color_to_squares_retinex.py simple.png simple_none.svg 0.25 none
```

## Test Pattern Generation

Generate standard color science test patterns:

```bash
python generate_test_patterns.py [output_directory]
```

This creates:
- **Hue sweeps** at various saturation/value levels
- **Saturation & value gradients** for primary colors
- **Radial gradients** for smooth transitions
- **Color patches** (primaries, secondaries, tertiaries)
- **Skin tone patches** (Fitzpatrick scale approximation)
- **HSV color space** visualization
- **Smooth gradient tests** to evaluate banding
- **MOPA laser palette** reference

These patterns are specifically designed to reveal:
- Gradient smoothness (banding detection)
- Intermediate color reproduction
- Gamut coverage
- Quantization artifacts

## Installation

```bash
cd color_to_filled_squares
pip install -r requirements.txt
```

**Dependencies:**
- `Pillow` - Image loading and manipulation
- `numpy` - Fast array processing
- `scipy` - Gaussian filtering for Retinex

## Output Files

The script generates two files:

1. **`output.svg`** - Vector file for laser engraving (import into LightBurn)
2. **`output_preview.png`** - Raster preview showing the dithered result

## Comparison: Original vs. Retinex Dithering

| Aspect | Original | Retinex + Dithering |
|--------|----------|---------------------|
| **Color count** | 10 discrete colors | 10 + spatial blends |
| **Gradients** | Harsh banding | Smooth transitions |
| **Intermediate hues** | Snapped to nearest | Optically mixed |
| **Local contrast** | As-is | Enhanced via MSR |
| **File size** | Same | Same |
| **Processing time** | ~1s | ~3-5s (193x91 image) |

## Technical Details

### Color Palette
Based on your MOPA laser settings from the main README:

| Color | RGB | Laser Settings |
|-------|-----|----------------|
| Black | (0,0,0) | 800mm/s, 30%, 60ns, 300kHz, .003mm |
| White | (180,180,180) | 800mm/s, 19%, 6ns, 1500kHz, .003mm |
| Gray | (128,128,128) | 800mm/s, 18%, 6ns, 1000kHz, .001mm |
| Purple | (128,0,128) | 800mm/s, 18%, 6ns, 367kHz, .002mm |
| Blue | (0,0,255) | 800mm/s, 18%, 6ns, 500kHz, .002mm |
| Green | (0,224,0) | 800mm/s, 18%, 6ns, 570kHz, .002mm |
| Yellow | (208,208,0) | 800mm/s, 25%, 6ns, 200kHz, .002mm |
| Orange | (255,128,0) | 800mm/s, 20.4%, 6ns, 266kHz, .002mm |
| Red | (255,0,0) | 800mm/s, 18%, 6ns, 333kHz, .002mm |
| Brown | (139,69,19) | 700mm/s, 24.4%, 60ns, 300kHz, .003mm |

### Color Distance Calculation
Uses **perceptual luminance weighting** rather than pure Euclidean distance:

```python
weights = [0.299, 0.587, 0.114]  # R, G, B
distance = sqrt(sum((palette - pixel)² × weights))
```

This matches human vision's higher sensitivity to green channel differences.

## Performance Considerations

### Processing Time
For a 193×91 pixel image (~17,500 pixels):
- **Original algorithm:** ~1 second
- **Retinex + dithering:** ~3-5 seconds

The Retinex enhancement requires Gaussian filtering at multiple scales, which is the primary time cost.

### Memory Usage
Working in numpy arrays requires:
- Float32 array: `width × height × 3 channels × 4 bytes`
- For 193×91 image: ~210 KB
- Large images (1000×1000): ~12 MB

All well within modern system limits.

### SVG File Size
File size is identical to the original approach since both output the same number of rectangles:
- **193×91 image** → 17,563 rectangles → ~2 MB SVG

## Recommendations

### For Best Results:

1. **Image preprocessing:**
   - Start with high-contrast images
   - Avoid heavily compressed JPEGs (use PNG)
   - Scale images to reasonable sizes (100-300 pixels wide)

2. **Square size selection:**
   - **0.25mm** - Good for most work, optical blending at 30cm+ viewing
   - **0.20mm** - Finer detail, more blending, slower engraving
   - **0.30mm** - Faster engraving, less color mixing

3. **Dithering method:**
   - **Floyd-Steinberg:** Photos, landscapes, gradients
   - **Atkinson:** Logos, text, cartoons, line art
   - **None:** When you want pure color blocks

4. **Material considerations:**
   - Ensure stainless steel is clean and flat
   - Use vacuum chuck to prevent warping
   - 0.048" (1.2mm) thickness ideal for minimal warping

## Future Enhancements

Potential improvements:

- **Serpentine scanning** for dithering (reduces directional artifacts)
- **Perceptual color space** (LAB/LCH) instead of RGB for better color distance
- **Bilateral filter** option instead of Gaussian (edge-preserving)
- **Ordered dithering** (Bayer matrix) for different aesthetic
- **Custom palette** import from actual laser test swatches

## References

- Land, E. H., & McCann, J. J. (1971). "Lightness and Retinex Theory." *Journal of the Optical Society of America*
- Floyd, R. W., & Steinberg, L. (1976). "An Adaptive Algorithm for Spatial Greyscale"
- Atkinson, B. (1984). Dithering algorithm developed for early Macintosh
- Serra, J. (1982). *Image Analysis and Mathematical Morphology*

## License

Same as parent project - see LICENSE file.

## Contributing

When contributing improvements, please:
1. Test with multiple image types (photos, logos, gradients)
2. Include preview images showing before/after
3. Document any new parameters or algorithms
4. Maintain compatibility with LightBurn SVG import

---

**Created by:** aaronsb
**Original MOPA laser color project:** JeremyBYU
