# Peaches

A text workflow workbench: inspect, normalize and report text, then optionally
review progress in a terminal or consume typed tables and Markdown.

```python
import asyncio
from peaches import TextWorkbench

workbench = TextWorkbench()
outcome = asyncio.run(workbench.report(" Hello   WORLD "))
assert outcome["outputs"]["report"] == {"text": "hello world", "words": 2, "characters": 11}
document = workbench.inspect()
```

The library and optional CLI support Python 3.11+. Lifecycle, table and terminal
profiles require Python 3.14+. Install selected source profiles from this checkout:

```sh
uv run --python 3.11 --extra cli peaches report ' Hello WORLD '
uv run --python 3.11 --extra cli peaches inspect
uv run --python 3.14 --extra cli --extra sequence peaches report ' Hello WORLD ' --checkpoint progress.json --pace function
uv run --python 3.14 --extra cli --extra sequence peaches report ' Hello WORLD ' --checkpoint progress.json --resume
uv run --python 3.14 --extra cli --extra table peaches markdown --text ' Hello WORLD ' --text ' More WORDS '
uv run --python 3.14 --extra terminal peaches review ' Hello WORLD ' --checkpoint review.json
```

Run requires a new checkpoint path; --resume requires existing progress. --retry
explicitly repeats an uncertain step; --restart repeats the workflow. Outcomes
use Scriptty's schema-1 JSON contract. Commands keep UTF-8 results on stdout and
diagnostics/errors on stderr independently of console encoding.

`workbench.table(texts)` returns the existing typed Headless Spreadsheets Table;
`markdown(texts)` selects its detached, escaped renderer. `terminal_model` supplies
the same Scriptty/Carets model for embedding/testing; `await review(...)` selects
native terminal ownership. The native host requires a supported POSIX TTY. Every
surface uses the same curated text functions, explicit mappings and selected
capabilities. Terminal review requires capability confirmation before execution.

Peaches composes Wispsy's typed reference, Hidden Moves catalogs, moveset pipelines
and Scriptty's passive documents/application API. Func_seq owns optional durable
execution; Carets owns optional terminal behavior; Headless Spreadsheets owns
typed tables and rendering. The workbench introduces no second parser/executor
or new grammar. Inspect returns the existing passive schema-1 document.

This is a functional source-development package at 0.0.1.dev0 with immutable
sibling revisions. It is independently versioned and requires no hosted service.
Release/license/dependency publication choices remain in the
[Wispsy Composition Project](https://github.com/orgs/wispsy/projects/23).
Build with `uv build --out-dir dist`; `python scripts/qualify.py dist` installs
wheel/source artifacts outside the checkout, checks optional-profile isolation,
actual commands/restart and synthetic terminal/table equivalence. CI qualifies
Python 3.11 on Linux/Windows and Python 3.14 on Linux/macOS/Windows.
