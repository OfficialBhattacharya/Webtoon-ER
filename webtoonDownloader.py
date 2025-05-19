import os
import sys
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

if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage: python script.py <base_url> <start_num> <end_num> <output_folder>")
        sys.exit(1)

    base_url = sys.argv[1]
    start_num = sys.argv[2]
    end_num = sys.argv[3]
    output_folder = sys.argv[4]

    download_images(base_url, start_num, end_num, output_folder)
