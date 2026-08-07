import importlib.util
from pathlib import Path
from unittest.mock import patch

from PIL import Image

spec = importlib.util.spec_from_file_location("les13", Path(__file__).resolve().parents[1] / "les13.py")
les13 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(les13)


def test_summarize_captions_describes_scene_content():
    captions = [
        "a dog running in a park",
        "a dog resting on the grass",
    ]

    description = les13.summarize_captions(captions)

    assert "dog" in description.lower()
    assert "park" in description.lower() or "grass" in description.lower()
    assert "then" in description.lower()
    assert "shows" in description.lower()


def test_describe_video_locally_keeps_successful_captions_when_one_frame_fails(tmp_path):
    image_one = tmp_path / "frame1.png"
    image_two = tmp_path / "frame2.png"
    Image.new("RGB", (4, 4), color="red").save(image_one)
    Image.new("RGB", (4, 4), color="blue").save(image_two)

    class FakeCaptioner:
        def __init__(self):
            self.calls = 0

        def __call__(self, image):
            self.calls += 1
            if self.calls == 1:
                return [{"generated_text": "a dog running in a park"}]
            raise RuntimeError("frame failed")

    fake_captioner = FakeCaptioner()

    with patch.object(les13, "pipeline", return_value=fake_captioner):
        description = les13.describe_video_locally([image_one, image_two], 0.2)

    assert "dog" in description.lower()
    assert "park" in description.lower()
    assert "shows" in description.lower()


def test_describe_video_locally_uses_image_to_text_task_when_image_captioning_is_unavailable(tmp_path):
    image_path = tmp_path / "frame.png"
    Image.new("RGB", (4, 4), color="green").save(image_path)

    class FakePipeline:
        def __init__(self, task, model, **kwargs):
            self.task = task
            self.model = model

        def __call__(self, image):
            return [{"generated_text": "a dog running"}]

    def fake_pipeline(task, model=None, **kwargs):
        if task == "image-captioning":
            raise ValueError("unsupported task")
        if task == "image-to-text":
            return FakePipeline(task, model, **kwargs)
        raise AssertionError(f"unexpected task {task}")

    with patch.object(les13, "pipeline", side_effect=fake_pipeline):
        description = les13.describe_video_locally([image_path], 0.2)

    assert "dog" in description.lower()
    assert "running" in description.lower()


def test_extract_caption_text_supports_common_result_shapes():
    assert les13._extract_caption_text({"generated_text": "a dog"}) == "a dog"
    assert les13._extract_caption_text([{"caption": "a cat"}]) == "a cat"
    assert les13._extract_caption_text("a bird") == "a bird"
