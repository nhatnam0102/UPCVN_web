import os
import requests
import time

# the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
# do not change this unless explicitly requested by the user
from openai import OpenAI

def generate_image(text, filename):
    """
    Generate an image using OpenAI's DALL-E and save it to static/images folder
    """
    # Create directory if not exists
    os.makedirs("static/images", exist_ok=True)
    
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY environment variable is not set")
    
    client = OpenAI(api_key=OPENAI_API_KEY)
    
    try:
        response = client.images.generate(
            model="dall-e-3",
            prompt=text,
            n=1,
            size="1024x1024"
        )
        
        image_url = response.data[0].url
        
        # Download the image
        img_response = requests.get(image_url)
        if img_response.status_code == 200:
            output_path = os.path.join("static/images", filename)
            with open(output_path, "wb") as file:
                file.write(img_response.content)
            return output_path
        else:
            print(f"Failed to download image: {img_response.status_code}")
            return None
    except Exception as e:
        print(f"Error generating image: {str(e)}")
        return None