"""
Create a real video file from a folder of images.

Usage:
    python les13.py "C:/path/to/folder" 0.2 output.mp4

The first argument is the folder containing images.
The second argument is the delay between images in seconds.
The third argument is the output video file name.

Make sure you name your frames properly; the script reads the frames in numerical sequence.
"""

import os
import sys
from pathlib import Path

try:
    from PIL import Image, UnidentifiedImageError
except ImportError:  # pragma: no cover - handled at runtime
    Image = None
    UnidentifiedImageError = None

try:
    import imageio.v2 as imageio
except ImportError:  # pragma: no cover - handled at runtime
    imageio = None

try:
    from transformers import pipeline
except ImportError:  # pragma: no cover - handled at runtime
    pipeline = None

try:
    from transformers import AutoProcessor, BlipForConditionalGeneration
except ImportError:  # pragma: no cover - handled at runtime
    AutoProcessor = None
    BlipForConditionalGeneration = None

try:
    import pillow_heif  # noqa: F401
except ImportError:  # pragma: no cover - handled at runtime
    pillow_heif = None

if pillow_heif is not None:
    try:
        pillow_heif.register_heif_opener()
    except Exception:  # pragma: no cover - some versions expose a different API
        pass

SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".tif", ".tiff", ".heic", ".heif"}


class LocalVisionCaptionGenerator:
    def __init__(self, model_name: str = "nlpconnect/vit-gpt2-image-captioning"):
        self.model_name = model_name
        from transformers import AutoFeatureExtractor, VisionEncoderDecoderModel

        self.feature_extractor = AutoFeatureExtractor.from_pretrained(model_name)
        self.model = VisionEncoderDecoderModel.from_pretrained(model_name)

    def generate_caption(self, image_path: str) -> str:
        from transformers import AutoTokenizer

        image = load_image(Path(image_path))
        if image is None:
            return ""

        image = image.convert("RGB")
        inputs = self.feature_extractor(images=image, return_tensors="pt")
        generated_ids = self.model.generate(**inputs)
        tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        return tokenizer.decode(generated_ids[0], skip_special_tokens=True)


def extract_number(name: str):
    lower_name = name.lower()

    for token in lower_name.replace(".", " ").replace("_", " ").replace("-", " ").split():
        if token.isdigit():
            return int(token)

    digits = []
    for char in lower_name:
        if char.isdigit():
            digits.append(char)
        elif digits:
            break

    if digits:
        return int("".join(digits))

    return float("inf")


def find_images(folder_path: str):
    folder = Path(folder_path)
    if not folder.exists() or not folder.is_dir():
        raise FileNotFoundError(f"Folder not found: {folder_path}")

    images = [
        path for path in folder.iterdir()
        if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS
    ]
    images.sort(key=lambda path: (extract_number(path.name.lower()), path.name.lower()))

    if not images:
        raise FileNotFoundError(f"No supported image files found in: {folder_path}")

    return images


def load_image(path: Path):
    if Image is None:
        raise RuntimeError("Pillow is required. Install it with: pip install pillow")

    if path.suffix.lower() in {".heic", ".heif"} and pillow_heif is None:
        raise RuntimeError("HEIC/HEIF support requires pillow-heif. Install it with: pip install pillow-heif")

    try:
        with Image.open(path) as img:
            return img.convert("RGBA")
    except (UnidentifiedImageError, OSError) as error:
        raise RuntimeError(f"Could not read image: {path}\n{error}") from error


def _extract_caption_text(result):
    if isinstance(result, dict):
        for key in ("generated_text", "caption", "text", "output_text"):
            value = result.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
    elif isinstance(result, list):
        for item in result:
            text = _extract_caption_text(item)
            if text:
                return text
    elif isinstance(result, str):
        text = result.strip()
        if text:
            return text

    return ""


def _create_caption_pipeline(model_name: str):
    if pipeline is not None:
        for task_name in ("image-captioning", "image-to-text"):
            try:
                return pipeline(task_name, model=model_name)
            except Exception:
                continue

    if AutoProcessor is not None and BlipForConditionalGeneration is not None:
        try:
            processor = AutoProcessor.from_pretrained(model_name)
            model = BlipForConditionalGeneration.from_pretrained(model_name)
            return _BLIPCaptioner(processor, model)
        except Exception:
            return None

    return None


