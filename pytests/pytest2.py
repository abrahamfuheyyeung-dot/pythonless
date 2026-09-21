import sys
import subprocess
from pathlib import Path

les4_path = Path(__file__).resolve().parents[1] / "les4.py"




def test_les4_ann_output(tmp_path):
	result = subprocess.run(
		[sys.executable, str(les4_path), "--name", "Ann"],
		cwd=tmp_path,
		capture_output=True,
		text=True,
	)

	assert "math scores of [70, 80, 90]" in result.stdout
	assert "english scores of [20, 80, 70]" in result.stdout


