import os
import sys
from PIL import Image, ImageChops
from reportlab.lib.pagesizes import A4

def is_black_or_white_band(image, y, band_height=5):
    """
    Check if the specified horizontal band is black or white.
    """
    band = image.crop((0, y, image.width, y + band_height))
    # Create black and white images of the same size as the band to compare
    black_band = Image.new("RGB", band.size, (0, 0, 0))
    white_band = Image.new("RGB", band.size, (255, 255, 255))
    black_diff = ImageChops.difference(band, black_band)
    white_diff = ImageChops.difference(band, white_band)
    return not black_diff.getbbox() or not white_diff.getbbox()  # Return True if no difference

def slice_long_image(long_image_path, output_folder):
    # Ensure the output folder exists
    os.makedirs(output_folder, exist_ok=True)

    # Load the long image
    with Image.open(long_image_path) as long_image:
        img_width, img_height = long_image.size

        # A4 page dimensions in pixels (at 72 dpi)
        a4_width, a4_height = int(A4[0]), int(A4[1])
        min_height = a4_height  # Minimum slice height is A4

        current_height = 0
        slice_number = 0

        while current_height < img_height:
            # Start with the maximum possible slice height
            slice_height = img_height - current_height
            
            # Find the next black band if the height exceeds A4
            if slice_height > a4_height:
                for y in range(a4_height, slice_height):
                    if is_black_or_white_band(long_image, current_height + y):
                        slice_height = y
                        break

            # Ensure slice height is not less than the minimum height
            slice_height = max(slice_height, min_height)

            # Extract the slice from the long image
            with long_image.crop((0, current_height, img_width, current_height + slice_height)) as slice_image:
                slice_image_path = os.path.join(output_folder, f'slice_{slice_number:03d}.png')
                slice_image.save(slice_image_path)

            print(f'Saved {slice_image_path}')

            current_height += slice_height
            slice_number += 1

    print(f'Slicing completed. Total slices: {slice_number}')

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python script.py <long_image_path> <output_folder>")
        sys.exit(1)

    long_image_path = sys.argv[1].strip()
    output_folder = sys.argv[2].strip()
    
    slice_long_image(long_image_path, output_folder)
