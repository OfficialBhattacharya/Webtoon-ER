import os
import sys
import fitz  # PyMuPDF
from PIL import Image

def pdf_to_long_image(pdf_path, output_image_path):
    # Open the PDF file
    pdf_document = fitz.open(pdf_path)
    
    # Get the total number of pages
    num_pages = pdf_document.page_count
    
    # List to store images of all pages
    images = []

    # Iterate through each page and convert it to an image
    for i in range(num_pages):
        page = pdf_document.load_page(i)
        pix = page.get_pixmap()
        
        # Convert Pixmap to PIL Image
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        images.append(img)
    
    # Determine the total height of the final image
    total_height = sum(img.height for img in images)
    max_width = max(img.width for img in images)
    
    # Create a new blank image with the total height
    final_image = Image.new("RGB", (max_width, total_height))
    
    # Paste each page image into the final image
    y_offset = 0
    for img in images:
        final_image.paste(img, (0, y_offset))
        y_offset += img.height
    
    # Save the final image
    final_image.save(output_image_path)
    print(f'Image created successfully at {output_image_path}')

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <pdf_path>")
        sys.exit(1)

    pdf_path = sys.argv[1].strip()
    output_image_path = os.path.splitext(pdf_path)[0] + ".png"  # Change to .jpeg if needed
    
    pdf_to_long_image(pdf_path, output_image_path)
