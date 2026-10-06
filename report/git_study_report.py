"""Build the current report from real observations in the Git-freeze continuation."""
import json
from collections import defaultdict
from datetime import datetime, timezone

from lab.compare import build_table, load_runs
from lab.tasks import ROOT, list_tasks


def main():
    report = ROOT / "report"
    plan = json.loads((report / "git-study-plan.json").read_text(encoding="utf-8"))
    archived = (report / "pre-git-freeze/REPORT.md").read_text(encoding="utf-8")
    def section(number):
        return archived.split(f"## {number}.", 1)[1].split(f"## {number + 1}.", 1)[0].strip()
    runs = load_runs(ROOT / "results")
    table = build_table(runs)
    (report / "table.md").write_text(table + "\n", encoding="utf-8")
    by_key = {(r["condition"], r["task"]): r for r in runs}
    devs = {}
    for task in list_tasks("learn"):
        path = ROOT / "results/skills-auto-dev" / task.id / "run.json"
        if path.exists():
            devs[task.id] = json.loads(path.read_text(encoding="utf-8"))
    frozen_path = report / "git-freeze.json"
    frozen = json.loads(frozen_path.read_text(encoding="utf-8")) if frozen_path.exists() else None
    groups = defaultdict(list)
    for r in runs:
        groups[(r["condition"], r["role"])].append(r)
    breakdown = []
    for (condition, role), records in sorted(groups.items()):
        technical = [c for r in records for c in r["checks"] if not c["name"].startswith("rule_")]
        rules = [c for r in records for c in r["checks"] if c["name"].startswith("rule_")]
        breakdown.append(dict(condition=condition, role=role, runs=len(records), errors=sum(bool(r["error"]) for r in records),
                              technical_passed=sum(c["passed"] for c in technical), technical_total=len(technical),
                              rules_passed=sum(c["passed"] for c in rules), rules_total=len(rules),
                              mean_score=sum(r["score"] for r in records)/len(records),
                              mean_tokens=sum(r["tokens"]["total"] for r in records)/len(records)))
    summary_rows = ["| Điều kiện | Vai trò | Kỹ thuật | Quy ước | Token TB |", "|---|---|---|---|---:|"]
    for b in breakdown:
        summary_rows.append(f"| {b['condition']} | {b['role']} | {b['technical_passed']}/{b['technical_total']} | "
                            f"{b['rules_passed']}/{b['rules_total']} | {b['mean_tokens']:,.0f} |")
    delegation = ["| Task | subagent_calls | Loại được giao trong vết | Token | Giây |", "|---|---:|---|---:|---:|"]
    for r in sorted((r for r in runs if r["condition"] == "subagents"), key=lambda r: r["task"]):
        trace = (ROOT / "results/subagents" / r["task"] / "trace.md").read_text(encoding="utf-8")
        types = []
        for line in trace.splitlines():
            try:
                item = json.loads(line)
                if isinstance(item, dict) and "subagent_type" in item:
                    types.append(item["subagent_type"])
            except (ValueError, TypeError):
                pass
        delegation.append(f"| {r['task']} | {r['subagent_calls']} | {', '.join(types) or 'Không thấy lời giao việc'} | {r['tokens']['total']:,} | {r['seconds']} |")
    pairs = []
    noise = ["| Task | Development trước freeze | Chính thức sau freeze | Δ điểm | Token dev / chính thức | skills_read dev / chính thức |", "|---|---|---|---:|---|---|"]
    for task in list_tasks("learn"):
        d, o = devs.get(task.id), by_key.get(("skills-auto", task.id))
        if d and o:
            pair = dict(task=task.id, development_score=d["score"], official_score=o["score"], delta=o["score"]-d["score"],
                        same_hash=d["skills_sha256"]==o["skills_sha256"], same_model=d["model"]==o["model"],
                        same_cap=d["recursion_limit"]==o["recursion_limit"], development_timestamp=d["timestamp"], official_timestamp=o["timestamp"])
            pairs.append(pair)
            noise.append(f"| {task.id} | {d['passed']}/{d['total']} | {o['passed']}/{o['total']} | {pair['delta']:+.3f} | "
                         f"{d['tokens']['total']:,} / {o['tokens']['total']:,} | {d['skills_read']} / {o['skills_read']} |")
        elif d:
            noise.append(f"| {task.id} | {d['passed']}/{d['total']} | Chưa chạy | — | {d['tokens']['total']:,} / — | {d['skills_read']} / — |")
    costs = ["| Condition | Số lượt | Điểm TB | Token TB | Điểm / 10.000 token |", "|---|---:|---:|---:|---:|"]
    means = {}
    for condition in ("baseline", "subagents", "skills-auto"):
        rs = [r for r in runs if r["condition"] == condition]
        if not rs:
            continue
        score = sum(r["score"] for r in rs)/len(rs)
        tokens = sum(r["tokens"]["total"] for r in rs)/len(rs)
        costs.append(f"| {condition} | {len(rs)} | {score:.3f} | {tokens:,.0f} | {score/tokens*10000:.4f} |")
        for role in ("learn", "eval"):
            selected = [r for r in rs if r["role"]==role]
            if selected:means[(condition, role)]=sum(r["score"] for r in selected)/len(selected)
    comparisons = []
    for condition in ("subagents", "skills-auto"):
        for role in ("learn", "eval"):
            if (condition,role) in means and ("baseline",role) in means:
                comparisons.append(f"- {condition}, {role}: chênh baseline {means[(condition,role)]-means[('baseline',role)]:+.3f} trên thang 0–1.")
    mechanisms_path = report / "git-study-observations.md"
    mechanisms = mechanisms_path.read_text(encoding="utf-8") if mechanisms_path.exists() else "Các quan sát trace mới sẽ bổ sung sau khi chạy chính thức; chưa kết luận cơ chế từ điểm chưa có."
    old_unread = """Đối chiếu phiên trước tại `results/pre-git-freeze/skills-auto/`: cả bốn lượt dưới đây có `skills_read=0`, trace không ghi `read_file` vào SKILL.md.

| Lượt cũ | Hành vi quan sát | Giải thích khả dĩ về kích hoạt |
|---|---|---|
| code-learn | Đọc mã/docstring, sửa pricing/report/export và chạy pytest | Skill chỉ nói answer.json/meta/clean.csv; không cung cấp quy ước type hints, regression tests hoặc changelog cho sửa mã |
| code-eval | Sửa bookings/billing, timeutil, schedule và chạy test | Đề yêu cầu sửa package; description không nhắm việc sửa mã, nên ít phù hợp với nhiệm vụ |
| logs-learn | Đọc app.log rồi ghi/đọc errors.json | Output là errors.json; skill yêu cầu order_id/region/amount_cents, không hướng dẫn service names, errors sorting hay schema log |
| logs-eval | Đọc worker.log rồi ghi/đọc errors.json | JSON triage log khác answer.json/meta/clean.csv; skill không bao phủ repeat_count/counts_by_service hoặc quy ước log mới |

Đây là suy luận từ description, đề bài và vết, không phải quan sát suy nghĩ nội bộ của model. Có công cụ nạp skill không bảo đảm model chọn đọc nó. Trong bốn lượt này không có bằng chứng skill giúp các check quy ước; UTC xuất hiện ở cả log và skill nhưng nội dung chưa được đọc. Không mở rộng description bằng tay hay tạo skill từ feedback đánh giá."""
    current_reads = ["| Lượt skills-auto mới | skills_read | Quan sát trong trace |", "|---|---:|---|"]
    for r in sorted((r for r in runs if r["condition"]=="skills-auto"),key=lambda r:r["task"]):
        current_reads.append(f"| {r['task']} | {r['skills_read']} | {'Đã đọc; cần đối chiếu từng chỉ dẫn với output/check' if r['skills_read'] else 'Không đọc; description chỉ nhắm answer.json/meta/clean.csv, xem phạm vi bên trên'} |")
    hypotheses = section(2).split("\n\nGemini là",1)[0]
    # The original hypotheses stay unchanged; only current execution evidence is replaced.
    curator = section(6).split("\n\nDevelopment gốc",1)[0]
    content = f"""# Báo cáo Lab: Self evolving Agentic — hoàn thiện Git freeze

Ngày: 06/10/2026, Asia/Bangkok. Phiên cũ được giữ ở `results/pre-git-freeze/` và `report/pre-git-freeze/`. Người dùng đã cho phép commit/tag freeze; không push. Skill curator OpenRouter giữ nguyên byte. Phiên này sửa bằng chứng trình tự chạy và bổ sung phân tích, không tuyên bố chưa từng thấy đánh giá trước đây.

## 1. Thông tin nhóm và cấu hình

| Họ tên | Mã sinh viên | Phần thực hiện |
|---|---|---|
| Mai Văn Trung | 2A202602513 | Harness, thí nghiệm và báo cáo với trợ lý Codex |

- Model `{plan['model']}`, Gemini Developer API, temperature {plan['temperature']}, recursion limit {plan['recursion_limit']}. Python 3.12.15, Deep Agents 0.7.21, langchain-google-genai 4.4.0; Docker Linux trên Windows.
- Cấu hình shell UID 65534, không kế thừa khóa, không đọc thư mục runner/check ẩn. Xem shell-isolation.json và REPRODUCE.md. `.env` được ignore.
- Có {len(runs)}/18 lượt chính, {sum(not r['error'] for r in runs)} không lỗi thực thi; development mới {len(devs)}/3. Sáu lượt baseline/subagents học được giữ từ trước tag, cùng model/cap, không chạy lại không cần thiết.
- Commit tag freeze: {frozen['commit'] if frozen else 'chưa tạo — bản nháp trước freeze'}. Commit hypotheses: {frozen['hypotheses_commit'] if frozen else 'sẽ commit sau khi đủ development'}. Kế hoạch: git-study-plan.json.

## 2. Giả thuyết trước tag freeze

{hypotheses}

Giữ các giả thuyết từ hồ sơ trước đánh giá ban đầu, không đổi chúng để khớp kết quả. Commit mới ghi lại nội dung này trước tag mới; do đã thấy kết quả phiên trước, đây là xác nhận lại giả thuyết có sẵn trong phiên tiếp tục, không phải đăng ký mù mới.

## 3. Làm quen Deep Agents

{section(3)}

System prompt mặc định khi không truyền system_prompt là rỗng, như tour.txt thể hiện.

## 4. Đường cơ sở và phân loại lỗi

{section(4)}

## 5. Điều kiện subagents

Explorer đọc đặc tả và báo cáo, không sửa; implementer thực hiện có phạm vi và kiểm chứng; reviewer kiểm tra độc lập, không sửa. Description nêu tình huống giao việc; mỗi vai trò nhận PATHS_NOTE.

{chr(10).join(delegation)}

subagent_calls=0 vẫn là kết quả hợp lệ: model có công cụ task nhưng có thể chọn xử lý trực tiếp. Những tác vụ nhỏ có thể không cần phân vai; đây là giải thích khả dĩ, không xác nhận suy nghĩ nội bộ. Trace chỉ lưu luồng chính, callback token có cộng model call bên trong subagent. Phân tích giao việc cụ thể được bổ sung ở mục 8 từ prompt/báo cáo lưu trong trace mới.

## 6. Skill curator và development trước freeze

{curator}

Development mới ở `results/skills-auto-dev/<task>/`; ba lượt này dùng skill nguyên bản, cùng Gemini/model/cap với lượt chính. Không chạy curator thêm, không thay skill sau khi đã xem đánh giá. Phiên cũ có development chưa đủ; không dùng nó để đo nhiễu trên model mới.

{chr(10).join(noise)}

### Vì sao bốn lượt trước không đọc skill

{old_unread}

### Việc đọc skill trong lượt chính mới

{chr(10).join(current_reads)}

## 7. Kết quả so sánh và đóng băng

{table}

{chr(10).join(summary_rows)}

Hash skill `{plan['skills_sha256']}`. Báo cáo không coi hash cục bộ là thay thế Git. Verifier gốc được chạy sau khi đủ lượt chính; kết quả lưu ở git-freeze-check.txt. Các lượt chính skills-auto phải sau thời điểm commit tag mới, các lượt development phải trước nó, hash/model/cap phải bằng nhau. Trạng thái thực tế: {'tag đã được tạo; kiểm tra kết quả chạy trong git-study-validation.json' if frozen else 'chưa tạo tag; chưa có lượt chính mới'}.

## 8. Phân tích

{chr(10).join(comparisons)}

Chỉ so sánh điều kiện sau khi có cùng độ phủ. Kết quả âm hoặc bằng nhau không làm mất giá trị thí nghiệm; không suy ra quan hệ nhân quả từ một lượt/task.

{mechanisms}

### Chi phí

{chr(10).join(costs)}

Điểm/token được tính từ các lượt chính cùng model. Token không đồng nhất với tiền vì tier/cache/billing khác nhau. Dùng số lần gọi và trace để đánh giá chi phí giao việc, không mặc định đa tác tử hiệu quả hơn.

### Nhiễu development so với sau freeze

{chr(10).join(noise)}

Chênh điểm chính thức trừ development trong ba cặp: {', '.join(f"{p['task']} {p['delta']:+.3f}" for p in pairs) or 'chưa đủ cặp'}. Cùng skill/model/cap và không sửa skill, nên biến động giữa hai lần chạy là ước lượng nhiễu quan sát, không phải skill học thêm. Một cặp/task chưa đủ khoảng tin cậy hoặc kiểm định thống kê. Đối chiếu timestamp/hash nằm trong git-study-summary.json; không gán thay đổi token hoặc điểm cho curator mới.

### Rò rỉ và quá khớp

Skill khớp byte với curator-attempt-2, không thêm quy tắc đánh giá. Skill chỉ sinh từ data-learn OpenRouter, schema region có nguy cơ không chuyển giao sang dữ liệu khác; thiếu chỉ dẫn tiền JSON. Không sửa skill để khớp check đánh giá. Trước phiên mới đã biết kết quả đánh giá cũ; việc tạo tag mới không xóa sự tiếp xúc này, nên không gọi đây là một đánh giá mù lần đầu.

## 9. Hạn chế và tính hợp lệ

1. Đã biết đánh giá phiên trước: giả thuyết gốc giữ nguyên nhưng phiên tiếp tục không đăng ký mù; kết quả mới không khôi phục lịch sử thí nghiệm ban đầu.
2. Curator chỉ có feedback data-learn OpenRouter; skill chuyển sang Gemini, chưa kiểm tra học từ đủ ba họ tác vụ. Không thể kết luận hiệu quả mọi quy ước.
3. Ba task/vai trò và một cặp development/chính thức; temperature 0 vẫn có nhiễu, không đủ suy rộng hoặc kết luận ý nghĩa thống kê.
4. Sáu baseline/subagents học được giữ từ phiên trước, cùng tham số nhưng khác thời điểm; task và model chỉ có một bộ, hạn chế so sánh nhân quả.
5. Trace chỉ luồng chính, cắt nội dung dài; không thấy đầy đủ công việc subagent, không lấy lời báo hoàn thành làm bằng chứng duy nhất.
6. Dữ liệu/quy ước do giảng viên thiết kế, skill schema có thể quá khớp; kết quả lab không chứng minh lợi ích trên dự án thực tế.

## 10. Kết luận

Đã lưu {len(runs)}/18 lượt chính và {len(devs)}/3 development trên cùng model/cap với skill nguyên bản. Điểm và chi phí lấy từ bảng hiện có; kết luận cơ chế dựa vào trace và check. Quy trình Git mới chỉ xác nhận các lượt sau tag mới, không sửa lịch sử trước đó. Bước tiếp theo là lặp nhiều lần và dùng bộ đánh giá mới chưa quan sát, nếu muốn kiểm định chuyển giao mù.

## Phụ lục: tái lập và lịch sử

REPRODUCE.md có lệnh và các bước archive → development → hypotheses commit → freeze commit/tag → official → verifier/compare/report. Không gọi curator thêm, không push, không sửa tests/tasks/scripts/module có sẵn. Các hồ sơ cũ nằm riêng; HYPOTHESES.md, REPORT-before-eval.md, freeze.json và artifact curator ban đầu được giữ nguyên. Bonus chưa thực hiện.
"""
    (report / "REPORT.md").write_text(content, encoding="utf-8")
    summary = dict(timestamp=datetime.now(timezone.utc).isoformat(), study=plan["study"], primary_runs=len(runs),
                   development_runs=len(devs), pairs=pairs, breakdown=breakdown,
                   missing=[dict(condition=c,task=t.id) for c in ("baseline","subagents","skills-auto") for t in list_tasks() if (c,t.id) not in by_key],
                   errors=[dict(condition=r["condition"],task=r["task"],error=r["error"]) for r in runs if r["error"]])
    (report / "git-study-summary.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(f"Report generated from {len(runs)} primary runs and {len(devs)} development runs")


if __name__ == "__main__":
    main()
