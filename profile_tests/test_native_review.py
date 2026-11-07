import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest


@unittest.skipUnless(os.name == "posix", "Native POSIX review host")
class NativeReviewTests(unittest.TestCase):
    def test_actual_terminal_selection_run_and_quit_restore_the_session(self):
        import fcntl
        import pty
        import select
        import struct
        import termios

        master, slave = pty.openpty()
        fcntl.ioctl(slave, termios.TIOCSWINSZ, struct.pack("HHHH", 24, 80, 0, 0))
        original = termios.tcgetattr(slave)
        with tempfile.TemporaryDirectory() as directory:
            checkpoint = Path(directory) / "review.json"
            process = subprocess.Popen([sys.executable, "-I", "-m", "peaches", "review", " Hello WORLD ",
                "--checkpoint", str(checkpoint)], stdin=slave, stderr=slave, stdout=subprocess.PIPE, cwd=directory)
            def drain():
                if select.select([master], [], [], 0.02)[0]:
                    os.read(master, 65536)
            try:
                deadline = time.monotonic() + 5
                while termios.tcgetattr(slave)[3] & termios.ICANON and process.poll() is None and time.monotonic() < deadline:
                    drain()
                self.assertFalse(termios.tcgetattr(slave)[3] & termios.ICANON, "Native raw session did not start")
                # Input editor → explicitly select both capabilities → actions → run.
                os.write(master, b"\t \x1b[B \t\r")
                completed = False
                deadline = time.monotonic() + 5
                while process.poll() is None and time.monotonic() < deadline:
                    drain()
                    if checkpoint.exists() and json.loads(checkpoint.read_text())["status"] == "completed":
                        completed = True
                        break
                self.assertTrue(completed, "Native keyboard execution did not complete")
                os.write(master, b"q")
                output, _ = process.communicate(timeout=5)
                self.assertEqual(process.returncode, 0, output)
                self.assertEqual(json.loads(output)["outputs"], {"report": {"text": "hello world", "words": 2, "characters": 11}})
                restored = termios.tcgetattr(slave)
                mask = termios.ICANON | termios.ECHO
                self.assertEqual(restored[3] & mask, original[3] & mask)
            finally:
                if process.poll() is None:
                    process.kill()
                    process.communicate()
                os.close(master)
                os.close(slave)
