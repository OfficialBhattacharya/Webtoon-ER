# Webtoon-ER: Webtoon Processing Tool

A Python tool that automatically downloads webtoon images and converts them into properly formatted PDF files. This tool is perfect for processing webcomics/webtoons from various sources and organizing them into readable PDF format.

## Features

- **Automatic Image Download**: Downloads all images for a chapter by detecting the last available image
- **PDF Generation**: Converts downloaded images into merged PDF files
- **Long Image Creation**: Combines all pages into a single long vertical image
- **Smart Formatting**: Automatically slices long images at optimal break points (black/white bands)
- **Final PDF Output**: Creates a properly formatted PDF with optimal page breaks
- **YAML Configuration**: Easy configuration through YAML file
- **Smart Cleanup**: Automatically removes temporary files, keeping only the long PNG and final PDF

## Installation

### Prerequisites

Make sure you have Python 3.6+ installed on your system.

### Required Dependencies

Install the required packages using pip:

```bash
pip install requests PyMuPDF Pillow reportlab PyYAML
```

Or use the provided requirements file:

```bash
pip install -r requirements.txt
```

The `requirements.txt` contains:
```
requests>=2.25.1
PyMuPDF>=1.18.0
Pillow>=8.0.0
reportlab>=3.5.0
PyYAML>=5.4.0
```

## Quick Start

### 1. Configure Your Settings

Create or edit the `config.yaml` file with your settings:

```yaml
# Webtoon Processor Configuration
# Edit the values below to configure your processing task

# Base URL with XXX as placeholder for image numbers
base_url: "https://official.lowee.us/manga/Mercenary-Enrollment/0000-XXX.png"

# Chapter number (as string)
chapter_number: "0"

# Output folder path where all files will be saved
output_folder: "D:\\Webtoon-ER\\Webtoons\\Mercenary_Enrollment"

# Optional: Starting image number (default: "001")
start_num: "001"

# Optional: Whether to keep temporary files during processing (default: false)
keep_temp_files: false
```

### 2. Run the Processor

Simply run:

```bash
python run_processor.py
```

The tool will:
1. Read configuration from `config.yaml`
2. Download all images for the chapter
3. Process them into a formatted PDF
4. Save the final PDF and long PNG
5. Clean up temporary files

## Configuration File (config.yaml)

### Required Fields

- **`base_url`**: URL template with 'XXX' as placeholder for image numbers
- **`chapter_number`**: Chapter number for naming files and folders
- **`output_folder`**: Path where all files will be saved

### Optional Fields

- **`start_num`**: Starting image number (default: "001")
- **`keep_temp_files`**: Whether to keep temporary files (default: false)

### Example Configurations

#### Mercenary Enrollment
```yaml
base_url: "https://official.lowee.us/manga/Mercenary-Enrollment/0000-XXX.png"
chapter_number: "0"
output_folder: "D:\\Webtoon-ER\\Webtoons\\Mercenary_Enrollment"
```

#### Custom Series
```yaml
base_url: "https://example.com/manga/my-series/chapter-XXX.jpg"
chapter_number: "1"
output_folder: "C:\\Comics\\MySeries"
start_num: "010"  # Start from image 010
keep_temp_files: true  # Keep all intermediate files
```

## Output Structure

When you specify an output folder (e.g., `D:\Webtoon-ER\Webtoons\Mercenary_Enrollment`), the tool creates this structure:

```
Your_Output_Folder/
├── LongPNGs/              # Long vertical images ⭐
│   └── ChapterX_Merged.png
└── FinalPDFs/             # Final output PDFs ⭐
    └── ChapterX_Final.pdf
```

**Note**: All temporary files (raw images, temp PDFs, formatted slices) are automatically deleted after processing to save space, keeping only the essential outputs.

## URL Format

The tool expects URLs with `XXX` as a placeholder for image numbers. Common patterns:

- `https://example.com/manga/series/chapter-XXX.png`
- `https://example.com/images/0000-XXX.jpg`
- `https://site.com/webtoon/chapter1/XXX.png`

