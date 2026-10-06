"""Run from /host/lab in Docker, with a private repository copy.

The root model/runner process can access credentials and hidden checks.
The LocalShellBackend child drops to UID 65534 and cannot access either.
Only results/report are copied back; source tasks/tests/skills are never synced.
"""
import os
import hashlib
import runpy
import shutil
import sys
from pathlib import Path

from dotenv import load_dotenv


def main():
    host = Path("/host/lab")
    private = Path("/lab")
    assert os.geteuid() == 0 and host.is_dir()
    Path("/host").chmod(0o700)
    private.chmod(0o700)
    load_dotenv(host / ".env", override=True)
    os.environ["LAB_ISOLATE_SHELL"] = "1"
    os.environ["LAB_ROOT"] = str(private)
    os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
    for name in ("src", "tasks", "tests", "scripts", "skills", "report", "results"):
        source = host / name
        if source.is_dir():
            shutil.copytree(source, private / name, dirs_exist_ok=True,
                            ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    initial = {
        str(path.relative_to(private)): hashlib.sha256(path.read_bytes()).digest()
        for name in ("results", "report") for path in (private / name).rglob("*")
        if path.is_file()
    }
    # New files created by file tools must remain writable by the shell UID.
    # /lab and /host remain explicitly mode 0700, so this does not expose them.
    os.umask(0)
    os.chdir(private)
    sys.path.insert(0, str(private / "src"))
    argv = sys.argv[1:]
    if argv and argv[0] == "python":
        argv = argv[1:]
    assert argv and argv[0].startswith("report/") and argv[0].endswith(".py")
    sys.argv = argv
    try:
        runpy.run_path(str(private / argv[0]), run_name="__main__")
    finally:
        for name in ("results", "report"):
            for source in (private / name).rglob("*"):
                if source.is_file():
                    relative = source.relative_to(private)
                    if hashlib.sha256(source.read_bytes()).digest() != initial.get(str(relative)):
                        # Do not restore stale, unchanged report files over edits
                        # the user made while the experiment was running.
                        target = host / relative
                        target.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(source, target)


if __name__ == "__main__":
    main()
