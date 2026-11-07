import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from carets import KeyMsg
from carets.testing import TestProgram
from peaches import TextWorkbench
from wispsy.reference import run_reference


class ProfileTests(unittest.IsolatedAsyncioTestCase):
    async def test_typed_table_markdown_and_terminal_reuse_report_contract(self):
        workbench, text = TextWorkbench(), " Hello   WORLD "
        self.assertEqual(workbench.table([text]).to_records(), [run_reference(text)])
        self.assertIn("&lt;script&gt;", workbench.markdown(["<script>"]))
        with tempfile.TemporaryDirectory() as directory:
            model = workbench.terminal_model(text, checkpoint=str(Path(directory) / "terminal.json"))
            test = TestProgram(model)
            model.attach(test.program)
            async with test:
                await test.send(KeyMsg("tab"), KeyMsg(" "), KeyMsg("down"), KeyMsg(" "), KeyMsg("tab"), KeyMsg("enter"))
                await test.wait_for(lambda: model.status == "completed")
                self.assertEqual(model.outcome["outputs"], {"report": run_reference(text)})

    async def test_installed_commands_pause_and_resume_in_separate_processes(self):
        with tempfile.TemporaryDirectory() as directory:
            checkpoint = str(Path(directory) / "progress.json")
            def command(*options):
                result = subprocess.run([sys.executable, "-I", "-m", "peaches", "report", " Hello WORLD ", "--checkpoint", checkpoint, *options], cwd=directory, capture_output=True)
                self.assertEqual(result.returncode, 0, result.stderr)
                return json.loads(result.stdout)
            first = command("--pace", "function")
            self.assertEqual((first["status"], first["completed"]), ("paused", ["normalize"]))
            resumed = command("--resume")
            self.assertEqual(resumed["status"], "completed")
            self.assertEqual(resumed["run_id"], first["run_id"])
            self.assertEqual(resumed["outputs"], {"report": run_reference(" Hello WORLD ")})
