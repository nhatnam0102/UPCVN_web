import os
import requests
import time

# Create directories if they don't exist
os.makedirs("static/images/products", exist_ok=True)
os.makedirs("static/images/case_studies", exist_ok=True)

# Product images from Unsplash
product_images = {
    'bt_cloud': 'https://images.unsplash.com/photo-1489389944381-3471b5b30f04?w=800&auto=format&fit=crop&q=80',
    'ai': 'https://images.unsplash.com/photo-1591453089816-0fbb971b454c?w=800&auto=format&fit=crop&q=80',
    'wms': 'https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?w=800&auto=format&fit=crop&q=80',
    'iot': 'https://images.unsplash.com/photo-1580584126903-c17d41830450?w=800&auto=format&fit=crop&q=80',
    'cybouz': 'https://images.unsplash.com/photo-1600880292203-757bb62b4baf?w=800&auto=format&fit=crop&q=80',
    'custom': 'https://images.unsplash.com/photo-1577760258779-e787a1733016?w=800&auto=format&fit=crop&q=80',
}

# Case study images from Unsplash
case_study_images = {
    'case_kintone': 'https://images.unsplash.com/photo-1558494949-ef010cbdcc31?w=800&auto=format&fit=crop&q=80',
    'case_ai_inspection': 'https://images.unsplash.com/photo-1563986768609-322da13575f3?w=800&auto=format&fit=crop&q=80',
    'case_foreign_labor': 'https://images.unsplash.com/photo-1521791136064-7986c2920216?w=800&auto=format&fit=crop&q=80',
    'case_ai_ocr': 'https://images.unsplash.com/photo-1618044619888-009e412ff12a?w=800&auto=format&fit=crop&q=80',
    'case_temperature': 'https://images.unsplash.com/photo-1535350356005-fd52b3b524fb?w=800&auto=format&fit=crop&q=80',
    'case_more': 'https://images.unsplash.com/photo-1553877522-43269d4ea984?w=800&auto=format&fit=crop&q=80',
}

def download_image(url, filename):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            with open(filename, 'wb') as f:
                f.write(response.content)
            print(f"Downloaded: {filename}")
            return True
        else:
            print(f"Failed to download {url}. Status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"Error downloading {url}: {str(e)}")
        return False

# Download product images
print("Downloading product images...")
for name, url in product_images.items():
    output_file = f"static/images/products/{name}.jpg"
    if not os.path.exists(output_file):
        success = download_image(url, output_file)
        if success:
            time.sleep(0.5)  # Be nice to the server

# Download case study images
print("Downloading case study images...")
for name, url in case_study_images.items():
    output_file = f"static/images/case_studies/{name}.jpg"
    if not os.path.exists(output_file):
        success = download_image(url, output_file)
        if success:
            time.sleep(0.5)  # Be nice to the server

print("Image download completed.")