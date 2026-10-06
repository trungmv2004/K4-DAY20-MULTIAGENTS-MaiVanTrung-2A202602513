"""Validate development timing, real Git freeze, records and protected sources."""
import argparse
import ast
import json
import subprocess
from datetime import datetime, timezone

from dotenv import dotenv_values
from lab.compare import build_table, load_runs
from lab.curator import validate_skill
from lab.tasks import ROOT, hash_skills, list_tasks


def git(*args):
    return subprocess.run(["git", "-c", f"safe.directory={ROOT}", "-c", "core.autocrlf=true", *args],
                          cwd=ROOT, capture_output=True, text=True, check=True).stdout.strip()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pre-freeze", action="store_true")
    args = parser.parse_args()
    report = ROOT / "report"
    plan = json.loads((report / "git-study-plan.json").read_text(encoding="utf-8"))
    assert hash_skills(ROOT / "skills/auto") == plan["skills_sha256"]
    for skill in (ROOT / "skills/auto").glob("*/SKILL.md"):
        assert not validate_skill(skill.read_text(encoding="utf-8"), expected_name=skill.parent.name)
        artifact = report / "curator-attempt-2/skills" / skill.parent.name / "SKILL.md"
        assert skill.read_bytes() == artifact.read_bytes()
    protected = ["tests", "tasks", "scripts", "src/lab/model.py", "src/lab/tasks.py", "src/lab/grading.py", "src/lab/testing.py", "src/lab/compare.py"]
    ref = plan["protected_reference_commit"]
    assert not git("diff", "--name-only", ref, "--", *protected)
    def named_nodes(source):
        result = {}
        for node in ast.parse(source).body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                result[node.name] = ast.dump(node, include_attributes=False)
            elif isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        result[target.id] = ast.dump(node, include_attributes=False)
        return result
    for name, members in {"agent.py": ["PATHS_NOTE", "BASE_PROMPT", "SKILLS_NOTE", "SUBAGENTS_NOTE"],
                          "runner.py": ["CONDITIONS", "render_trace", "main"],
                          "curator.py": ["SAFE_NAME", "validate_skill", "parse_skill_blocks"]}.items():
        path = "src/lab/" + name
        old, new = named_nodes(git("show", ref + ":" + path)), named_nodes((ROOT / path).read_text(encoding="utf-8"))
        for member in members:
            assert old[member] == new[member], member
    devs = []
    for task in list_tasks("learn"):
        directory = ROOT / "results/skills-auto-dev" / task.id
        record = json.loads((directory / "run.json").read_text(encoding="utf-8"))
        assert record["study"] == plan["study"] and record["phase"] == "development"
        assert record["error"] is None and record["skills_modified"] is False
        assert record["skills_sha256"] == plan["skills_sha256"]
        assert record["model"] == plan["model"] and record["recursion_limit"] == plan["recursion_limit"]
        assert directory.joinpath("trace.md").stat().st_size > 0
        devs.append(record)
    secrets = [v for k, v in dotenv_values(ROOT / ".env").items() if k.endswith(("_KEY", "_API_KEY")) and v and len(v) > 10]
    files = set()
    for directory in ("results", "report", "skills"):
        files.update(p for p in (ROOT / directory).rglob("*") if p.is_file() and p.suffix in (".md", ".json", ".txt", ".py", ".ps1"))
    files.update(ROOT / p for p in git("ls-files").splitlines() if p != ".env" and (ROOT / p).is_file())
    for path in files:
        assert not any(value in path.read_text(encoding="utf-8", errors="replace") for value in secrets), "Credential in artifact (value withheld)"
    assert ".env" not in git("ls-files").splitlines()
    assert ".env" not in git("diff", "--cached", "--name-only").splitlines()
    print(f"PASS: 3 development runs, unchanged curator skill/protected source, {len(files)} files scanned without configured secrets")
    if args.pre_freeze:
        return 0
    frozen = json.loads((report / "git-freeze.json").read_text(encoding="utf-8"))
    assert frozen["commit"] == git("rev-parse", "freeze^{commit}")
    tag_time = datetime.fromisoformat(git("log", "-1", "--format=%cI", "freeze"))
    assert all(datetime.fromisoformat(d["timestamp"]) < tag_time for d in devs)
    runs = load_runs(ROOT / "results")
    assert len(runs) == 18
    for condition in ("baseline", "subagents", "skills-auto"):
        selected = [r for r in runs if r["condition"] == condition]
        assert {r["task"] for r in selected} == {t.id for t in list_tasks()}
        for r in selected:
            assert r["error"] is None and not r["skills_modified"]
            assert r["model"] == plan["model"] and r["recursion_limit"] == plan["recursion_limit"] and r["temperature"] == plan["temperature"]
            assert r["total"] == len(r["checks"]) and r["passed"] == sum(c["passed"] for c in r["checks"])
            assert abs(r["score"] - r["passed"] / r["total"]) < 1e-10
            assert r["tokens"]["total"] == r["tokens"]["input"] + r["tokens"]["output"] > 0
            if condition == "skills-auto" or r["role"] == "eval":
                assert datetime.fromisoformat(r["timestamp"]) >= tag_time
                assert r["study"] == plan["study"]
            if condition == "skills-auto":
                assert r["skills_sha256"] == plan["skills_sha256"]
    assert (report / "table.md").read_text(encoding="utf-8").strip() == build_table(runs).strip()
    verifier = subprocess.run(["python", "scripts/verify_freeze.py"], cwd=ROOT, capture_output=True, text=True)
    (report / "git-freeze-check.txt").write_text(verifier.stdout + verifier.stderr, encoding="utf-8")
    assert verifier.returncode == 0, verifier.stdout + verifier.stderr
    print(verifier.stdout.strip())
    breakdown = subprocess.run(["python", "scripts/check_breakdown.py"], cwd=ROOT, capture_output=True, text=True, check=True)
    (report / "check_breakdown.txt").write_text(breakdown.stdout, encoding="utf-8")
    result = dict(timestamp=datetime.now(timezone.utc).isoformat(), ok=True, primary_runs=18, development_runs=3,
                  git_freeze=True, original_verifier_exit=verifier.returncode, tag_commit=frozen["commit"],
                  hypotheses_commit=frozen["hypotheses_commit"], development_before_git_freeze=True,
                  official_runs_after_git_freeze=True, same_skill_model_cap=True, protected_source_unchanged=True,
                  configured_secrets_found=False, files_scanned=len(files), fresh_blind_preregistration=False)
    (report / "git-study-validation.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("PASS: 18 official records, 3 pre/post pairs, real Git freeze, comparison table")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
