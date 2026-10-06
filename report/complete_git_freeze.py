"""Run development before the new Git freeze, then fresh official observations.

The original curator skill is reused without edits. Historical evaluation has
already been seen; this continuation does not claim a new blind preregistration.
Use run_gemini.ps1 so the model shell remains isolated from keys and checks.
"""
import argparse
import json
import time
from datetime import datetime, timezone

from lab.model import make_model
from lab.runner import run_task
from lab.tasks import ROOT, hash_skills, list_tasks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("stage", choices=["development", "official"])
    args = parser.parse_args()
    plan = json.loads((ROOT / "report/git-study-plan.json").read_text(encoding="utf-8"))
    model = make_model()
    assert type(model).__name__ == "ChatGoogleGenerativeAI"
    assert model.model == plan["model"].split(":", 1)[1]
    assert hash_skills(ROOT / "skills/auto") == plan["skills_sha256"]
    if args.stage == "development":
        target = ROOT / "results/skills-auto-dev"
        queue = [("skills-auto", task) for task in list_tasks("learn")]
        frozen = None
    else:
        target = ROOT / "results"
        frozen = json.loads((ROOT / "report/git-freeze.json").read_text(encoding="utf-8"))
        assert frozen["skills_sha256"] == plan["skills_sha256"]
        assert frozen["development_complete"]
        for task in list_tasks("learn"):
            dev = json.loads((ROOT / "results/skills-auto-dev" / task.id / "run.json").read_text(encoding="utf-8"))
            assert not dev["error"] and not dev["skills_modified"]
            assert datetime.fromisoformat(dev["timestamp"]) < datetime.fromisoformat(frozen["timestamp"])
            assert dev["model"] == plan["model"] and dev["recursion_limit"] == plan["recursion_limit"]
            assert dev["skills_sha256"] == plan["skills_sha256"]
        queue = [(condition, task) for condition in ("baseline", "subagents") for task in list_tasks("eval")]
        queue += [("skills-auto", task) for task in list_tasks()]
    for condition, task in queue:
        saved = target / condition / task.id / "run.json" if args.stage == "official" else target / task.id / "run.json"
        if saved.exists():
            old = json.loads(saved.read_text(encoding="utf-8"))
            assert old.get("study") == plan["study"], "Archive historical runs first"
            if not old["error"]:
                print(f"KEEP {condition}/{task.id}: {old['passed']}/{old['total']}", flush=True)
                continue
            raise RuntimeError(f"Failed observation retained at {saved}; archive before an explicit retry")
        print(f"START {args.stage} {condition}/{task.id}", flush=True)
        directory = target if args.stage == "official" else ROOT / "results/git-development-tmp"
        record = run_task(task.id, condition, results_dir=directory, model=model, recursion_limit=plan["recursion_limit"])
        record.update(model=plan["model"], provider="Gemini Developer API", temperature=plan["temperature"],
                      recursion_limit=plan["recursion_limit"], study=plan["study"], phase=args.stage)
        saved.parent.mkdir(parents=True, exist_ok=True)
        saved.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        if args.stage == "development":
            saved.with_name("trace.md").write_bytes((directory / condition / task.id / "trace.md").read_bytes())
        print(f"DONE {condition}/{task.id}: {record['passed']}/{record['total']} tokens={record['tokens']['total']} "
              f"seconds={record['seconds']} skills={record['skills_read']} subagents={record['subagent_calls']} error={record['error']}", flush=True)
        assert hash_skills(ROOT / "skills/auto") == plan["skills_sha256"]
        if frozen:
            assert datetime.fromisoformat(record["timestamp"]) >= datetime.fromisoformat(frozen["timestamp"])
        if record["error"]:
            print("Execution error saved; stop without consuming more quota.", flush=True)
            return 2
        time.sleep(3)
    print(f"COMPLETE {args.stage}; unchanged curator skill", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
