"""
Local image caption generator using BLIP model with offline capability.
Requires: pip install torch torchvision transformers pillow
"""
import os
from pathlib import Path
from PIL import Image
import torch
from transformers import BlipProcessor, BlipForConditionalGeneration

# Model cache directory
MODEL_CACHE_DIR = Path.home() / ".cache" / "image_caption_models"
MODEL_CACHE_DIR.mkdir(parents=True, exist_ok=True)

# Use CPU if CUDA not available (faster on most systems for this task)
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"


class CaptionGenerator:
    """Local image caption generator using BLIP model."""
    
    def __init__(self, model_name: str = "Salesforce/blip-image-captioning-base"):
        """
        Initialize the caption generator with a lightweight BLIP model.
        Downloads model on first run only.
        """
        print(f"Loading model to {DEVICE}...")
        
        # Download model once and cache it
        self.processor = BlipProcessor.from_pretrained(
            model_name,
            cache_dir=str(MODEL_CACHE_DIR)
        )
        self.model = BlipForConditionalGeneration.from_pretrained(
            model_name,
            cache_dir=str(MODEL_CACHE_DIR)
        ).to(DEVICE)
        
        print("✓ Model loaded successfully")
    
    def generate_caption(self, image_path: str, max_length: int = 50) -> str:
        """
        Generate a caption for a single image.
        
        Args:
            image_path: Path to the image file
            max_length: Maximum caption length in tokens
            
        Returns:
            Generated caption text
        """
        # Open and prepare image
        image = Image.open(image_path).convert("RGB")
        
        # Process image
        inputs = self.processor(image, return_tensors="pt").to(DEVICE)
        
        # Generate caption
        with torch.no_grad():
            out = self.model.generate(**inputs, max_length=max_length)
        
        # Decode to text
        caption = self.processor.decode(out[0], skip_special_tokens=True)
        return caption

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Generate captions for images locally without online downloads"
    )
    parser.add_argument(
        "image_path",
        help="Path to image file or directory of images"
    )
    parser.add_argument(
        "-o", "--output",
        help="Output file for batch captions (default: captions.txt)",
        default="captions.txt"
    )
    
    args = parser.parse_args()
    
    # Initialize generator (downloads model on first run)
    generator = CaptionGenerator()
    
    path = Path(args.image_path)
    
    if path.is_file():
        # Single image
        caption = generator.generate_caption(str(path))
        print(f"Image: {path.name}")
        print(f"Caption: {caption}")
    else:
        print(f"Error: {args.image_path} is not a valid file or directory")
