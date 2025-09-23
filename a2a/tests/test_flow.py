import os, subprocess, sys, tempfile, pathlib

def test_end_to_end():
    repo_root = pathlib.Path(__file__).resolve().parents[1]
    output_dir = tempfile.mkdtemp()
    # Run the CLI via python -m
    cmd = [sys.executable, "-m", "a2a_demo", "--task", "Explain EOR vs PEO and give 3 practical tips for SMBs", "--max-turns", "6", "--output-dir", output_dir]
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=repo_root)
    assert result.returncode == 0
    # Check outputs
    files = os.listdir(output_dir)
    assert any(f.startswith("transcript-") and f.endswith(".txt") for f in files)
    assert any(f.startswith("report-") and f.endswith(".md") for f in files)
