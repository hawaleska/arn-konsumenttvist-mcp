import runpy
from pathlib import Path
def test_r5_real_sdk_metadata():
    runpy.run_path(str(Path(__file__).with_name("r5_metadata_check.py")),run_name="__main__")
