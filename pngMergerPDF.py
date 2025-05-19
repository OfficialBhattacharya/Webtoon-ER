import os
import sys
from PIL import Image

def merge_png_to_pdf(folder_path, output_pdf_path):
    # List all PNG files in the folder and sort them by their names
    png_files = sorted([f for f in os.listdir(folder_path) if f.endswith('.png')])
    
    if not png_files:
        print(f"No PNG images found in the directory '{folder_path}'.")
        return

    # Open the first image to get the size and mode
    first_image_path = os.path.join(folder_path, png_files[0])
    first_image = Image.open(first_image_path)
    
    # Create a list to store all image objects
    image_list = [Image.open(os.path.join(folder_path, f)).convert('RGB') for f in png_files]

    # Save the images as a PDF
    output_pdf_path = os.path.join(folder_path, output_pdf_path)
    image_list[0].save(output_pdf_path, save_all=True, append_images=image_list[1:])
    
    print(f'PDF created successfully at {output_pdf_path}')

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python script.py <folder_path> <output_pdf_name>")
        sys.exit(1)

    folder_path = sys.argv[1].strip()
    output_pdf_name = sys.argv[2].strip() + ".pdf"
    
    merge_png_to_pdf(folder_path, output_pdf_name)
