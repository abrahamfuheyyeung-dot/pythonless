import importlib.util
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

import requests


MODULE_PATH = Path(__file__).resolve().parents[1] / "les11-1.py"
SPEC = importlib.util.spec_from_file_location("les11_1", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class CaptionGeneratorTests(unittest.TestCase):
    @patch("requests.get")
    @patch("subprocess.Popen")
    def test_init_starts_ollama_when_server_is_down(self, popen_mock, get_mock):
        get_mock.side_effect = [
            requests.exceptions.ConnectionError("down"),
            Mock(status_code=200, json=lambda: {"models": []}),
        ]
        popen_mock.return_value = Mock()

        generator = MODULE.CaptionGenerator(auto_start=True)

        self.assertEqual(generator.model_name, MODULE.VISION_MODEL)
        popen_mock.assert_called_once()


if __name__ == "__main__":
    unittest.main()
