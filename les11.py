from transformers import BlipProcessor, BlipForConditionalGeneration
from PIL import Image
import torch
import argparse

parser = argparse.ArgumentParser()


parser.add_argument("image_path", help = "Path to JPEG")
args = parser.parse_args()

# Load model
processor = BlipProcessor.from_pretrained(
    "Salesforce/blip-image-captioning-base"
)

model = BlipForConditionalGeneration.from_pretrained(
    "Salesforce/blip-image-captioning-base"
)

# Open JPEG image
image = Image.open(args.image_path).convert("RGB")

# Process image
inputs = processor(images=image, return_tensors="pt")

# Generate caption
out = model.generate(**inputs)

# Decode caption
caption = processor.decode(out[0], skip_special_tokens=True)

print("Caption:", caption)