"""Application choices over the qualified reference and scripting API."""

import json
import sys

from scriptty import loads
from scriptty.application import execute
from wispsy.composition import text_workflow_document


class TextWorkbench:
    """Inspect/report text without requiring a terminal, storage or HTTP service."""

    def __init__(self, *, catalog_version="wispsy-text-v1"):
        self.catalog_version = catalog_version
        self.workflow = loads(json.dumps(text_workflow_document()), source="peaches:text-report")

    def inspect(self):
        return self.workflow.inspect()

    def catalog(self):
        """Explicitly assemble only the curated reference capabilities on demand."""
        from wispsy.integration import build_catalog

        return build_catalog()

    async def report(self, text: str, *, checkpoint=None, resume=False, retry=False,
                     restart=False, pace="auto", control=None, observer=None):
        """Return the same schema-1 outcome used by scripting/terminal hosts."""
        return await execute(self.workflow, self.catalog(), catalog_version=self.catalog_version,
            inputs={"text": text}, checkpoint=checkpoint, resume=resume, retry=retry,
            restart=restart, pace=pace, control=control, observer=observer)

    def table(self, texts: list[str]):
        if sys.version_info < (3, 14):
            raise ImportError("Install peaches[table] on Python 3.14+")
        try:
            from wispsy.tabular import normalize_table
        except ImportError:
            raise ImportError("Install peaches[table] on Python 3.14+") from None
        return normalize_table(texts)

    def markdown(self, texts: list[str]) -> str:
        return self.table(texts).to_document().to_markdown()

    def terminal_model(self, text: str, *, checkpoint):
        try:
            from scriptty.terminal import WorkflowTerminal
        except ImportError:
            raise ImportError("Install peaches[terminal] on Python 3.14+") from None
        return WorkflowTerminal(self.workflow, self.catalog(), catalog_version=self.catalog_version,
                                checkpoint=checkpoint, inputs={"text": text})

    async def review(self, text: str, *, checkpoint, **terminal_options):
        try:
            from scriptty.terminal import run_terminal
        except ImportError:
            raise ImportError("Install peaches[terminal] on Python 3.14+") from None
        return await run_terminal(self.workflow, self.catalog(), catalog_version=self.catalog_version,
                                  checkpoint=checkpoint, inputs={"text": text}, **terminal_options)
