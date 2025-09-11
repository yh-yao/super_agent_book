from diffusers import StableDiffusionPipeline
import torch

class DesignerAgent:
    def __init__(self):
        self.pipe = StableDiffusionPipeline.from_pretrained(
            "runwayml/stable-diffusion-v1-5"
        ).to("cuda")

    def run(self, text_prompt, save_path="outputs/poster.png"):
        image = self.pipe(text_prompt).images[0]
        image.save(save_path)
        return save_path
