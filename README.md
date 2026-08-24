# PythonLess Lessons

This repository is a collection of small Python lessons and experiments. The files named `les*.py` are the learning track. They move from basic variables and lists to command-line arguments, CSV files, time-series analysis, web APIs, machine-learning image captions, and video creation.

## Running a lesson

From the repository directory:

```bash
python les0.py
python les1.py
python les2.py --name Ann
python les3.py --name Ann --writecsv
python les4.py --name Ann
python les5.py --name Ann --readcsv fromsheet.csv
python les8.py --age 2
python les10.py example
python les11.py image.jpg
python les11-1.py image.jpg
python les12-1.py image.jpg
python les13.py "path/to/frames" 0.2 output.mp4
```

Some lessons are demonstrations rather than reusable modules and execute their work immediately when started. Run them in a virtual environment and check each file's imports before installing optional dependencies.

## Lesson guide

### Foundations and data files

| File | What it demonstrates | How it is used |
| --- | --- | --- |
| `les0.py` | Variables, booleans, numbers, strings, type conversion, addition, and printing. | Run directly; prints example values. |
| `les1.py` | Lists, dictionaries, `statistics.mean`, sums, and measuring elapsed time with `time`. | Run directly; prints scores and timing information. |
| `les2.py` | Command-line parsing and looking up a student's math and English scores in an in-memory dictionary. | `python les2.py --name Ann` |
| `les3.py` | Functions, averages, dictionaries, CSV writing, and CSV reading. | `--name` selects a student; `--writecsv` writes `myfile.csv`. |
| `les4.py` | A revision of the score lookup lesson with an `all` branch and CSV output. | `python les4.py --name Ann`; its `all` path is experimental. |
| `les5.py` | Loading score rows from a CSV, converting score strings to integers, and calculating averages. | `python les5.py --name Ann --readcsv fromsheet.csv`; expects `Name`, `Math 1`–`Math 3`, and `Eng 1`–`Eng 3` columns. |

### Tools and analysis

| File | What it demonstrates | Notes |
| --- | --- | --- |
| `les6.py` | Git and GitHub concepts such as commits, branches, merges, pushes, pulls, and rebases. | Notes only; it does not run a program. |
| `les7.py` | Pandas data loading, datetime indexes, rolling averages, seasonal decomposition, ARIMA, SARIMAX, Matplotlib, and PDF reports. | Uses `monthly-milk-production.csv`, currently references a machine-specific absolute path, and writes `les7_plots.pdf`. It also requires NumPy, Pandas, Matplotlib, Statsmodels, and `openpyxl`-style data tooling as applicable. |
| `les8.py` | Reading a CSV into dictionaries, selecting a dog age, and averaging human-age equivalents. | Defaults to `dog_scores.csv`; use `python les8.py --age 2`. |
| `les9.py` | Currency conversion using a small table of USD, RMB, YEN, NTD, and WON rates. | `python les9.py --amount 10 --from USD --to RMB`. |
| `les10.py` | Calling the Dictionary API, printing definitions and parts of speech, and reading the result aloud with text-to-speech. | Requires internet access, `requests`, and `pyttsx3`; run `python les10.py word`. |

### Image and video captioning

| File | What it demonstrates | Requirements and usage |
| --- | --- | --- |
| `les11.py` | Single-image caption generation with Salesforce BLIP and Hugging Face Transformers. | Requires `torch`, `transformers`, and Pillow. Run `python les11.py image.jpg`. The model is downloaded and cached on first use. |
| `les11-1.py` | Alternate single-image caption implementation using a Vision Encoder-Decoder model and ViT image processor. | Requires `torch`, `transformers`, and Pillow. Run `python les11-1.py image.jpg`. Despite the old description in the source, this version uses Hugging Face models rather than Ollama. |
| `les12.py` | Captioning notes and example Ollama setup instructions stored in the file. | Documentation content only; it does not provide a normal executable workflow. |
| `les12-1.py` | Local Ollama Vision captioning through the Ollama HTTP API, with optional automatic server startup. | Requires Ollama, the `llava` model, `requests`, and Pillow. Run `python les12-1.py image.jpg`; use `--no-auto-start`, `--model`, or `--api-url` when needed. |
| `les13.py` | Finding and numerically sorting image frames, reading common image formats, generating captions, summarizing captions, and creating an MP4 video. | Requires Pillow and `imageio`; optional captioning requires `transformers` and `torch`, while HEIC/HEIF files require `pillow-heif`. Run `python les13.py "frames" 0.2 output.mp4`. |

## Optional dependencies

Install only the groups needed for the lesson you are running:

```bash
pip install requests pillow
pip install numpy pandas matplotlib statsmodels
pip install torch transformers
pip install imageio pillow-heif
pip install pyttsx3
```

For `les12-1.py`, install [Ollama](https://ollama.com), download a vision model, and leave the local service available:

```bash
ollama pull llava
ollama serve
```

For `les13.py`, the video-writing backend used by `imageio` may also need an installed FFmpeg executable, depending on the environment.

## Sample inputs and outputs

- `monthly-milk-production.csv` is the time-series input for `les7.py`.
- `dog_scores.csv` is the default input for `les8.py`.
- `fromsheet.csv` is an example score table for `les5.py`.
- `myfile.csv` may be created by `les3.py` or `les4.py`.
- `vidimg/` contains image frames that can be used with `les13.py`.
- `les7_plots.pdf` is generated by `les7.py`.

## Troubleshooting

- A lesson that imports an optional library will fail until that library is installed.
- `les7.py` may need its CSV path changed from `/Users/abrah/pythonless/monthly-milk-production.csv` to the local repository path.
- `les13.py` sorts frames by numbers in their filenames, so name frames consistently, such as `Frame1.png`, `Frame2.png`, and `Frame3.png`.
- `les12-1.py` needs Ollama reachable at `http://localhost:11434` by default and needs the requested vision model already pulled.

This is a personal learning project. The lesson scripts intentionally preserve exploratory code and are not presented as a single production package.
