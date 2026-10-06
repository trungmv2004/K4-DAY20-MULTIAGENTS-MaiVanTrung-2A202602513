"""Summarize recorded observations without inventing missing runs."""
import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

from lab.compare import build_table, load_runs
from lab.tasks import ROOT, list_tasks


def main():
    runs = load_runs(ROOT / "results")
    report = ROOT / "report"
    (report / "table.md").write_text(build_table(runs) + "\n", encoding="utf-8")
    by_key = {(r["condition"], r["task"]): r for r in runs}
    missing, errors = [], []
    for condition in ("baseline", "subagents", "skills-auto"):
        for task in list_tasks():
            key = (condition, task.id)
            if key not in by_key:
                missing.append({"condition": condition, "task": task.id})
            elif by_key[key].get("error"):
                errors.append({"condition": condition, "task": task.id, "error": by_key[key]["error"]})
    groups = defaultdict(list)
    for record in runs:
        groups[(record["condition"], record["role"])].append(record)
    breakdown = []
    for (condition, role), records in sorted(groups.items()):
        technical = [c for r in records for c in r["checks"] if not c["name"].startswith("rule_")]
        rules = [c for r in records for c in r["checks"] if c["name"].startswith("rule_")]
        breakdown.append({"condition": condition, "role": role, "runs": len(records),
                          "errors": sum(bool(r.get("error")) for r in records),
                          "mean_score": sum(r["score"] for r in records) / len(records),
                          "technical_passed": sum(c["passed"] for c in technical), "technical_total": len(technical),
                          "rules_passed": sum(c["passed"] for c in rules), "rules_total": len(rules),
                          "mean_tokens": sum(r["tokens"]["total"] for r in records) / len(records),
                          "mean_seconds": sum(r["seconds"] for r in records) / len(records),
                          "subagent_calls": sum(r["subagent_calls"] for r in records),
                          "runs_read_skill": sum(r["skills_read"] > 0 for r in records)})
    repeats = []
    for task in list_tasks("learn"):
        path = ROOT / "results/gemini-repeat/skills-auto" / task.id / "run.json"
        if path.exists():
            repeat = json.loads(path.read_text(encoding="utf-8"))
            official = by_key.get(("skills-auto", task.id))
            repeats.append({"task": task.id, "repeat_score": repeat["score"], "repeat_error": repeat["error"],
                            "official_score": official["score"] if official else None,
                            "official_error": official["error"] if official else None,
                            "delta": official["score"] - repeat["score"] if official else None,
                            "repeat_tokens": repeat["tokens"]["total"],
                            "official_tokens": official["tokens"]["total"] if official else None,
                            "repeat_seconds": repeat["seconds"],
                            "official_seconds": official["seconds"] if official else None,
                            "same_skill_hash": official["skills_sha256"] == repeat["skills_sha256"] if official else None,
                            "repeat_skills_read": repeat["skills_read"],
                            "official_skills_read": official["skills_read"] if official else None})
    unique = {}
    for path in (ROOT / "results").rglob("run.json"):
        record = json.loads(path.read_text(encoding="utf-8"))
        if record.get("provider") != "Gemini Developer API":
            continue
        key = (record["condition"], record["task"], record["timestamp"])
        unique[key] = record
    budget = {"task_attempts": len(unique), "task_tokens": sum(r["tokens"]["total"] for r in unique.values()),
              "task_seconds": sum(r["seconds"] for r in unique.values()),
              "attempt_errors": sum(bool(r.get("error")) for r in unique.values())}
    summary = {"timestamp": datetime.now(timezone.utc).isoformat(), "selected_runs": len(runs),
               "error_free_runs": sum(not r.get("error") for r in runs), "planned_runs": 18,
               "missing": missing, "retry": errors, "breakdown": breakdown, "repeats": repeats, "budget": budget}
    for name, value in (("gemini-summary.json", summary), ("remaining-work.json", {
            "provider": "Gemini", "selected_runs": len(runs), "planned_runs": 18,
            "missing": missing, "retry": errors, "repeat_comparison": repeats,
            "resume": ".\\report\\run_gemini.ps1 python report/continue_gemini.py all --recursion-limit 60",
            "git_requirement": "Not performed: explicit no-commit/no-push instruction",
            "protocol": "Original pre-freeze learning coverage incomplete; continuation transfers the unchanged frozen skill"}),
            ("observed-breakdown.json", breakdown)):
        (report / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
