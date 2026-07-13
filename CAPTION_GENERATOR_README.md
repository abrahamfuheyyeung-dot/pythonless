# Local Image Caption Generator with Ollama Vision

## What It Does
- Generates captions for images **locally on your computer** using Ollama Vision
- Works **completely offline** after model download
- Fast and lightweight - no Hugging Face dependencies
- Perfect for one image at a time

## Installation

### Step 1: Install Ollama

**Windows:**
1. Download from https://ollama.ai/download/windows
2. Run the installer
3. Accept defaults and complete installation

**Mac:**
```bash
brew install ollama
```

**Linux:**
```bash
curl https://ollama.ai/install.sh | sh
```

### Step 2: Pull the Vision Model

Once Ollama is installed, pull the LLaVA vision model (one-time download, ~4.7GB):

```bash
ollama pull llava
```

This downloads the vision model locally - no internet required after this.

### Step 3: Install Python Dependencies

```bash
pip install requests pillow
```

That's it! No torch, no transformers, no Hugging Face downloads.

## Usage

### Start Ollama Server
In a terminal, start the Ollama API server (leave it running):

```bash
ollama serve
```

You should see:
```
Listening on 127.0.0.1:11434
```

**Keep this terminal open** while using the caption generator.

### Generate a Caption

In another terminal, run:

```bash
python local_caption_generator.py /path/to/image.jpg
```

Example output:
```
✓ Connected to Ollama
✓ Model llava is ready
Generating caption...

📸 Image: photo.jpg
✨ Caption: A golden retriever sits in a sunlit living room, looking contentedly at the camera while relaxing on a plush carpet.
```

## Examples

### Single Image
```bash
python local_caption_generator.py "C:\Users\Me\Pictures\vacation.jpg"
```

### With your caption drawing tool
```python
from local_caption_generator import CaptionGenerator
from caption_generator import add_caption_to_image

# Generate caption
generator = CaptionGenerator()
caption = generator.generate_caption("photo.jpg")

# Add caption to image
add_caption_to_image("photo.jpg", "photo_captioned.jpg", caption)
```

## Performance

- **First image:** ~10-15 seconds (model initialization)
- **Subsequent images:** ~5-10 seconds each
- Uses your GPU if available (automatic)
- Falls back to CPU otherwise

## Troubleshooting

**"Error: Ollama is not running!"**
- Make sure you ran `ollama serve` in another terminal
- Keep that terminal open while using the script

**"Model llava not found"**
- Run: `ollama pull llava` (one-time download)
- Wait for it to complete

**Model takes too long to download**
- LLaVA is ~4.7GB - this is a one-time download
- Once downloaded, subsequent runs are fast
- Make sure your internet connection is stable

**Port already in use**
- Ollama uses port 11434 by default
- Check if another instance is running: `ollama serve` in another terminal first

## Why Ollama?

✅ No Hugging Face downloads  
✅ Completely local and private  
✅ Fast (GPU accelerated if available)  
✅ Simple installation  
✅ Works offline after model download  
✅ Lightweight (~4.7GB for model)
