"""Expose the curated workbench as ordinary application commands."""

import contextlib
import sys

from expose_interface import Interface, UsageError, option
from moveset.core import canonical

from .workbench import TextWorkbench


def build_interface():
    app = Interface("peaches", description="Inspect and run the selected text workbench.")

    @app.command(name="inspect")
    def inspect_workflow():
        return {"schema": 1, "status": "inspected", "workflow": TextWorkbench().inspect()}

    @app.command(name="report")
    async def report(text: str, *, checkpoint: str | None = None, resume: bool = False,
                     retry: bool = False, restart: bool = False, pace: str = "auto"):
        """Normalize/report text; optional checkpoints retain explicit recovery."""
        return await TextWorkbench().report(text, checkpoint=checkpoint, resume=resume,
                                            retry=retry, restart=restart, pace=pace)

    @app.command(name="markdown")
    @option("--text", dest="texts", multiple=True, required=True)
    def markdown(*, texts: list[str]):
        """Render typed reports through the optional table profile."""
        return {"schema": 1, "status": "rendered", "format": "markdown", "text": TextWorkbench().markdown(texts)}

    @app.command(name="review")
    async def review(text: str, *, checkpoint: str):
        """Select the optional interactive POSIX terminal profile."""
        return await TextWorkbench().review(text, checkpoint=checkpoint)

    return app


def main(argv=None):
    try:
        with contextlib.redirect_stdout(sys.stderr):
            outcome = build_interface().invoke(argv)
        if outcome is not None:
            sys.stdout.buffer.write(canonical(outcome) + b"\n")
            sys.stdout.buffer.flush()
    except Exception as error:
        record = {"schema": 1, "status": "error", "error": type(error).__name__, "message": str(error)}
        sys.stderr.buffer.write(b"\n" + canonical(record) + b"\n")
        sys.stderr.buffer.flush()
        raise SystemExit(2 if isinstance(error, UsageError) else 1) from None
