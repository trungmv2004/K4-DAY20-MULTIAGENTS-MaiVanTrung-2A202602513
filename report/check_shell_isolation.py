"""Offline checks of actual shell access, run through run_gemini.ps1."""
import json
from pathlib import Path

from langchain_core.messages import AIMessage

from lab.runner import run_task
from lab.testing import ScriptedChatModel


def main():
    command = (
        "id -u; python --version; "
        "if test -r /host/lab/.env; then echo SECRET_READABLE; exit 1; fi; "
        "if test -r /lab/tasks/code-eval/check.py; then echo CHECK_READABLE; exit 1; fi; "
        "if test -r /proc/1/environ; then echo ENV_READABLE; exit 1; fi; "
        "python -c 'from pathlib import Path; Path(\"workspace/probe.txt\").write_text(\"ok\")'; "
        "echo ISOLATION_OK"
    )
    model = ScriptedChatModel(script=[
        AIMessage(content="", tool_calls=[{"name": "execute", "args": {"command": command}, "id": "isolation"}]),
        AIMessage(content="done"),
    ])
    record = run_task("data-learn", "baseline", results_dir="report/isolation-check", model=model)
    trace = Path("report/isolation-check/baseline/data-learn/trace.md").read_text(encoding="utf-8")
    output = trace.split("### Tool result", 1)[1].split("### Assistant", 1)[0]
    assert not record["error"], record["error"]
    assert "65534" in output and "ISOLATION_OK" in output
    assert "READABLE" not in output and "Permission denied" not in output
    result = {"ok": True, "uid": 65534, "python": "available", "workspace_write": "ok",
              "host_env": "unreadable", "hidden_checks": "unreadable", "parent_env": "unreadable"}
    Path("report/shell-isolation.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result))


if __name__ == "__main__":
    main()
