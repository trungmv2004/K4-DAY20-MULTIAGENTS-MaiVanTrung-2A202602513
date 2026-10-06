"""Write the final continuation report from saved observations and frozen evidence."""
import json
import re
from collections import Counter
from datetime import datetime

from lab.compare import load_runs
from lab.tasks import ROOT


def main():
    report = ROOT / "report"
    runs = load_runs(ROOT / "results")
    summary = json.loads((report / "gemini-summary.json").read_text(encoding="utf-8"))
    plan = json.loads((report / "gemini-plan.json").read_text(encoding="utf-8"))
    frozen = json.loads((report / "freeze.json").read_text(encoding="utf-8"))
    table = (report / "table.md").read_text(encoding="utf-8").strip()
    lines = []
    add = lines.append
    add("# Báo cáo Lab: Self evolving Agentic — phiên tiếp tục Gemini\n")
    add("Ngày thực hiện: 06/10/2026, Asia/Bangkok. Kết quả OpenRouter được giữ riêng trong `results/openrouter/` và `report/openrouter/`. Báo cáo này dùng các lượt Gemini cùng model/cap ở ba điều kiện chính; skill vẫn là đầu ra nguyên văn của curator OpenRouter, không sinh lại sau khi đã xem đánh giá.\n")
    add("## 1. Thông tin và cấu hình\n")
    add("| Họ tên | Mã sinh viên | Phần thực hiện |\n|---|---|---|\n| Mai Văn Trung (theo tên kho) | 2A202602513 | Harness, thực nghiệm và báo cáo với trợ lý Codex |\n")
    add(f"- Model đang dùng: `{plan['model']}`, Gemini Developer API; temperature 0, recursion limit {plan['recursion_limit']}. Python 3.12.15, Deep Agents 0.7.21, langchain-google-genai 4.4.0; Docker Linux trên Windows/WSL2. Cấu hình trước lượt Gemini ở [gemini-plan.json](gemini-plan.json).\n- Đã lưu **{summary['selected_runs']}/18** lượt chính, **{summary['error_free_runs']}** không có lỗi thực thi. Không có lỗi thực thi không đồng nghĩa đạt toàn bộ check. Ngân sách Gemini đo được: **{summary['budget']['task_attempts']}** lượt task, **{summary['budget']['task_tokens']:,}** token; gồm lượt lặp và lỗi, loại bản sao trùng. Probe 3.8 dùng 56 token. Lượt bị dừng để sửa cô lập chưa có run.json nên token của nó không đo được; tổng trên là cận dưới.\n- `.env` giữ hai khóa, kích hoạt `GEMINI_API_KEY` qua `LAB_MODEL`; ba biến Azure/OpenAI để trống vì factory có sẵn ưu tiên chúng. Không sửa `model.py`. Shell không kế thừa khóa, chạy UID 65534, không đọc được thư mục chứa khóa/check ẩn hoặc môi trường runner; [shell-isolation.json](shell-isolation.json) đạt.\n- Không commit, push hoặc tạo tag theo yêu cầu người dùng. Không đạt tiêu chí commit `hypotheses`/tag `freeze` của rubric; mốc SHA-256 cục bộ chỉ bổ sung chứng cứ.\n")
    add("## 2. Giả thuyết trước đánh giá\n")
    add("[HYPOTHESES.md](HYPOTHESES.md) và [REPORT-before-eval.md](REPORT-before-eval.md) được giữ nguyên từ trước đánh giá OpenRouter. Không đăng ký lại sau khi biết điểm.\n\n- H1: Subagents không tăng điểm đánh giá rõ, nhưng tăng token vì phân vai không cung cấp quy ước Acme ẩn. [Anthropic](https://www.anthropic.com/engineering/multi-agent-research-system) là căn cứ về lợi ích/chi phí chia việc, không chứng minh lợi ích trên lab nhỏ.\n- H2: Skills-auto có khả năng cao nhất nếu phản hồi học được tổng quát hóa đúng; quy ước mới có thể chưa được bao phủ. [SkillsBench](https://arxiv.org/abs/2602.12670) nghiên cứu lợi ích skill, không bảo đảm curator của lab tạo skill tốt.\n- H3: Mức tăng do skill trên học dự đoán lớn hơn hoặc bằng trên đánh giá. [SkillEvolBench](https://arxiv.org/abs/2605.24117) là căn cứ cần phân biệt thích nghi cục bộ với chuyển giao.\n\nGemini là phép chuyển giao skill giữa model trong phiên tiếp tục. Các sai khác protocol gốc vẫn tồn tại, nên đây không phải kiểm chứng đăng ký trước hoàn chỉnh cho model mới.\n")
    add("## 3. Làm quen Deep Agents\n")
    add("Tour ngoại tuyến ở [tour.txt](tour.txt). Model thấy `ls`, `read_file`, `write_file`, `edit_file`, `delete`, `glob`, `grep`, `execute`, `task`; `execute` chạy shell. `general-purpose` có các công cụ tương tự, chỉ nhận prompt giao việc và trả về báo cáo cuối, nên agent chính phải truyền đủ đề/quy tắc/đường dẫn. Chế độ single vẫn có subagent mặc định.\n\nMô tả `task`: “Put full detail in the prompt and state exactly what it should return”. Mô tả `execute`: “Use absolute paths and avoid `cd` so the working directory stays stable”. Harness giữ nguyên prompt đề bài và quy ước shell tương đối `workspace/...`; file tools dùng gốc ảo. Không dùng tour làm bằng chứng đã gọi model thật.\n")
    add("## 4. Đường cơ sở và phân loại lỗi\n")
    add("Chỉ dùng baseline **học** dưới đây. Feedback lỗi chỉ xuất hiện ở task học; không đọc đáp án/bộ chấm đánh giá để sinh skill.\n\n| Task | Check trượt | Nhóm | Bằng chứng từ detail |\n|---|---|---|---|")
    for run in runs:
        if run["condition"] == "baseline" and run["role"] == "learn":
            for check in run["checks"]:
                if not check["passed"]:
                    group = "E" if check["name"].startswith("rule_") else "G (lượt lỗi)" if run["error"] else "A–D, cần đối chiếu vết"
                    detail = check["detail"].replace("\n", " ").replace("|", "\\|")[:260]
                    add(f"| {run['task']} | {check['name']} | {group} | {detail} |")
    baseline = next((b for b in summary["breakdown"] if b["condition"] == "baseline" and b["role"] == "learn"), None)
    if baseline:
        add(f"\nBaseline học đạt **{baseline['technical_passed']}/{baseline['technical_total']} kỹ thuật**, **{baseline['rules_passed']}/{baseline['rules_total']} quy ước**. Các check kỹ thuật đạt là bằng chứng phủ định lỗi A–D trong phạm vi những check này; không suy ra agent luôn tránh lỗi đó. Skill quy ước có thể giúp E nếu bao phủ đúng và được áp dụng.\n")
    add("Vết code học ghi sửa hàm dùng chung theo docstring và chạy pytest; baseline dữ liệu thử pandas/dateutil chưa có, rồi chuyển sang thư viện chuẩn, tạo answer.json và đọc lại. Các lỗi trung gian được sửa không được gọi là lỗi thực thi cuối lượt. Xem `results/baseline/*/trace.md`; mọi nhận xét cuối phải đối chiếu điểm chấm thực tế.\n")
    add("## 5. Điều kiện subagents\n")
    add("Explorer đọc đặc tả và tìm nguyên nhân; implementer thực hiện thay đổi có phạm vi và kiểm chứng; reviewer kiểm tra độc lập, không sửa. Mỗi vai trò nhận nguyên PATHS_NOTE; agent chính nhận nguyên SUBAGENTS_NOTE.\n\n| Task | Gọi task | Loại subagent thấy trong vết chính | Token | Giây |\n|---|---|---|---|---|")
    for run in runs:
        if run["condition"] == "subagents":
            trace = (ROOT / "results/subagents" / run["task"] / "trace.md").read_text(encoding="utf-8")
            names = Counter(re.findall(r'"subagent_type"\s*:\s*"([^"]+)"', trace))
            add(f"| {run['task']} | {run['subagent_calls']} | {dict(names) if names else 'Không giao việc'} | {run['tokens']['total']:,} | {run['seconds']} |")
    add("\n`subagent_calls = 0` là kết quả hợp lệ, không có nghĩa harness thiếu công cụ. Vết chỉ chứa luồng chính; không quan sát đầy đủ công việc bên trong subagent. Số token callback có cộng các lời gọi model bên trong. Khi có giao việc, dùng prompt/báo cáo được lưu để kiểm tra đủ quy tắc và agent chính có kiểm chứng hay chưa; không giả định thiết kế ba vai trò bảo đảm cả ba đều được dùng.\n")
    if len([r for r in runs if r["condition"] == "subagents"]) == 6:
        add("Hai lần giao việc đều cho `general-purpose`; chưa có lượt thật chọn explorer/implementer/reviewer. Điều kiện này quan sát việc thêm vai trò và lời nhắc giao việc, nên chưa ước lượng được lợi ích khi ba vai trò chuyên biệt đó được sử dụng.\n")
    data_sub = next((r for r in runs if r["condition"] == "subagents" and r["task"] == "data-learn"), None)
    if data_sub:
        failed = {c["name"] for c in data_sub["checks"] if not c["passed"]}
        if "north_q1_revenue" in failed:
            add("Ví dụ quan sát: subagents/data-learn giao cho `general-purpose`, truyền quy tắc loại trùng, sentinel -999, chuẩn hóa vùng/ngày và các trường kết quả. Báo cáo trả revenue 3189.59; baseline học tính 3130.24 và qua check revenue, còn lượt subagent trượt check này. Agent chính đọc lại output/input nhưng vết không ghi phép tính kiểm chứng độc lập sửa được sai lệch. Nội dung giao việc không nhắc câu Acme review bot trong đề; các quy ước ẩn vẫn chưa được cung cấp. Đây là bằng chứng một báo cáo subagent có thể sai dù lời giao việc dài.\n")
    data_eval_sub = next((r for r in runs if r["condition"] == "subagents" and r["task"] == "data-eval"), None)
    if data_eval_sub and data_eval_sub["passed"] == 3:
        add("Ở subagents/data-eval, lời giao việc cũng ghi rõ chuyển UTC để xác định tháng. Subagent báo đã chuyển UTC; agent chính đọc output rồi chạy tính lại bằng `datetime.fromisoformat` và kiểm tra `dt.month == 3` mà không chuyển `astimezone(timezone.utc)`. Check doanh thu và số đơn tháng UTC đều trượt. Đây là nhóm D và kiểm chứng chưa đủ: tính lại cùng cách sai không xác nhận tính đúng.\n")
    add("## 6. Self-evolving: skill do curator sinh\n")
    add("Curator đã gọi **3 lần** trên OpenRouter, đạt giới hạn một lần đầu và hai lần chạy lại của GUIDE. Chỉ feedback/vết baseline data-learn không có lỗi thực thi được đưa vào prompt; các task học bị lỗi bị loại. Không dùng lượt Gemini hoặc tập đánh giá để thay skill đã đóng băng.\n\n| Lần | Kết quả | Lựa chọn |\n|---|---|---|\n| 1 | Ba tên chứa underscore bị validator chặn | Làm rõ regex trong prompt, không sửa output |\n| 2 | Ba skill hợp lệ định dạng | Loại skill đường dẫn vì khuyên `/workspace` trong shell; loại skill tiền vì khuyên float/round để chống sai số |\n| 3 | Bị chặn từ `orders`, là marker theo validator | Không sửa validator; chọn lại nguyên văn skill hợp lệ của lần 2 |\n\n[skill-review.json](skill-review.json), `curator-attempt-{1,2,3}/` giữ prompt/phản hồi/token và bản gốc. Chọn lại artifact cũ không phải viết tay skill.\n\n| Skill | Phạm vi và tính đúng | Độ dài/kích hoạt |\n|---|---|---|\n| produce-answer-and-clean-csv | Quy trình meta, loại trùng, UTC, CSV từ feedback học; không chứa tên input đánh giá. Schema region và ví dụ Q1 có rủi ro quá khớp. Thiếu chỉ dẫn rõ về tiền JSON và tham chiếu money-conversion chưa định nghĩa quy tắc làm tròn | 23 dòng toàn tệp, 19 dòng body; description `Use when` nhắm answer.json/meta/clean.csv |\n\nDevelopment gốc OpenRouter data-learn 0/8 bị cắt ở 16 bước, đã đọc một skill; lưu trong `results/openrouter/skills-auto-dev/`. **Không so nó với Gemini để đo nhiễu.** Lượt Gemini ở `results/gemini-repeat/skills-auto/` và lượt chính cùng skill/model/cap đều sau freeze gốc, chỉ là lặp học bổ sung.\n")
    add("## 7. Kết quả so sánh và đóng băng\n")
    add(table + "\n")
    add("Bảng do module compare có sẵn sinh, chỉ đọc ba condition cấp gốc. Lượt lặp, thử bị lỗi/thay model và OpenRouter được lưu riêng, không trộn vào bảng.\n\n| Condition | Role | Lượt/lỗi | Kỹ thuật | Quy ước | Token TB | Giây TB | Lượt đọc skill |\n|---|---|---|---|---|---|---|---|")
    for b in summary["breakdown"]:
        add(f"| {b['condition']} | {b['role']} | {b['runs']}/{b['errors']} | {b['technical_passed']}/{b['technical_total']} | {b['rules_passed']}/{b['rules_total']} | {int(b['mean_tokens']):,} | {b['mean_seconds']:.1f} | {b['runs_read_skill']}/{b['runs']} |")
    add("\nThống kê đầy đủ ở [observed-breakdown.json](observed-breakdown.json). Script `check_breakdown.py` gốc vẫn ẩn đánh giá vì không có tag; giữ nguyên script và lưu đầu ra tại [check_breakdown.txt](check_breakdown.txt).\n")
    if summary["retry"]:
        add("Lượt chính có lỗi thực thi, không dùng mọi check trượt của chúng để suy ra lỗi năng lực: " + ", ".join(f"`{r['condition']}/{r['task']}`" for r in summary["retry"]) + ". Lỗi đầy đủ trong run.json và [remaining-work.json](remaining-work.json).\n")
    else:
        add("Các lượt chính đã lưu không có lỗi thực thi. Lượt bị thay thế/lỗi API giữ dưới `results/gemini-attempts/` và `results/gemini-3.8-flash/`, không bị xóa.\n")
    add(f"Freeze cục bộ lúc `{frozen['timestamp']}`; hash skill `{frozen['skills_sha256']}`. Hash giả thuyết và skill gốc không đổi; đối chiếu [local_freeze_check.txt](local_freeze_check.txt), [check-status.json](check-status.json). `verify_freeze.py` gốc không đạt do không có Git commit/tag, kể cả khi kiểm tra cục bộ đạt.\n")
    add("## 8. Phân tích\n")
    complete = len(runs) == 18 and not summary["retry"]
    if complete:
        means = {(b["condition"], b["role"]): b["mean_score"] for b in summary["breakdown"]}
        for condition in ("subagents", "skills-auto"):
            learning = means[(condition, "learn")] - means[("baseline", "learn")]
            evaluation = means[(condition, "eval")] - means[("baseline", "eval")]
            add(f"- **{condition}:** chênh baseline học {learning:+.3f}, đánh giá {evaluation:+.3f} trên thang 0–1. Đây là mô tả một lượt/mỗi task, không phải kiểm định thống kê hoặc hiệu ứng nhân quả chắc chắn.")
        evaluations = {c: means[(c, "eval")] for c in ("baseline", "subagents", "skills-auto")}
        best = [c for c, score in evaluations.items() if score == max(evaluations.values())]
        skill_learn = means[("skills-auto", "learn")] - means[("baseline", "learn")]
        skill_eval = means[("skills-auto", "eval")] - means[("baseline", "eval")]
        h2 = "có cải thiện điểm so baseline trong số liệu này" if skill_eval > 0 else "chưa được hỗ trợ về lợi ích: skills-auto hòa baseline" if skill_eval == 0 else "không được hỗ trợ: skills-auto thấp hơn baseline"
        add(f"- **Giả thuyết:** điểm đánh giá cao nhất quan sát được ở {', '.join(best)}. H2 {h2}; đồng hạng không chứng minh skill có lợi. H3 {'phù hợp với' if skill_learn >= skill_eval else 'không phù hợp với'} hai mức tăng quan sát ({skill_learn:+.3f} học, {skill_eval:+.3f} đánh giá). H1 cần đọc đồng thời điểm và chi phí, vì việc thêm vai trò không bảo đảm agent chọn vai trò đó.")
        if skill_learn > 0 and skill_eval <= 0:
            add("Điểm học tăng nhưng đánh giá không tăng là dấu hiệu chuyển giao yếu. Trong vết hiện có, skill còn thiếu hướng dẫn tiền JSON và model không làm đúng quy tắc meta/UTC; chưa đủ để quy toàn bộ chênh lệch cho quá khớp nội dung skill.")
    else:
        add(f"- **Độ phủ:** còn {len(summary['missing'])} lượt chưa chạy, {len(summary['retry'])} lượt chính cần chạy lại. Trung bình chỉ mô tả các lượt đã có; chưa đủ để kết luận toàn bộ H1–H3.")
    add("- **Kỹ thuật/quy ước:** dùng phân tách mục 7, không quy mọi tăng điểm cho skill. Đọc skill chỉ chứng minh nạp nội dung, không chứng minh tuân thủ hoặc nhân quả. Các check mới trong đánh giá không được đưa vào skill sau freeze. Bảng check cụ thể dưới đây đối chiếu skills-auto với baseline; ô trống nghĩa thiếu lượt.")
    add("\n| Task dữ liệu | Check | Baseline | Skills-auto |\n|---|---|---|---|")
    by_key = {(r["condition"], r["task"]): r for r in runs}
    for task in ("data-learn", "data-eval"):
        base = by_key.get(("baseline", task))
        skilled = by_key.get(("skills-auto", task))
        checks = {c["name"] for r in (base, skilled) if r for c in r["checks"]}
        for name in sorted(checks):
            values = []
            for r in (base, skilled):
                check = next((c for c in r["checks"] if c["name"] == name), None) if r else None
                values.append("đạt" if check and check["passed"] else "trượt" if check else "—")
            add(f"| {task} | {name} | {' | '.join(values)} |")
    learning_skill = by_key.get(("skills-auto", "data-learn"))
    evaluation_skill = by_key.get(("skills-auto", "data-eval"))
    if learning_skill and any(c["name"] == "rule_meta_block" and c["passed"] for c in learning_skill["checks"]):
        add("\nVí dụ đạt sau khi dùng skill: `rule_meta_block` ở data-learn; baseline không có meta, skills-auto tạo source/rows_in/rows_used và qua check. Vết ghi rows_in=101, rows_used=86, bám hướng dẫn đếm đơn có tiền biết được. Đây là thay đổi phù hợp với nội dung skill, với giới hạn một lượt baseline.")
        add("Ví dụ không làm đúng dù đã đọc: CSV data-learn được tạo và đọc lại nhưng vẫn trượt `rule_clean_csv`. Vết input có S-1032 tại `2024-01-07T23:15:00-05:00`, còn CSV ghi `2024-01-07T23:15:00Z`; chuyển UTC đúng phải là `2024-01-08T04:15:00Z`. Gắn Z mà giữ nguyên giờ địa phương không thực hiện chỉ dẫn chuyển UTC của skill. Check có thể còn lý do khác; vết này đủ chứng minh một lỗi cụ thể.")
    if evaluation_skill and evaluation_skill["passed"] == 5:
        add("Ở data-eval, agent đã đọc skill nhưng `rule_meta_block` vẫn trượt: vết answer.json ghi rows_in=88 và rows_used=83, cùng kết quả 5 duplicate và 7 đơn thiếu tiền. Skill yêu cầu chỉ đếm đơn có tiền biết được, tức 88−5−7=76, nên rows_used=83 cho thấy không làm theo quy tắc này. `rule_clean_csv` cũng trượt; vết/câu trả lời cuối không chứng minh đã kiểm chứng một CSV hợp lệ. Skill không yêu cầu rõ tiền trong answer.json thành integer cents, và không bao phủ check mới `rule_sorted_keys_format`; cả hai vẫn trượt. Giữ nguyên skill thay vì chỉnh theo phản hồi đánh giá.")
    for run in (learning_skill, evaluation_skill):
        if run:
            trace = (ROOT / "results/skills-auto" / run["task"] / "trace.md").read_text(encoding="utf-8")
            calls = re.findall(r"^### Tool call: ([^\n]+)\n([^\n]+)", trace, re.MULTILINE)
            positions = [i + 1 for i, (name, arguments) in enumerate(calls)
                         if name == "read_file" and "skills/" in arguments]
            add(f"Vết {run['task']}: đọc skill ở tool call {positions}; tool call đầu là `{calls[0][0] if calls else 'không có'}`. skills_read={run['skills_read']} chứng minh đã đọc, nhưng chưa làm đúng yêu cầu FIRST action khi có công cụ khác trước đó.")
    add("\n- **Chi phí:** điểm TB trên mỗi 10.000 token dùng các lượt chính cùng model; bảng dưới có thể chứa điểm của lượt lỗi nếu có. Chỉ so điều kiện khi cùng độ phủ. Không chuyển token thành tiền vì tier/billing/cache có thể khác.")
    add("\n| Condition | Lượt | Token TB | Điểm TB | Điểm / 10.000 token |\n|---|---|---|---|---|")
    for condition in ("baseline", "subagents", "skills-auto"):
        selected = [r for r in runs if r["condition"] == condition]
        if selected:
            mean_tokens = sum(r["tokens"]["total"] for r in selected) / len(selected)
            mean_score = sum(r["score"] for r in selected) / len(selected)
            efficiency = mean_score * 10000 / mean_tokens if mean_tokens else 0
            add(f"| {condition} | {len(selected)} | {int(mean_tokens):,} | {mean_score:.3f} | {efficiency:.4f} |")
    if complete:
        baselines = [r for r in runs if r["condition"] == "baseline"]
        subs = [r for r in runs if r["condition"] == "subagents"]
        token_ratio = sum(r["tokens"]["total"] for r in subs) / sum(r["tokens"]["total"] for r in baselines)
        score_delta = sum(r["score"] for r in subs) / 6 - sum(r["score"] for r in baselines) / 6
        add(f"\nSubagents dùng {token_ratio:.2f} lần token baseline, chênh điểm TB toàn bộ task {score_delta:+.3f}. {'Chi phí tăng chưa được bù bằng cải thiện điểm quan sát.' if token_ratio > 1 and score_delta <= 0 else 'Cần cân nhắc cả chênh điểm và chi phí; một lượt chưa đủ chứng minh lợi ích ổn định.'} H1 {'phù hợp về hướng trong số liệu này' if token_ratio > 1 and evaluations['subagents'] <= evaluations['baseline'] else 'chưa được hỗ trợ đầy đủ về hướng dự đoán'}, với giới hạn chọn subagent/nhiễu đã nêu.")
    add("\n- **Rò rỉ/quá khớp:** skill vẫn khớp byte với artifact curator và validator gốc. Curator không nhận dữ liệu đánh giá; không sửa skill sau quan sát. Schema region cố định là rủi ro chuyển giao sang dữ liệu category; xem vết dữ liệu đánh giá để kiểm tra tác động. Việc validator chặn từ chung `orders` không tự chứng minh đã đọc tập đánh giá.\n- **Nhiễu:** các lặp Gemini dưới đây cùng skill/model/cap. Một cặp/task chỉ cho thấy biến động quan sát, không đủ ước lượng khoảng tin cậy; đều sau freeze gốc nên không thay thế development đầy đủ theo GUIDE.\n")
    add("| Task | Lặp học bổ sung | Lượt chính | Chênh điểm chính − lặp | Token lặp / chính |\n|---|---|---|---|---|")
    for repeat in summary["repeats"]:
        official = "—" if repeat["official_score"] is None else f"{repeat['official_score']:.3f}"
        delta = "—" if repeat["delta"] is None else f"{repeat['delta']:+.3f}"
        tokens = f"{repeat['repeat_tokens']:,} / {repeat['official_tokens']:,}" if repeat['official_tokens'] is not None else f"{repeat['repeat_tokens']:,} / —"
        add(f"| {repeat['task']} | {repeat['repeat_score']:.3f} | {official} | {delta} | {tokens} |")
    if complete and all(r["delta"] == 0 for r in summary["repeats"]):
        add("\nBa cặp học đều chênh điểm 0 với cùng skill; không có biến động điểm quan sát trong cặp này. Token vẫn biến động: data-learn từ 69.076 lên 205.500 (khoảng 2,98 lần), dù đều 6/8. Vì vậy điểm ổn định ở một cặp không chứng minh chi phí ổn định, và các chênh token nhỏ giữa condition cần được kiểm chứng bằng nhiều lượt lặp.")
    add("\n## 9. Hạn chế và tính hợp lệ\n")
    add("1. **Protocol gốc chưa đủ trước freeze:** thiếu baseline/subagents học và development code/logs trước curator/freeze; bổ sung Gemini không thể sửa lịch sử đó. Skill chỉ học từ feedback data-learn OpenRouter.\n2. **Đổi model:** bảng mới giữ model/cap thống nhất, nhưng skill đến từ model khác. Không trộn hoặc so chênh token OpenRouter/Gemini như hiệu ứng skill.\n3. **Quy mô/nhiễu:** ba task mỗi role, một lượt chính mỗi condition/task và tối đa một lặp skill học; temperature 0 không bảo đảm lặp y hệt. Không khái quát sang mọi model hoặc công việc thực tế.\n4. **Git:** yêu cầu không commit/push được ưu tiên; không có chứng cứ commit/tag theo rubric. Freeze cục bộ chỉ kiểm tra thời gian/hash và trạng thái run.\n5. **Hạ tầng/quota:** 3.8 Flash bị quota 20/ngày; lượt đầu bị chủ động dừng sau khi shell liệt kê kho mount. Vết không thấy đọc `.env`, protected files không đổi, nhưng token lượt bị dừng không đo được. Shell đã được cô lập và kiểm chứng trước mọi lượt mới.\n6. **Vết giới hạn:** render_trace chỉ giữ luồng chính và cắt nội dung ở 1.500 ký tự; không khẳng định đã quan sát toàn bộ mã/script hoặc công việc bên trong subagent. Chuẩn hóa CRLF chỉ thực hiện trên Python trong bản sao sandbox.\n")
    add("## 10. Kết luận\n")
    add(f"Harness đạt 29 test ngoại tuyến, kiểm tra cô lập shell đạt và phiên Gemini lưu {summary['selected_runs']}/18 lượt chính, {summary['error_free_runs']} lượt không lỗi thực thi. Skill giữ nguyên sau freeze giúp qua meta trên data-learn (6/8 so baseline 5/8), còn điểm đánh giá TB vẫn bằng baseline (0,597). Subagents đạt điểm đánh giá thấp hơn (0,523) và dùng 1,44 lần tổng token baseline; hai lần giao việc chỉ dùng general-purpose. Kết quả mô tả phép chuyển giao skill với protocol gốc chưa đầy đủ và thiếu commit/tag theo chỉ dẫn người dùng. Bước tiếp theo nên là thí nghiệm mới tách dữ liệu, đủ học/development trước freeze và nhiều lượt lặp, giữ nguyên lịch sử phiên này.\n")
    add("## Phụ lục: lệnh, artifact và phần còn thiếu\n")
    add("Thứ tự: kiểm tra danh sách model/probe 3.8; lưu plan và tách OpenRouter; dừng lượt mount chưa cô lập; kiểm chứng shell UID riêng; 3.8 báo quota ngày; chuyển 3.1 Flash-Lite và chạy tuần tự học baseline/subagents, lặp skill học, đánh giá baseline/subagents, skill cả sáu task; summarize/compare; kiểm tra freeze và protected files. Không chạy curator thêm, không thực hiện bonus 6e (cần hai lần lặp thêm trên mọi condition/eval).\n\n[REPRODUCE.md](REPRODUCE.md) có lệnh tái chạy; [remaining-work.json](remaining-work.json) giữ danh sách thiếu/lỗi; [gemini-summary.json](gemini-summary.json) giữ thống kê/budget; [protected-file-check.json](protected-file-check.json) kiểm tra tệp/hàm được bảo vệ; [pytest.txt](pytest.txt) giữ kết quả test. `report/REPORT.md` và `table.md` được sinh từ run.json thật; không thêm điểm cho lượt chưa chạy.\n")
    (report / "REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Report written: {len(runs)} observed primary runs.")


if __name__ == "__main__":
    main()
