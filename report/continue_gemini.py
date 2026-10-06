"""Continue with Gemini, preserving the already frozen OpenRouter skill.

This is a model-transfer continuation, not a new preregistered study.
No curator invocation, skill edits, Git commits, or tags are performed.
"""
import argparse
import hashlib
import json
import shutil
import time
from datetime import datetime, timezone
from pathlib import Path

from lab.compare import build_table, load_runs
from lab.model import make_model
from lab.runner import run_task
from lab.tasks import ROOT, hash_skills, list_tasks


def check_freeze():
    frozen = json.loads((ROOT / "report/freeze.json").read_text(encoding="utf-8"))
    assert hash_skills(ROOT / "skills/auto") == frozen["skills_sha256"], "Frozen skills changed"
    assert hashlib.sha256((ROOT / "report/HYPOTHESES.md").read_bytes()).hexdigest() == frozen["hypotheses_sha256"], "Frozen hypotheses changed"
    return frozen


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("stage", choices=["learning", "repeat", "evaluation", "all"])
    parser.add_argument("--recursion-limit", type=int, default=60)
    args = parser.parse_args()
    frozen = check_freeze()
    profile = json.loads((ROOT / "report/gemini-plan.json").read_text(encoding="utf-8"))
    model = make_model()
    assert type(model).__name__ == "ChatGoogleGenerativeAI", "Gemini is not active in .env"
    assert model.model == profile["model"].split(":", 1)[1], "Model differs from recorded plan"
    queue = []
    if args.stage in ("learning", "all"):
        queue += [(c, t, ROOT / "results") for c in ("baseline", "subagents") for t in list_tasks("learn")]
    if args.stage in ("repeat", "all"):
        queue += [("skills-auto", t, ROOT / "results/gemini-repeat") for t in list_tasks("learn")]
    if args.stage in ("evaluation", "all"):
        queue += [(c, t, ROOT / "results") for c in ("baseline", "subagents") for t in list_tasks("eval")]
        queue += [("skills-auto", t, ROOT / "results") for t in list_tasks()]
    for condition, task, results in queue:
        check_freeze()
        directory = results / condition / task.id
        saved = directory / "run.json"
        if saved.exists():
            previous = json.loads(saved.read_text(encoding="utf-8"))
            if previous.get("model") == profile["model"] and not previous.get("error"):
                print(f"Keeping {condition}/{task.id}: {previous['passed']}/{previous['total']}", flush=True)
                continue
        for attempt in range(3):
            if directory.exists():
                # Both endpoints are resolved and checked inside this workspace.
                stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
                backup = ROOT / "results/gemini-attempts" / results.name / condition / task.id / stamp
                for path in (directory, backup):
                    assert path.resolve().is_relative_to(ROOT.resolve()), "Archive outside workspace"
                backup.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(directory), str(backup))
            print(f"START {condition}/{task.id} ({results.name}), attempt {attempt + 1}", flush=True)
            record = run_task(task.id, condition, results_dir=results, model=model, recursion_limit=args.recursion_limit)
            record.update(model=profile["model"], provider="Gemini Developer API", temperature=0,
                          recursion_limit=args.recursion_limit, study="frozen-skill model transfer")
            saved.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            print(f"DONE {condition}/{task.id}: {record['passed']}/{record['total']}; "
                  f"tokens={record['tokens']['total']}; seconds={record['seconds']}; "
                  f"subagents={record['subagent_calls']}; skills={record['skills_read']}; "
                  f"error={record['error']}", flush=True)
            (ROOT / "report/table.md").write_text(build_table(load_runs(ROOT / "results")) + "\n", encoding="utf-8")
            if not record["error"]:
                break
            error = record["error"].lower()
            if "429" not in error and "resource_exhausted" not in error and "rate" not in error:
                print("Execution error saved; investigate before continuing.", flush=True)
                return 2
            if "perday" in error or "per_day" in error or "limit: 0" in error or attempt == 2:
                print("Quota block saved; resume after quota becomes available.", flush=True)
                return 2
            for _ in range(3):
                print("Rate limit: waiting 20 seconds before retry.", flush=True)
                time.sleep(20)
    assert hash_skills(ROOT / "skills/auto") == frozen["skills_sha256"]
    print("Stage complete; frozen skill unchanged.", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
