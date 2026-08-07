import importlib.util
from pathlib import Path
spec = importlib.util.spec_from_file_location('les13', Path('les13.py'))
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
img = mod.load_image(Path('vidimg/Frame1.HEIC'))
for task in ['image-to-text', 'image-text-to-text']:
    try:
        captioner = mod.pipeline(task, model='nlpconnect/vit-gpt2-image-captioning')
        result = captioner(img)
        print(task, type(result), result, flush=True)
        print('extracted:', mod._extract_caption_text(result), flush=True)
    except Exception as e:
        print(task, 'FAILED', type(e).__name__, e, flush=True)
