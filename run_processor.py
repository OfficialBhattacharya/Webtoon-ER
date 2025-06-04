#!/usr/bin/env python3
"""
Run Webtoon Processor with YAML configuration
"""
import yaml
from webtoon_processor import WebtoonProcessor

def load_config(config_file="config.yaml"):
    """Load configuration from YAML file"""
    try:
        with open(config_file, 'r', encoding='utf-8') as file:
            config = yaml.safe_load(file)
        return config
    except FileNotFoundError:
        print(f"❌ Configuration file '{config_file}' not found!")
        print("Please create a config.yaml file with your settings.")
        return None
    except yaml.YAMLError as e:
        print(f"❌ Error reading YAML configuration: {e}")
        return None

def main():
    print("=== Webtoon Processor ===")
    print("Loading configuration from config.yaml...")
    
    # Load configuration from YAML file
    config = load_config()
    if config is None:
        return False
    
    # Extract configuration values
    base_url = config.get('base_url')
    chapter_number = str(config.get('chapter_number', '0'))
    output_folder = config.get('output_folder')
    start_num = config.get('start_num', '001')
    keep_temp_files = config.get('keep_temp_files', False)
    
    # Validate required fields
    if not base_url or not output_folder:
        print("❌ Missing required configuration: base_url and output_folder must be specified")
        return False
    
    print(f"Processing Chapter {chapter_number}")
    print(f"Base URL: {base_url}")
    print(f"Output folder: {output_folder}")
    print(f"Start image: {start_num}")
    print(f"Keep temporary files: {keep_temp_files}")
    print("-" * 50)
    
    try:
        # Create processor instance
        processor = WebtoonProcessor(output_folder)
        
        # Process the chapter
        print(f"\nStarting to process Chapter {chapter_number}...")
        final_pdf_path = processor.process_chapter(
            base_url=base_url,
            chapter_number=chapter_number,
            start_num=start_num,
            cleanup=not keep_temp_files
        )
        
        print(f"\n✅ Success! Final PDF saved at: {final_pdf_path}")
        print(f"📁 Check the FinalPDFs folder in: {output_folder}")
        
    except Exception as e:
        print(f"\n❌ Error occurred: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    main() 