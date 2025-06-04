import os
import sys
import requests
import fitz  # PyMuPDF
from PIL import Image, ImageChops
from reportlab.lib.pagesizes import A4
import shutil

class WebtoonProcessor:
    def __init__(self, base_folder):
        """
        Initialize the WebtoonProcessor with a base folder for all operations.
        
        Args:
            base_folder: The main folder to store all processed files
        """
        self.base_folder = base_folder
        self.raw_folder = os.path.join(base_folder, "RawChapters")
        self.pdf_folder = os.path.join(base_folder, "PDFs")
        self.long_png_folder = os.path.join(base_folder, "LongPNGs")
        self.formatted_png_folder = os.path.join(base_folder, "FormattedPNGs")
        self.final_pdf_folder = os.path.join(base_folder, "FinalPDFs")
        
        # Create all necessary folders
        for folder in [self.raw_folder, self.pdf_folder, self.long_png_folder, 
                      self.formatted_png_folder, self.final_pdf_folder]:
            os.makedirs(folder, exist_ok=True)
    
    def download_images(self, base_url, chapter_number, start_num="001"):
        """
        Task 1: Download images for a specific chapter
        
        Args:
            base_url: URL template with 'XXX' as placeholder for image number
            chapter_number: Chapter number for folder naming
            start_num: Starting image number (string), defaults to "001"
        
        Returns:
            Path to the folder containing downloaded images
        """
        output_folder = os.path.join(self.raw_folder, f"Chapter{chapter_number}")
        os.makedirs(output_folder, exist_ok=True)
        
        start = int(start_num)
        current_num = start
        max_failures = 5  # Stop after this many consecutive failures
        consecutive_failures = 0
        
        print(f"Starting download of Chapter {chapter_number} from image {start_num}")
        print("Automatically detecting the last available image...")
        
        while consecutive_failures < max_failures:
            url = base_url.replace('XXX', f'{current_num:03d}')
            
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
                consecutive_failures = 0  # Reset failure counter on success
                current_num += 1
            
            except requests.RequestException as e:
                consecutive_failures += 1
                if consecutive_failures >= max_failures:
                    print(f"Reached end of chapter at image {current_num-1:03d} after {max_failures} consecutive failures")
                    break
                print(f'Failed to download {url}: {e}')
                current_num += 1
        
        end_num = current_num - consecutive_failures - 1
        print(f'Finished downloading Chapter {chapter_number}! Downloaded images from {start_num} to {end_num:03d}')
        return output_folder
    
    def merge_png_to_pdf(self, folder_path, chapter_number):
        """
        Task 2: Merge PNG files into a PDF
        
        Args:
            folder_path: Path to the folder containing PNG files
            chapter_number: Chapter number for PDF naming
        
        Returns:
            Path to the generated PDF file
        """
        output_pdf_name = f"Chapter{chapter_number}_Merged.pdf"
        output_pdf_path = os.path.join(self.pdf_folder, output_pdf_name)
        
        # List all PNG files in the folder and sort them by their names
        png_files = sorted([f for f in os.listdir(folder_path) if f.endswith('.png')])
        
        if not png_files:
            print(f"No PNG images found in the directory '{folder_path}'.")
            return None

        # Open the first image to get the size and mode
        first_image_path = os.path.join(folder_path, png_files[0])
        first_image = Image.open(first_image_path)
        
        # Create a list to store all image objects
        image_list = [Image.open(os.path.join(folder_path, f)).convert('RGB') for f in png_files]

        # Save the images as a PDF
        image_list[0].save(output_pdf_path, save_all=True, append_images=image_list[1:])
        
        print(f'PDF created successfully at {output_pdf_path}')
        return output_pdf_path
    
    def pdf_to_long_image(self, pdf_path, chapter_number):
        """
        Task 3: Convert PDF to a long image
        
        Args:
            pdf_path: Path to the PDF file
            chapter_number: Chapter number for image naming
        
        Returns:
            Path to the generated long PNG image
        """
        output_image_name = f"Chapter{chapter_number}_Merged.png"
        output_image_path = os.path.join(self.long_png_folder, output_image_name)
        
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
        print(f'Long image created successfully at {output_image_path}')
        return output_image_path
    
    def is_black_or_white_band(self, image, y, band_height=5):
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
    
    def format_png(self, long_image_path, chapter_number):
        """
        Task 4: Format the long PNG into smaller slices
        
        Args:
            long_image_path: Path to the long PNG image
            chapter_number: Chapter number for output folder naming
        
        Returns:
            Path to the folder containing formatted PNG slices
        """
        output_folder = os.path.join(self.formatted_png_folder, f"Chapter{chapter_number}")
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
                        if self.is_black_or_white_band(long_image, current_height + y):
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
        return output_folder
    
    def formatted_pngs_to_pdf(self, formatted_folder, chapter_number):
        """
        Task 5: Convert the formatted PNGs back to a PDF file
        
        Args:
            formatted_folder: Path to the folder containing formatted PNG slices
            chapter_number: Chapter number for PDF naming
        
        Returns:
            Path to the final PDF file
        """
        output_pdf_name = f"Chapter{chapter_number}_Final.pdf"
        output_pdf_path = os.path.join(self.final_pdf_folder, output_pdf_name)
        
        # List all PNG files in the folder and sort them by their names
        png_files = sorted([f for f in os.listdir(formatted_folder) if f.endswith('.png')])
        
        if not png_files:
            print(f"No PNG images found in the directory '{formatted_folder}'.")
            return None

        # Create a list to store all image objects
        image_list = [Image.open(os.path.join(formatted_folder, f)).convert('RGB') for f in png_files]

        # Save the images as a PDF
        image_list[0].save(output_pdf_path, save_all=True, append_images=image_list[1:])
        
        print(f'Final PDF created successfully at {output_pdf_path}')
        return output_pdf_path
    
    def cleanup_temp_files(self, chapter_number, keep_raw=False):
        """
        Delete temporary files while keeping only the essential outputs:
        1. Long PNG image
        2. Final PDF
        
        Args:
            chapter_number: Chapter number to clean up
            keep_raw: If True, keeps the raw downloaded images (default: False)
        """
        print(f"Cleaning up temporary files for Chapter {chapter_number}...")
        
        # Paths to check and potentially delete
        raw_folder = os.path.join(self.raw_folder, f"Chapter{chapter_number}")
        temp_pdf_path = os.path.join(self.pdf_folder, f"Chapter{chapter_number}_Merged.pdf")
        formatted_folder = os.path.join(self.formatted_png_folder, f"Chapter{chapter_number}")
        
        # Delete the raw images folder if it exists and keep_raw is False
        if not keep_raw and os.path.exists(raw_folder):
            print(f"Deleting raw images folder: {raw_folder}")
            shutil.rmtree(raw_folder)
        
        # Delete the temporary merged PDF if it exists
        if os.path.exists(temp_pdf_path):
            print(f"Deleting temporary merged PDF: {temp_pdf_path}")
            os.remove(temp_pdf_path)
        
        # Delete the formatted PNG slices folder if it exists
        if os.path.exists(formatted_folder):
            print(f"Deleting formatted PNG slices folder: {formatted_folder}")
            shutil.rmtree(formatted_folder)
            
        print("Cleanup completed!")
        print("Remaining files:")
        print(f"  - Long PNG: {os.path.join(self.long_png_folder, f'Chapter{chapter_number}_Merged.png')}")
        print(f"  - Final PDF: {os.path.join(self.final_pdf_folder, f'Chapter{chapter_number}_Final.pdf')}")
    
    def process_chapter(self, base_url, chapter_number, start_num="001", cleanup=True):
        """
        Process a complete chapter through all steps:
        1. Download images
        2. Merge to PDF
        3. Convert to long PNG
        4. Format into slices
        5. Convert back to final PDF
        6. Clean up temporary files (optional)
        
        Args:
            base_url: URL template with 'XXX' as placeholder for image number
            chapter_number: Chapter number
            start_num: Starting image number (string), defaults to "001"
            cleanup: Whether to delete temporary files after processing (default: True)
            
        Returns:
            Path to the final PDF
        """
        print(f"Starting to process Chapter {chapter_number}...")
        
        # Task 1: Download images
        download_folder = self.download_images(base_url, chapter_number, start_num)
        
        # Task 2: Merge PNGs to PDF
        merged_pdf_path = self.merge_png_to_pdf(download_folder, chapter_number)
        
        # Task 3: Convert PDF to long PNG
        long_png_path = self.pdf_to_long_image(merged_pdf_path, chapter_number)
        
        # Task 4: Format the PNG
        formatted_folder = self.format_png(long_png_path, chapter_number)
        
        # Task 5: Convert formatted PNGs to final PDF
        final_pdf_path = self.formatted_pngs_to_pdf(formatted_folder, chapter_number)
        
        # Task 6: Clean up temporary files if requested
        if cleanup:
            self.cleanup_temp_files(chapter_number)
        
        print(f"Chapter {chapter_number} processing completed!")
        return final_pdf_path


# Example usage (commented out)
"""
if __name__ == "__main__":
    # Create a new processor instance
    processor = WebtoonProcessor("E:\\BookClub\\Webtoon\\TeenageMercenary")
    
    # Process a chapter (automatically detects last available image)
    processor.process_chapter(
        base_url="https://official.lowee.us/manga/Mercenary-Enrollment/0000-XXX.png",
        chapter_number="0"
    )
    
    # You can also specify a custom start number if needed
    # processor.process_chapter(
    #     base_url="https://official.lowee.us/manga/Mercenary-Enrollment/0000-XXX.png",
    #     chapter_number="1",
    #     start_num="010"  # Start from the 10th image
    # )
    
    # If you want to keep temporary files, set cleanup=False
    # processor.process_chapter(
    #     base_url="https://official.lowee.us/manga/Mercenary-Enrollment/0000-XXX.png",
    #     chapter_number="2",
    #     cleanup=False
    # )
    
    # Or run cleanup manually later
    # processor.cleanup_temp_files("2")
""" 