The tool will automatically:
1. Replace `XXX` with `001`, `002`, `003`, etc.
2. Download images until it encounters consecutive failures
3. Stop when no more images are available

## Advanced Usage

### Using the WebtoonProcessor Class Directly

```python
from webtoon_processor import WebtoonProcessor

# Create processor instance
processor = WebtoonProcessor("your_output_folder")

# Process a chapter
final_pdf_path = processor.process_chapter(
    base_url="https://example.com/manga/series/0000-XXX.png",
    chapter_number="1",
    start_num="001",
    cleanup=True  # Clean up temporary files
)
```

### Processing Multiple Chapters

Create multiple config files or modify your script:

```python
import yaml
from webtoon_processor import WebtoonProcessor

chapters = ["0", "1", "2", "3", "4"]
base_url = "https://official.lowee.us/manga/Mercenary-Enrollment/000{}-XXX.png"
output_folder = "D:\\Webtoon-ER\\Webtoons\\Mercenary_Enrollment"

processor = WebtoonProcessor(output_folder)

for chapter in chapters:
    chapter_url = base_url.format(chapter)
    processor.process_chapter(
        base_url=chapter_url,
        chapter_number=chapter
    )
```

### Individual Tasks

You can also run individual tasks:

```python
processor = WebtoonProcessor("your_output_folder")

# Task 1: Download images only
download_folder = processor.download_images(base_url, chapter_number)

# Task 2: Convert images to PDF
pdf_path = processor.merge_png_to_pdf(download_folder, chapter_number)

# Task 3: Create long image
long_image_path = processor.pdf_to_long_image(pdf_path, chapter_number)

# Task 4: Format into slices
formatted_folder = processor.format_png(long_image_path, chapter_number)

# Task 5: Create final PDF
final_pdf = processor.formatted_pngs_to_pdf(formatted_folder, chapter_number)

# Task 6: Cleanup temporary files
processor.cleanup_temp_files(chapter_number)
```

## Troubleshooting

### Common Issues

1. **Config file not found**: Make sure `config.yaml` exists in the same directory as `run_processor.py`
2. **Invalid YAML**: Check your YAML syntax - use proper indentation and quotes for strings with special characters
3. **Network Errors**: Check your internet connection and URL format
4. **Permission Errors**: Ensure you have write permissions to the output folder
5. **Missing Dependencies**: Install all required packages using `pip install -r requirements.txt`

### Error Messages

- `Configuration file 'config.yaml' not found!`: Create a `config.yaml` file with your settings
- `Missing required configuration`: Make sure `base_url` and `output_folder` are specified
- `No PNG images found`: The download folder is empty or images aren't PNG format
- `Failed to download`: Network issue or incorrect URL
- `Permission denied`: Check folder permissions

## File Management

### What Gets Saved
- **Long PNG**: Single vertical image of the entire chapter
- **Final PDF**: Properly formatted PDF with optimal page breaks

### What Gets Deleted (Automatic Cleanup)
- Raw downloaded images
- Temporary merged PDF
- Formatted PNG slices
- All intermediate processing files

### Keeping Temporary Files
Set `keep_temp_files: true` in your config.yaml to preserve all intermediate files for debugging or manual inspection.

## Examples

### Basic Example (Mercenary Enrollment)
```yaml
base_url: "https://official.lowee.us/manga/Mercenary-Enrollment/0000-XXX.png"
chapter_number: "0"
output_folder: "D:\\Webtoon-ER\\Webtoons\\Mercenary_Enrollment"
```

### Advanced Example
```yaml
base_url: "https://mysite.com/comics/series/ep-XXX.jpg"
chapter_number: "12"
output_folder: "/home/user/Comics/MySeries"
start_num: "005"
keep_temp_files: true
```

## License

This tool is provided as-is for educational and personal use. Please respect the copyright and terms of service of the websites you're downloading from.

## Contributing

Feel free to submit issues and enhancement requests! 