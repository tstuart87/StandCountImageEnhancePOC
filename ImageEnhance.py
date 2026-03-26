import os
from PIL import Image, ImageEnhance
import numpy as np

INPUT_DIR = "Input"
OUTPUT_DIR = "Output"

os.makedirs(OUTPUT_DIR, exist_ok=True)

def enhance_image(img):
    # Increase contrast
    contrast = ImageEnhance.Contrast(img).enhance(2.3)

    # Increase saturation
    color = ImageEnhance.Color(contrast).enhance(2.4)

    return color

def highlight_edges(img):
    # Convert image to NumPy
    arr = np.array(img)
    h, w, _ = arr.shape # shape is a numpy function

    # Copy for drawing red edges
    output = arr.copy()

    # Thresholds (tweak these for your field conditions)
    for y in range(1, h - 1):
        for x in range(1, w - 1):

            r, g, b = [int(v) for v in arr[y, x]]

            # plant pixel definition (green dominant)
            plant = g > (r + 15) and g > (b + 15)

            if not plant:
                continue

            # check 4 neighbors for soil
            neighbors = [
                [int(v) for v in arr[y - 1, x]],
                [int(v) for v in arr[y + 1, x]],
                [int(v) for v in arr[y, x - 1]],
                [int(v) for v in arr[y, x + 1]],
            ]

            for nr, ng, nb in neighbors:
                # soil pixel: darker + not green

                # if soil == BROWN
                # soil = (ng < 80 and nb < 80 and r < 120)

                # if soil == GREY
                is_grayscale = abs(r - g) < 5 and abs(g - b) < 5
                is_dark = r < 150
                soil = is_grayscale and is_dark

                if soil:
                    output[y, x] = [255, 0, 0]  # red edge pixel
                    break

    # convert back to Pillow image
    return Image.fromarray(output)

def grayscale_soil_keep_plants(img):
    arr = np.array(img)
    h, w, _ = arr.shape

    # Copy output buffer
    out = arr.copy()

    threshold = 20

    for y in range(h):
        for x in range(w):
            r, g, b = [int(v) for v in arr[y, x]]

            # Is this pixel a plant?
            is_plant = g > r + threshold and g > b + threshold

            if not is_plant:
                # Convert soil pixel to grayscale
                gray = int(0.299 * r + 0.587 * g + 0.114 * b)
                out[y, x] = [gray, gray, gray]
                # Plant pixels left untouched

    return Image.fromarray(out)

def plants_to_red(img, threshold=10):
    # Convert green pixels to shades of red.
    arr = np.array(img)
    h, w, _ = arr.shape
    out = arr.copy()

    for y in range(h):
        for x in range(w):
            r, g, b = [int(v) for v in arr[y, x]]

            # plant detection: green dominant
            is_plant = g > r + threshold and g > b + threshold

            if is_plant:
                # keep brightness but convert to red
                brightness = int((r + g + b) / 3)

                # shade of red that matches brightness level
                shade = min(255, brightness + 40)

                out[y, x] = [shade, 0, 0]

    return Image.fromarray(out)

def white_to_blue(img, tolerance=40):
    # Converts white or near-white pixels into vibrant blue.
    # 'tolerance' controls how close to white a pixel must be.
    arr = np.array(img)
    out = arr.copy()

    for y in range(arr.shape[0]):
        for x in range(arr.shape[1]):
            r, g, b = [int(v) for v in arr[y, x]]

            # pixels are white if all channels are high
            if r > 255 - tolerance and g > 255 - tolerance and b > 255 - tolerance:

                # BLUE
                # out[y, x] = [30, 220, 255]

                # PINK
                # out[y, x] = [255, 75, 230]

                # YELLOW
                out[y, x] = [240, 255, 80]

    return Image.fromarray(out)


def process_all_images():
    for filename in os.listdir(INPUT_DIR):
        if not filename.lower().endswith((".jpg", ".png", ".jpeg", ".tiff")):
            continue

        path = os.path.join(INPUT_DIR, filename)
        img = Image.open(path).convert("RGB")

        # enhance contrast + color
        highContrastIMG = enhance_image(img)

        # change soil to grayscale
        graySoilIMG = grayscale_soil_keep_plants(highContrastIMG)

        # convert green in plants to red
        redPlantIMG = plants_to_red(graySoilIMG)

        # highlight plant edges
        # outlined = highlight_edges(redPlantIMG)

        blueEdgedPlantIMG = white_to_blue(redPlantIMG)

        # Save finished file
        out_path = os.path.join(OUTPUT_DIR, filename)
        # outlined.save(out_path)
        blueEdgedPlantIMG.save(out_path)

        print(f"Processed: {filename}")

if __name__ == "__main__":
    process_all_images()
