# PythonLess - Local AI & Utility Scripts

A collection of Python scripts demonstrating practical use cases for working with **local AI models (Ollama)**, image processing, CSV manipulation, and other utilities.

## Project Overview

This workspace contains:
- **Local AI Integration**: Scripts that work with Ollama for offline AI capabilities
- **Image Processing**: Caption generation and video creation from images
- **Data Processing**: CSV utilities and AI-powered data transformation
- **Learning Examples**: Lesson files demonstrating various Python concepts

## Key Features

### 🤖 AI & Language Models
- **CSV to AI** (`csv_to_ai.py`) - Batch process CSV rows through local Ollama models
- **Caption Generator** (`caption_generator.py` / `local_caption_generator.py`) - Generate image captions locally using Ollama Vision

### 🎥 Image & Video Processing
- **Video Creator** (`les13.py`) - Create MP4 videos from image sequences
- **Caption Overlay** - Add text captions to images with customizable fonts and backgrounds

### 💰 Utilities
- **Currency Converter** (`currency_converter.py`) - Convert between currencies

### 📚 Educational Examples
- Lesson files (`les0.py` through `les13.py`) - Progressive Python learning examples
- Test suite in `tests/` directory for validation

## Setup & Installation

### Prerequisites
- Python 3.7+
- For AI features: [Ollama](https://ollama.ai)

### Step 1: Install Ollama (for AI features)

**Windows:**
Download and run installer from https://ollama.ai/download/windows

**Mac:**
```bash
brew install ollama
```

**Linux:**
```bash
curl https://ollama.ai/install.sh | sh
```

### Step 2: Download Models

```bash
# For language tasks (CSV processing, etc.)
ollama pull llama3.2

# For image captioning
ollama pull llava
```

### Step 3: Install Python Dependencies

```bash
pip install requests pillow pandas tqdm imageio pillow-heif
```

## Usage Examples

### Process CSV with AI

```bash
python csv_to_ai.py --input prompts.csv --prompt-column prompt --output responses.csv --model llama3.2
```

### Generate Image Captions

```bash
python caption_generator.py image.jpg
```

### Create Video from Images

```bash
python les13.py "path/to/image/folder" 0.2 output.mp4
```

Arguments:
- Folder path containing numbered image files
- Delay between frames (seconds)
- Output video filename

## Project Structure

```
pythonless/
├── caption_generator.py          # Image caption generator
├── local_caption_generator.py     # Alternative implementation
├── csv_to_ai.py                 # Batch CSV processing with AI
├── currency_converter.py          # Currency conversion utility
├── les0.py through les13.py      # Progressive learning examples
├── tests/                         # Test suite
│   ├── test_ai_rewrite.py
│   ├── test_les11_1.py
│   ├── test_les13.py
│   ├── test_phrase_pairs.py
│   └── test_randomizer.py
├── restrec/                       # Restaurant recommendations data
│   ├── AIresp_o.csv
│   ├── criteria_output.csv
│   └── phrases.csv
├── vidimg/                        # Video/image files directory
└── *.csv                          # Sample data files
```

## Key Files

| File | Purpose |
|------|---------|
| `csv_to_ai.py` | Send CSV data to local Ollama models in batch |
| `caption_generator.py` | Generate and overlay captions on images |
| `les13.py` | Create MP4 videos from image sequences |
| `currency_converter.py` | Convert between currency values |
| `CAPTION_GENERATOR_README.md` | Detailed caption generator documentation |

## Running Tests

```bash
python -m pytest tests/
```

## Notes

- All AI features work **completely offline** after initial model download
- No API keys or external services required
- Ollama server must be running for AI features to work
- Start Ollama with: `ollama serve` (runs on localhost:11434 by default)

## Requirements

- Python 3.7+
- Ollama (optional, for AI features)
- Dependencies: requests, pillow, pandas, tqdm, imageio, pillow-heif

## License

This is a personal learning project.

## Resources

- [Ollama Documentation](https://github.com/ollama/ollama)
- [LLaVA Vision Model](https://github.com/haotian-liu/LLaVA)
- [Pillow Documentation](https://pillow.readthedocs.io/)
