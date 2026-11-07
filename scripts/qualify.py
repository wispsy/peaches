"""Install both workbench artifacts outside source and select optional profiles."""

import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import zipfile
from email.parser import BytesParser

ROOT = Path(__file__).resolve().parents[1]


def main():
    directory = Path(sys.argv[1]).resolve()
    artifacts = sorted([*directory.glob("*.whl"), *directory.glob("*.tar.gz")])
    assert len(artifacts) == 2
    wheel, = directory.glob("*.whl")
    with zipfile.ZipFile(wheel) as archive:
        assert "peaches/py.typed" in archive.namelist()
        metadata, = [name for name in archive.namelist() if name.endswith("/METADATA")]
        message = BytesParser().parsebytes(archive.read(metadata))
        assert message["Name"] == "peaches" and message["Requires-Python"] == ">=3.11"
    for artifact in artifacts:
        with tempfile.TemporaryDirectory() as temporary:
            outside = Path(temporary)
            environment = outside / "env"
            subprocess.run(["uv", "venv", str(environment), "--python", sys.executable], check=True)
            python = environment / ("Scripts/python.exe" if sys.platform == "win32" else "bin/python")
            def run(*command):
                subprocess.run(command, check=True, cwd=outside)
            run("uv", "pip", "install", "--python", str(python), str(artifact))
            run(str(python), "-I", "-c", "import importlib.util, peaches; assert all(importlib.util.find_spec(name) is None for name in ('func_seq','carets','headless_spreadsheets','expose_interface'))")
            run(str(python), "-I", "-m", "unittest", "discover", "-s", str(ROOT / "tests"), "-v")
            run("uv", "pip", "install", "--python", str(python), f"{artifact}[cli]")
            run(str(python), "-I", "-m", "unittest", "discover", "-s", str(ROOT / "cli_tests"), "-v")
            if sys.version_info >= (3, 14):
                run("uv", "pip", "install", "--python", str(python), f"{artifact}[cli,sequence,table,terminal]")
                run(str(python), "-I", "-m", "unittest", "discover", "-s", str(ROOT / "profile_tests"), "-v")
            run("uv", "pip", "check", "--python", str(python))
        print(json.dumps({"schema": 1, "artifact": artifact.name, "sha256": hashlib.sha256(artifact.read_bytes()).hexdigest()}))


if __name__ == "__main__":
    main()
