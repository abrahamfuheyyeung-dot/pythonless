import transformers
from transformers import pipeline
print('transformers', transformers.__version__)
for task in ['image-captioning', 'image-to-text']:
    try:
        pipe = pipeline(task, model='nlpconnect/vit-gpt2-image-captioning', device=-1)
        print(task, 'ok', type(pipe).__name__)
    except Exception as exc:
        print(task, 'failed', type(exc).__name__, exc)