class _BLIPCaptioner:
    def __init__(self, processor, model):
        self.processor = processor
        self.model = model

    def __call__(self, image):
        inputs = self.processor(images=image, return_tensors="pt")
        generated_ids = self.model.generate(**inputs)
        caption = self.processor.decode(generated_ids[0], skip_special_tokens=True)
        return [{"generated_text": caption}]


def summarize_captions(captions):
    if not captions:
        return "No images were provided."

    unique_captions = []
    for caption in captions:
        if caption not in unique_captions:
            unique_captions.append(caption)

    cleaned_captions = [caption.strip().rstrip(".") for caption in unique_captions if caption and caption.strip()]

    if not cleaned_captions:
        return "No images were provided."

    if len(cleaned_captions) == 1:
        return f"The video shows {cleaned_captions[0]}."

    if len(cleaned_captions) == 2:
        return f"The video shows {cleaned_captions[0]}, then {cleaned_captions[1]}."

    first_caption = cleaned_captions[0]
    later_captions = ", then ".join(cleaned_captions[1:4])
    return f"The video shows {first_caption}, then {later_captions}."


def describe_video_locally(image_paths, delay_seconds: float):
    count = len(image_paths)
    if count == 0:
        return "No images were provided."

    captions = []
    if pipeline is not None:
        try:
            captioner = _create_caption_pipeline("Salesforce/blip-image-captioning-base")
            if captioner is None:
                raise RuntimeError("Unable to initialize a Hugging Face image captioning model")
            for path in image_paths:
                try:
                    image = load_image(path).convert("RGB")
                    result = captioner(image)
                    caption = _extract_caption_text(result)
                    if caption:
                        captions.append(caption)
                except Exception:
                    continue
        except Exception:
            captions = []
    else:
        try:
            generator = LocalVisionCaptionGenerator()
            for path in image_paths:
                try:
                    caption = generator.generate_caption(str(path))
                    if caption:
                        captions.append(caption)
                except Exception:
                    continue
        except Exception:
            captions = []

    if captions:
        return summarize_captions(captions)

    names = [Path(path.name).stem for path in image_paths]
    cleaned_names = []
    for name in names:
        cleaned = name.replace("_", " ").replace("-", " ").replace(".", " ")
        cleaned_names.append(cleaned)

    first_name = cleaned_names[0]
    last_name = cleaned_names[-1]

    if count == 1:
        return f"The video shows a single image depicting {first_name}."

    if first_name.lower() == last_name.lower():
        return f"The video shows a sequence of images centered around {first_name}."

    if first_name and last_name and first_name.lower() != last_name.lower():
        return (
            f"The video shows a sequence of frames beginning with {first_name} and ending with {last_name}, "
            f"suggesting a changing scene across the clip."
        )

    return f"The video shows a sequence of frames centered around {first_name}."


def create_video(image_paths, output_path: str, delay_seconds: float):
    if imageio is None:
        raise RuntimeError("imageio is required. Install it with: pip install imageio")

    frames = []
    for path in image_paths:
        image = load_image(path)
        frames.append(image)

    fps = max(1, int(round(1 / delay_seconds)))
    imageio.mimsave(output_path, frames, fps=fps, format="FFMPEG")
    print(f"Video saved to: {output_path}")

    description = describe_video_locally(image_paths, delay_seconds)
    print("Local video description:")
    print(description)

    if os.name == "nt":
        os.startfile(output_path)
    else:
        print("Open the video file manually:")
        print(output_path)


if __name__ == "__main__":
    folder = sys.argv[1] if len(sys.argv) > 1 else "."
    delay = float(sys.argv[2]) if len(sys.argv) > 2 else 0.2
    output = sys.argv[3] if len(sys.argv) > 3 else "output.mp4"

    try:
        images = find_images(folder)
    except (FileNotFoundError, NotADirectoryError) as error:
        print(error)
        sys.exit(1)

    try:
        create_video(images, output, delay)
    except Exception as error:
        print(error)
        sys.exit(1)
