import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from wispsy.reference import run_reference


class InstalledCommandTests(unittest.TestCase):
    def test_module_and_console_entrypoints_match_library_outcomes(self):
        text = " HéLLo   🌍 "
        console = Path(sys.executable).with_name("peaches.exe" if sys.platform == "win32" else "peaches")
        with tempfile.TemporaryDirectory() as outside:
            for prefix in ([sys.executable, "-I", "-m", "peaches"], [str(console)]):
                result = subprocess.run([*prefix, "report", text], cwd=outside, env={**os.environ, "PYTHONIOENCODING": "cp1252"}, capture_output=True)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(json.loads(result.stdout)["outputs"], {"report": run_reference(text)})
            inspected = subprocess.run([str(console), "inspect"], cwd=outside, capture_output=True)
            self.assertEqual(inspected.returncode, 0, inspected.stderr)
            self.assertEqual(json.loads(inspected.stdout)["status"], "inspected")
            failure = subprocess.run([str(console), "report"], cwd=outside, capture_output=True)
            self.assertEqual(failure.returncode, 2)
            self.assertEqual(failure.stdout, b"")
            self.assertEqual(json.loads(failure.stderr.splitlines()[-1])["schema"], 1)
