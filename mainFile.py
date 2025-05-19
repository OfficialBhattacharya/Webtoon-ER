import os
import requests

def download_images(base_url, start_num, end_num, output_folder):
    # Ensure the output folder exists
    os.makedirs(output_folder, exist_ok=True)
    
    # Create the list of URLs
    start = int(start_num)
    end = int(end_num)
    urls = [base_url.replace('XXX', f'{i:03d}') for i in range(start, end + 1)]
    
    for url in urls:
        try:
            # Fetch the image
            response = requests.get(url)
            response.raise_for_status()  # Ensure we got a valid response
            
            # Get the image name and create the file path
            image_name = url.split('/')[-1]
            image_path = os.path.join(output_folder, image_name)
            
            # Save the image to the output folder
            with open(image_path, 'wb') as file:
                file.write(response.content)
                
            print(f'Downloaded {image_name}')
        
        except requests.RequestException as e:
            print(f'Failed to download {url}: {e}')
    
    print('Finished!')

# Example usage
base_url = 'https://official.lowee.us/manga/Mercenary-Enrollment/0000-XXX.png'
start_num = '001'
end_num = '032'
output_folder = 'Chapter0_31_168'
download_images(base_url, start_num, end_num, output_folder)

import os
import sys
import requests
import sys
import fitz  # PyMuPDF
from PIL import Image, ImageChops
from reportlab.lib.pagesizes import A4


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


def download_images(base_url, start_num, end_num, output_folder):
    # Ensure the output folder exists
    os.makedirs(output_folder, exist_ok=True)
    
    # Create the list of URLs
    start = int(start_num)
    end = int(end_num)
    urls = [base_url.replace('XXX', f'{i:03d}') for i in range(start, end + 1)]
    
    for url in urls:
        try:
            # Fetch the image
            response = requests.get(url)
            response.raise_for_status()  # Ensure we got a valid response
            
            # Get the image name and create the file path
            image_name = url.split('/')[-1]
            image_path = os.path.join(output_folder, image_name)
            
            # Save the image to the output folder
            with open(image_path, 'wb') as file:
                file.write(response.content)
                
            print(f'Downloaded {image_name}')
        
        except requests.RequestException as e:
            print(f'Failed to download {url}: {e}')
    
    print('Finished!')


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



# if __name__ == "__main__":
#     if len(sys.argv) != 5:
#         print("Usage: python script.py <base_url> <start_num> <end_num> <output_folder>")
#         sys.exit(1)

#     base_url = sys.argv[1]
#     start_num = sys.argv[2]
#     end_num = sys.argv[3]
#     output_folder = sys.argv[4]

#     download_images(base_url, start_num, end_num, output_folder)

# python webtoonDownloader.py "https://official.lowee.us/manga/Mercenary-Enrollment/0000-XXX.png" "001" "121" "E:\BookClub\Webtoon\TeenageMercenary\RawChapters\Chapter0"


# if __name__ == "__main__":
#     if len(sys.argv) != 3:
#         print("Usage: python script.py <folder_path> <output_pdf_name>")
#         sys.exit(1)

#     folder_path = sys.argv[1].strip()
#     output_pdf_name = sys.argv[2].strip() + ".pdf"
    
#     merge_png_to_pdf(folder_path, output_pdf_name)
    
# python pngMergerPDF.py "E:\BookClub\Webtoon\TeenageMercenary\RawChapters\Chapter0" "Chapter0_Merged"


# if __name__ == "__main__":
#     if len(sys.argv) != 2:
#         print("Usage: python script.py <pdf_path>")
#         sys.exit(1)

#     pdf_path = sys.argv[1].strip()
#     output_image_path = os.path.splitext(pdf_path)[0] + ".png"  # Change to .jpeg if needed
    
#     pdf_to_long_image(pdf_path, output_image_path)

# python pdfToLongPNG.py "E:\BookClub\Webtoon\TeenageMercenary\RawChapters\MergedChapters_0_10\Chapter0_Merged.pdf"


# if __name__ == "__main__":
#     if len(sys.argv) != 3:
#         print("Usage: python script.py <long_image_path> <output_folder>")
#         sys.exit(1)

#     long_image_path = sys.argv[1].strip()
#     output_folder = sys.argv[2].strip()
    
#     slice_long_image(long_image_path, output_folder)
    
# python pngFormatter.py "E:\BookClub\Webtoon\TeenageMercenary\longPNGs_Step2\Chapter0_Merged.png" "E:\BookClub\Webtoon\TeenageMercenary\FormattedPNG"