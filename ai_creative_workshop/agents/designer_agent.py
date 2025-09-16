from openai import OpenAI
import requests
import os

class DesignerAgent:
    def __init__(self):
        self.client = OpenAI()

    def run(self, text_prompt, save_path="outputs/poster.png"):
        # Create outputs directory if it doesn't exist
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        
        # Generate image using DALL-E
        response = self.client.images.generate(
            model="dall-e-3",
            prompt=text_prompt,
            size="1024x1024",
            quality="standard",
            n=1,
        )
        
        # Download and save the image
        if response.data and len(response.data) > 0:
            image_url = response.data[0].url
            if image_url:
                image_response = requests.get(image_url)
                image_response.raise_for_status()
                
                with open(save_path, 'wb') as f:
                    f.write(image_response.content)
                
                return save_path
        
        raise Exception("Failed to generate image with DALL-E")
