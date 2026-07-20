"""
Simple image slideshow / quick-photo video player.

Usage:
    python les13.py "C:/path/to/folder" 0.2

The first argument is the folder containing images.
The second argument is the delay between images in seconds.



make it so that video can see if picture out of order
"""

import sys
import tkinter as tk
from pathlib import Path

try:
    from PIL import Image, ImageTk, UnidentifiedImageError
except ImportError:  # pragma: no cover - handled at runtime
    Image = None
    ImageTk = None
    UnidentifiedImageError = None

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


def load_photo(path: Path, width: int, height: int):
    if Image is None or ImageTk is None:
        raise RuntimeError("Pillow is required. Install it with: pip install pillow")

    if path.suffix.lower() in {".heic", ".heif"} and pillow_heif is None:
        raise RuntimeError("HEIC/HEIF support requires pillow-heif. Install it with: pip install pillow-heif")

    try:
        with Image.open(path) as img:
            img = img.convert("RGBA")
            resampling = getattr(Image, "Resampling", Image).LANCZOS
            img.thumbnail((width, height), resampling)
            return ImageTk.PhotoImage(img)
    except (UnidentifiedImageError, OSError) as error:
        raise RuntimeError(f"Could not read image: {path}\n{error}") from error


class ImagePlayer:
    def __init__(self, root: tk.Tk, image_paths, delay_seconds: float):
        self.root = root
        self.image_paths = image_paths
        self.delay_ms = max(50, int(delay_seconds * 1000))
        self.index = 0
        self.paused = False

        self.label = tk.Label(root, bg="black")
        self.label.pack(fill="both", expand=True)

        root.title("Image Slideshow")
        root.configure(bg="black")
        root.attributes("-fullscreen", True)
        root.bind("<Escape>", lambda event: root.destroy())
        root.bind("q", lambda event: root.destroy())
        root.bind("<space>", lambda event: self.toggle_pause())

        self.show_next()

    def toggle_pause(self):
        self.paused = not self.paused

    def display_image(self, path: Path):
        self.root.update_idletasks()
        width = max(1, self.root.winfo_width())
        height = max(1, self.root.winfo_height())
        photo = load_photo(path, width, height)
        self.label.configure(image=photo)
        self.label.image = photo
        self.root.title(path.name)

    def show_next(self):
        if self.paused:
            self.root.after(100, self.show_next)
            return

        if self.index >= len(self.image_paths):
            self.index = 0

        path = self.image_paths[self.index]
        self.index += 1
        self.display_image(path)
        self.root.after(self.delay_ms, self.show_next)


if __name__ == "__main__":
    folder = sys.argv[1] if len(sys.argv) > 1 else "."
    delay = float(sys.argv[2]) if len(sys.argv) > 2 else 0.2

    try:
        images = find_images(folder)
    except (FileNotFoundError, NotADirectoryError) as error:
        print(error)
        sys.exit(1)

    root = tk.Tk()
    ImagePlayer(root, images, delay)
    root.mainloop()
