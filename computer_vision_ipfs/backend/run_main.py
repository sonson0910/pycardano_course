"""Run main.py but capture all output"""

import subprocess
import sys

result = subprocess.run(
    [
        sys.executable,
        "d:\\venera\\cardano\\pycardano_course\\computer_vision_ipfs\\backend\\main.py",
    ],
    capture_output=True,
    text=True,
    timeout=10,
)

print("STDOUT:")
print(result.stdout)
print("\nSTDERR:")
print(result.stderr)
print(f"\nReturn code: {result.returncode}")
