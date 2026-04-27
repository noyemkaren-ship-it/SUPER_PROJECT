import subprocess
import os

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

def java_chek(password):
    result = subprocess.run(
        ['java', '-cp', CURRENT_DIR, 'Chek', password],
        capture_output=True,
        text=True
    )
    return result.stdout.strip().lower()