"""
Local image caption generator using Ollama Vision API.
Requires:
  - pip install requests pillow
  - Ollama installed (the script can start it for you if available)
  - Vision model pulled: ollama pull llava
"""
import base64
import os
import subprocess
import time
from pathlib import Path

import requests
from PIL import Image

# Ollama API endpoint (default local)
OLLAMA_API_URL = os.getenv("OLLAMA_API_URL", "http://localhost:11434/api/generate")
VISION_MODEL = os.getenv("OLLAMA_MODEL", "llava")  # Vision-capable model


class CaptionGenerator:
    """Local image caption generator using Ollama Vision."""

    def __init__(
        self,
        model_name: str | None = None,
        api_url: str | None = None,
        auto_start: bool = True,
    ):
        """
        Initialize the caption generator with Ollama Vision.
        Requires Ollama to be running or present on the system.
        """
        self.model_name = model_name or VISION_MODEL
        self.api_url = api_url or OLLAMA_API_URL
        self._ensure_ollama_server(auto_start=auto_start)

    def _ensure_ollama_server(self, auto_start: bool) -> None:
        tags_url = self.api_url.replace("/api/generate", "/api/tags")
        try:
            response = requests.get(tags_url, timeout=2)
            response.raise_for_status()
            print("✓ Connected to Ollama")
            models = response.json().get("models", [])
            model_names = [m["name"].split(":")[0] for m in models]
            if self.model_name.split(":")[0] not in model_names:
                print(f"⚠ Warning: {self.model_name} not found. Pull it with: ollama pull {self.model_name}")
            else:
                print(f"✓ Model {self.model_name} is ready")
        except requests.exceptions.RequestException as exc:
            if not auto_start:
                print("❌ Error: Ollama is not running!")
                print("   Start it with: ollama serve")
                raise ConnectionError("Could not connect to Ollama") from exc

            if not self._start_ollama_server():
                print("❌ Error: Ollama is not running!")
                print("   Start it with: ollama serve")
                raise ConnectionError("Could not connect to Ollama") from exc

            for _ in range(10):
                time.sleep(0.5)
                try:
                    response = requests.get(tags_url, timeout=2)
                    response.raise_for_status()
                    print("✓ Connected to Ollama")
                    return
                except requests.exceptions.RequestException:
                    continue

            print("❌ Error: Ollama is not running!")
            print("   Start it with: ollama serve")
            raise ConnectionError("Could not connect to Ollama") from exc

    def _start_ollama_server(self) -> bool:
        try:
            creationflags = subprocess.CREATE_NEW_CONSOLE if os.name == "nt" else 0
            subprocess.Popen(
                ["ollama", "serve"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                stdin=subprocess.DEVNULL,
                creationflags=creationflags,
            )
            return True
        except OSError:
            return False

    def generate_caption(self, image_path: str) -> str:
        """
        Generate a caption for a single image using Ollama Vision.

        Args:
            image_path: Path to the image file

        Returns:
            Generated caption text
        """
        # Read and encode image
        with open(image_path, "rb") as f:
            image_data = base64.b64encode(f.read()).decode("utf-8")

        # Prepare prompt
        prompt = "Provide a concise, natural caption for this image in 1-2 sentences."

        # Call Ollama API
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "images": [image_data],
            "stream": False,
            "temperature": 0.7,
        }

        print("Generating caption...")
        response = requests.post(self.api_url, json=payload, timeout=120)

        if response.status_code != 200:
            raise RuntimeError(f"Ollama API error: {response.text}")

        result = response.json()
        caption = result.get("response", "").strip()

        return caption


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate captions for images using Ollama Vision locally"
    )
    parser.add_argument("image_path", help="Path to image file to caption")
    parser.add_argument("--model", default=None, help="Ollama model to use")
    parser.add_argument("--api-url", default=None, help="Override the Ollama API URL")
    parser.add_argument(
        "--no-auto-start",
        action="store_true",
        help="Do not try to start Ollama automatically",
    )

    args = parser.parse_args()

    path = Path(args.image_path)

    if path.is_file():
        try:
            generator = CaptionGenerator(
                model_name=args.model,
                api_url=args.api_url,
                auto_start=not args.no_auto_start,
            )
            caption = generator.generate_caption(str(path))
            print(f"\n📸 Image: {path.name}")
            print(f"✨ Caption: {caption}\n")
        except Exception as e:
            print(f"❌ Error: {e}")
    else:
        print(f"Error: {args.image_path} is not a valid image file")
