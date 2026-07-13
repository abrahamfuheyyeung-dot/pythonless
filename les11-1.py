"""
Local image caption generator using Ollama Vision locally.
Requires:
  - pip install requests
  - ollama installed (the script can start it for you if available)
  - vision model pulled: ollama pull llava
"""
import argparse
import sys 

def describe_image(image_path: str) -> str:
    try:
        from PIL import Image
    except ImportError as exc:
        raise ImportError("Pillow is required for image processing") from exc
    try:
        from transformers import (
            VisionEncoderDecoderModel,
            ViTImageProcessor,
            AutoTokenizer,
       )
    except ImportError as exc:
        raise ImportError("Transformers is required for image captioning") from exc

    image = Image.open(image_path).convert("RGB")
    model_name = "nlpconnect/vit-gpt2-image-captioning"

    model = VisionEncoderDecoderModel.from_pretrained(model_name)
    feature_extractor = ViTImageProcessor.from_pretrained(model_name)
    tokenizer = AutoTokenizer.from_pretrained(model_name)

    'this decode caption below is kinda funky, after it gets the caption out, it goes off into threading, gotta fix that later'


    pixel_values = feature_extractor(images=image, return_tensors="pt").pixel_values
    output_ids = model.generate(pixel_values, max_length=16, num_beams=4)
    print(output_ids)
    caption = tokenizer.decode(output_ids[0], skip_special_tokens=True)

    return caption


def main():
    parser = argparse.ArgumentParser(description="Generate captions for images using Ollama Vision.")
    parser.add_argument("image_path", type=str, help="Path to the image file")

    args = parser.parse_args()

    try:
        description = describe_image(args.image_path)
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    print("Image Description")
    print(description)
    sys.exit(0)

if __name__ == "__main__":
    main()