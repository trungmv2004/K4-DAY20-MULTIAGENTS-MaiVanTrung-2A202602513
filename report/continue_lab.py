"""Resume the GUIDE stages after OpenRouter quota/credits become available.

Run through report/run_gemini.ps1 for the private Linux container.
Review generated skills before the freeze stage of a NEW experiment.
Existing attempts are archived; this script never creates Git commits or tags.
"""
import argparse
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

from lab.compare import build_table, load_runs
from lab.curator import curate_skills, validate_skill
from lab.runner import run_task
from lab.tasks import ROOT, hash_skills, list_tasks


def run(condition, task, *, force=False, recursion_limit=60):
    directory = ROOT / "results" / condition / task.id
    saved = directory / "run.json"
    if saved.exists():
        previous = json.loads(saved.read_text(encoding="utf-8"))
        if not force and not previous.get("error"):
            print(f"Keeping {condition}/{task.id}: {previous['passed']}/{previous['total']}", flush=True)
            return
    if directory.exists():
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
        backup = ROOT / "results/attempts" / condition / task.id / stamp
        backup.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(directory), str(backup))
    result = run_task(task.id, condition, results_dir=ROOT / "results", recursion_limit=recursion_limit)
    print(f"{condition}/{task.id}: {result['passed']}/{result['total']}; "
          f"tokens={result['tokens']['total']}; error={result['error']}", flush=True)
    if result["error"]:
        raise RuntimeError("Attempt saved. Resolve the execution/API error before resuming.")


def skills():
    paths = sorted((ROOT / "skills/auto").glob("*/SKILL.md"))
    if not paths:
        raise RuntimeError("No generated skill exists yet.")
    for path in paths:
        problems = validate_skill(path.read_text(encoding="utf-8"), path.parent.name)
        if problems:
            raise RuntimeError(f"Invalid skill {path.parent.name}: {problems}")
    return paths


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("stage", choices=["learn", "development", "freeze", "frozen-learning", "evaluation"])
    parser.add_argument("--recursion-limit", type=int, default=60)
    args = parser.parse_args()
    manifest_path = ROOT / "report/freeze.json"
    learning = list_tasks("learn")
    if args.stage in {"learn", "development"} and manifest_path.exists():
        raise RuntimeError("Already frozen; do not change the learning/skill development evidence.")
    if args.stage == "learn":
        for condition in ("baseline", "subagents"):
            for task in learning:
                run(condition, task, recursion_limit=args.recursion_limit)
        if not list((ROOT / "skills/auto").glob("*/SKILL.md")):
            paths = curate_skills()
            if not paths:
                raise RuntimeError("Curator produced no valid skills; inspect its output.")
        print("Review all generated SKILL.md files per GUIDE 3.3 before development/freeze.")
    elif args.stage == "development":
        skills()
        for task in learning:
            run("skills-auto", task, recursion_limit=args.recursion_limit)
    elif args.stage == "freeze":
        if manifest_path.exists():
            raise RuntimeError("Freeze manifest already exists; never overwrite it.")
        paths = skills()
        for condition in ("baseline", "subagents", "skills-auto"):
            for task in learning:
                path = ROOT / "results" / condition / task.id / "run.json"
                if not path.exists() or json.loads(path.read_text(encoding="utf-8")).get("error"):
                    raise RuntimeError(f"Missing successful learning run: {condition}/{task.id}")
        for condition in ("baseline", "subagents", "skills-auto"):
            for task in list_tasks("eval"):
                if (ROOT / "results" / condition / task.id / "run.json").exists():
                    raise RuntimeError("Evaluation evidence already exists; cannot preregister retroactively.")
        hypotheses = ROOT / "report/HYPOTHESES.md"
        text = hypotheses.read_text(encoding="utf-8")
        if any(not any(line.startswith(f"- H{i}:") and line.split(":", 1)[1].strip()
                       for line in text.splitlines()) for i in (1, 2, 3)):
            raise RuntimeError("Fill H1-H3 before freezing.")
        manifest = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "skills_sha256": hash_skills(ROOT / "skills/auto"),
            "hypotheses_sha256": hashlib.sha256(hypotheses.read_bytes()).hexdigest(),
            "skill_files": {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},
            "git_freeze": False,
            "reason": "Explicit user instruction: no commit, no push.",
        }
        development = ROOT / "results/skills-auto-dev"
        if development.exists():
            raise RuntimeError("Development backup already exists; inspect it before freezing.")
        shutil.copytree(ROOT / "results/skills-auto", development)
        shutil.copyfile(ROOT / "report/REPORT.md", ROOT / "report/REPORT-before-eval.md")
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        print("Local freeze saved. This does not meet the course's Git freeze requirement.")
    elif args.stage in {"frozen-learning", "evaluation"}:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if hash_skills(ROOT / "skills/auto") != manifest["skills_sha256"]:
            raise RuntimeError("Skills changed after freezing.")
        if hashlib.sha256((ROOT / "report/HYPOTHESES.md").read_bytes()).hexdigest() != manifest["hypotheses_sha256"]:
            raise RuntimeError("Hypotheses changed after freezing.")
        if args.stage == "frozen-learning":
            # Complete comparison coverage without using new feedback to revise skills.
            for condition in ("baseline", "subagents"):
                for task in learning:
                    run(condition, task, recursion_limit=args.recursion_limit)
            print("Learning comparison completed after partial freeze; curator was not called.")
            return
        for condition in ("baseline", "subagents"):
            for task in list_tasks("eval"):
                run(condition, task, recursion_limit=args.recursion_limit)
        frozen_at = datetime.fromisoformat(manifest["timestamp"])
        for task in list_tasks():
            path = ROOT / "results/skills-auto" / task.id / "run.json"
            force = False
            if path.exists():
                record = json.loads(path.read_text(encoding="utf-8"))
                force = datetime.fromisoformat(record["timestamp"]) < frozen_at
            run("skills-auto", task, force=force, recursion_limit=args.recursion_limit)
        (ROOT / "report/table.md").write_text(build_table(load_runs(ROOT / "results")) + "\n", encoding="utf-8")
        print("Official table saved; update REPORT.md from the actual records and traces.")


if __name__ == "__main__":
    main()
