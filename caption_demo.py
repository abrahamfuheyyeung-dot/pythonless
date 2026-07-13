"""
Demo script showing different ways to use the local caption generator.
"""
from pathlib import Path
from local_caption_generator import CaptionGenerator
from caption_generator import add_caption_to_image


def example_single_image():
    """Caption a single image."""
    print("=" * 60)
    print("EXAMPLE 1: Single Image Caption")
    print("=" * 60)
    
    generator = CaptionGenerator()
    
    # Replace with your actual image path
    image_path = "sample_image.jpg"
    
    if Path(image_path).exists():
        caption = generator.generate_caption(image_path)
        print(f"Image: {image_path}")
        print(f"Caption: {caption}\n")
    else:
        print(f"Sample image not found at {image_path}")
        print("Replace image_path with your actual image file\n")


def example_batch_processing():
    """Process all images in a directory."""
    print("=" * 60)
    print("EXAMPLE 2: Batch Process Directory")
    print("=" * 60)
    
    generator = CaptionGenerator()
    
    # Replace with your actual image directory
    image_dir = "my_images"
    
    if Path(image_dir).is_dir():
        generator.batch_caption_images(image_dir, output_file="captions.txt")
    else:
        print(f"Directory not found: {image_dir}")
        print("Create a directory with images and update the path\n")


def example_caption_and_draw():
    """Generate caption and draw it on the image."""
    print("=" * 60)
    print("EXAMPLE 3: Generate Caption + Draw on Image")
    print("=" * 60)
    
    generator = CaptionGenerator()
    
    image_path = "sample_image.jpg"
    
    if Path(image_path).exists():
        # Generate caption
        caption = generator.generate_caption(image_path)
        print(f"Generated caption: {caption}")
        
        # Add caption to image
        output_path = "sample_image_captioned.jpg"
        add_caption_to_image(image_path, output_path, caption)
        print(f"✓ Saved captioned image to: {output_path}\n")
    else:
        print(f"Image not found: {image_path}\n")


def example_custom_captions():
    """Generate captions with different settings."""
    print("=" * 60)
    print("EXAMPLE 4: Custom Caption Settings")
    print("=" * 60)
    
    generator = CaptionGenerator()
    
    image_path = "sample_image.jpg"
    
    if Path(image_path).exists():
        # Short caption (max 30 tokens)
        short_caption = generator.generate_caption(image_path, max_length=30)
        print(f"Short caption: {short_caption}")
        
        # Medium caption (max 50 tokens) - default
        medium_caption = generator.generate_caption(image_path, max_length=50)
        print(f"Medium caption: {medium_caption}")
        
        # Long caption (max 75 tokens)
        long_caption = generator.generate_caption(image_path, max_length=75)
        print(f"Long caption: {long_caption}\n")
    else:
        print(f"Image not found: {image_path}\n")


if __name__ == "__main__":
    print("\n🎨 LOCAL IMAGE CAPTION GENERATOR DEMO\n")
    print("Choose which example to run:\n")
    print("1. Single image caption")
    print("2. Batch process directory")
    print("3. Generate caption + draw on image")
    print("4. Custom caption settings")
    
    choice = input("\nEnter your choice (1-4): ").strip()
    
    if choice == "1":
        example_single_image()
    elif choice == "2":
        example_batch_processing()
    elif choice == "3":
        example_caption_and_draw()
    elif choice == "4":
        example_custom_captions()
    else:
        print("Invalid choice. Please run the script again and enter 1-4.")
