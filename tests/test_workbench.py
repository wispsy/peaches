import unittest

from peaches import TextWorkbench
from wispsy.reference import run_reference


class WorkbenchTests(unittest.IsolatedAsyncioTestCase):
    async def test_report_reuses_the_same_typed_reference_without_lifecycle(self):
        workbench = TextWorkbench()
        for text in (" Hello  WORLD ", " Straße 🌍 ", ""):
            outcome = await workbench.report(text)
            self.assertEqual((outcome["schema"], outcome["status"], outcome["outputs"]),
                             (1, "completed", {"report": run_reference(text)}))
            self.assertIsNone(outcome["run_id"])
        with self.assertRaises(ValueError):
            await workbench.report(2)

    async def test_inspection_is_passive_and_returns_detached_metadata(self):
        workbench = TextWorkbench()
        workbench.inspect()["steps"].clear()
        self.assertEqual(len(workbench.inspect()["steps"]), 2)
        self.assertEqual([step["capability"] for step in workbench.inspect()["steps"]], ["text.normalize", "text.report"])
