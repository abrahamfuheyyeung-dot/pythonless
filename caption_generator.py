from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def add_caption_to_image(input_path: str, output_path: str, caption: str) -> None:
    """Open an image, draw a caption at the bottom, and save the result."""
    image = Image.open(input_path)
    image = image.convert("RGB")

    draw = ImageDraw.Draw(image)
    width, height = image.size

    try:
        font = ImageFont.truetype("arial.ttf", size=max(20, width // 20))
    except OSError:
        font = ImageFont.load_default()

    text = caption.strip()
    padding = 20
    text_width, text_height = draw.textsize(text, font=font)

    rectangle_height = text_height + padding
    rectangle_y = height - rectangle_height
    draw.rectangle(
        [(0, rectangle_y), (width, height)],
        fill=(0, 0, 0, 150)
    )

    text_x = (width - text_width) // 2
    text_y = rectangle_y + (padding // 2)
    draw.text((text_x, text_y), text, fill=(255, 255, 255), font=font)

    output_format = Path(output_path).suffix.replace(".", "").upper() or image.format
    image.save(output_path, format=output_format)


def read_caption_from_file(path: str) -> str:
    with open(path, encoding="utf-8") as file:
        return file.read().strip()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Write a text caption onto any Pillow-supported image.")
    parser.add_argument("input", help="Path to the source image file")
    parser.add_argument("output", help="Path to save the captioned image")

    caption_group = parser.add_mutually_exclusive_group(required=True)
    caption_group.add_argument("--caption", help="Caption text to draw on the image")
    caption_group.add_argument("--caption-file", help="Path to a text file containing the caption")

    args = parser.parse_args()

    caption_text = args.caption if args.caption is not None else read_caption_from_file(args.caption_file)
    add_caption_to_image(args.input, args.output, caption_text)
