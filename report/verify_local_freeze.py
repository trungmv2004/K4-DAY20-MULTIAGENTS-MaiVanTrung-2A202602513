"""Verify the local freeze evidence without creating commits or tags.

Run in the Linux lab container: python report/verify_local_freeze.py
This supplements, but does not satisfy, the course's Git freeze requirement.
"""
import hashlib
import json
from datetime import datetime
from pathlib import Path

from lab.tasks import ROOT, hash_skills, list_tasks


def main():
    manifest_path = ROOT / "report/freeze.json"
    if not manifest_path.exists():
        print("FAIL: local freeze has not been created; finish learning and skill review first.")
        return 1
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    problems = []
    if hash_skills(ROOT / "skills/auto") != manifest["skills_sha256"]:
        problems.append("skills changed after the local freeze")
    hypotheses = ROOT / "report/HYPOTHESES.md"
    if hashlib.sha256(hypotheses.read_bytes()).hexdigest() != manifest["hypotheses_sha256"]:
        problems.append("hypotheses changed after the local freeze")
    frozen_at = datetime.fromisoformat(manifest["timestamp"])
    count = 0
    for task in list_tasks():
        path = ROOT / "results/skills-auto" / task.id / "run.json"
        if not path.exists():
            problems.append(f"missing official skills-auto run: {task.id}")
            continue
        record = json.loads(path.read_text(encoding="utf-8"))
        count += 1
        if record.get("skills_sha256") != manifest["skills_sha256"]:
            problems.append(f"{task.id}: wrong skill hash")
        if record.get("skills_modified"):
            problems.append(f"{task.id}: modified skills in sandbox")
        if datetime.fromisoformat(record["timestamp"]) < frozen_at:
            problems.append(f"{task.id}: started before the local freeze")
        if record.get("error"):
            problems.append(f"{task.id}: execution error")
    for problem in problems:
        print("FAIL:", problem)
    print(f"Local freeze: {count} official runs checked; {'OK' if not problems else 'FAIL'}")
    print("Git freeze requirement remains unmet by the explicit no-commit instruction.")
    return int(bool(problems))


if __name__ == "__main__":
    raise SystemExit(main())
