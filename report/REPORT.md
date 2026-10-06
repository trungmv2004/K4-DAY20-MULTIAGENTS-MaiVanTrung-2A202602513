# Báo cáo Lab: Self evolving Agentic — hoàn thiện Git freeze

Ngày: 06/10/2026, Asia/Bangkok. Phiên cũ được giữ ở `results/pre-git-freeze/` và `report/pre-git-freeze/`. Người dùng đã cho phép commit/tag freeze; không push. Skill curator OpenRouter giữ nguyên byte. Phiên này sửa bằng chứng trình tự chạy và bổ sung phân tích, không tuyên bố chưa từng thấy đánh giá trước đây.

## 1. Thông tin nhóm và cấu hình

| Họ tên | Mã sinh viên | Phần thực hiện |
|---|---|---|
| Mai Văn Trung | 2A202602513 | Harness, thí nghiệm và báo cáo với trợ lý Codex |

- Model `google_genai:gemini-3.1-flash-lite`, Gemini Developer API, temperature 0, recursion limit 60. Python 3.12.15, Deep Agents 0.7.21, langchain-google-genai 4.4.0; Docker Linux trên Windows.
- Cấu hình shell UID 65534, không kế thừa khóa, không đọc thư mục runner/check ẩn. Xem shell-isolation.json và REPRODUCE.md. `.env` được ignore.
- Có 6/18 lượt chính, 6 không lỗi thực thi; development mới 3/3. Sáu lượt baseline/subagents học được giữ từ trước tag, cùng model/cap, không chạy lại không cần thiết.
- Commit tag freeze: chưa tạo — bản nháp trước freeze. Commit hypotheses: sẽ commit sau khi đủ development. Kế hoạch: git-study-plan.json.

## 2. Giả thuyết trước tag freeze

Giả thuyết trước đánh giá

[HYPOTHESES.md](HYPOTHESES.md) và [REPORT-before-eval.md](REPORT-before-eval.md) được giữ nguyên từ trước đánh giá OpenRouter. Không đăng ký lại sau khi biết điểm.

- H1: Subagents không tăng điểm đánh giá rõ, nhưng tăng token vì phân vai không cung cấp quy ước Acme ẩn. [Anthropic](https://www.anthropic.com/engineering/multi-agent-research-system) là căn cứ về lợi ích/chi phí chia việc, không chứng minh lợi ích trên lab nhỏ.
- H2: Skills-auto có khả năng cao nhất nếu phản hồi học được tổng quát hóa đúng; quy ước mới có thể chưa được bao phủ. [SkillsBench](https://arxiv.org/abs/2602.12670) nghiên cứu lợi ích skill, không bảo đảm curator của lab tạo skill tốt.
- H3: Mức tăng do skill trên học dự đoán lớn hơn hoặc bằng trên đánh giá. [SkillEvolBench](https://arxiv.org/abs/2605.24117) là căn cứ cần phân biệt thích nghi cục bộ với chuyển giao.

Giữ các giả thuyết từ hồ sơ trước đánh giá ban đầu, không đổi chúng để khớp kết quả. Commit mới ghi lại nội dung này trước tag mới; do đã thấy kết quả phiên trước, đây là xác nhận lại giả thuyết có sẵn trong phiên tiếp tục, không phải đăng ký mù mới.

## 3. Làm quen Deep Agents

Làm quen Deep Agents

Tour ngoại tuyến ở [tour.txt](tour.txt). Model thấy `ls`, `read_file`, `write_file`, `edit_file`, `delete`, `glob`, `grep`, `execute`, `task`; `execute` chạy shell. `general-purpose` có các công cụ tương tự, chỉ nhận prompt giao việc và trả về báo cáo cuối, nên agent chính phải truyền đủ đề/quy tắc/đường dẫn. Chế độ single vẫn có subagent mặc định.

Mô tả `task`: “Put full detail in the prompt and state exactly what it should return”. Mô tả `execute`: “Use absolute paths and avoid `cd` so the working directory stays stable”. Harness giữ nguyên prompt đề bài và quy ước shell tương đối `workspace/...`; file tools dùng gốc ảo. Không dùng tour làm bằng chứng đã gọi model thật.

System prompt mặc định khi không truyền system_prompt là rỗng, như tour.txt thể hiện.

## 4. Đường cơ sở và phân loại lỗi

Đường cơ sở và phân loại lỗi

Chỉ dùng baseline **học** dưới đây. Feedback lỗi chỉ xuất hiện ở task học; không đọc đáp án/bộ chấm đánh giá để sinh skill.

| Task | Check trượt | Nhóm | Bằng chứng từ detail |
|---|---|---|---|
| code-learn | rule_type_hints | E | RULE: every public function (name not starting with '_') in the package has type annotations on all parameters and on the return value. |
| code-learn | rule_regression_tests | E | RULE: add tests/test_regressions.py with one test function per bug you fixed (at least 3); the file must pass. |
| code-learn | rule_changelog | E | RULE: record each fix in CHANGELOG.md under the heading '## Unreleased' as a bullet '- fix(<function name>): <short description>' (at least 3 bullets). |
| data-learn | rule_money_in_cents | E | RULE: money values in answer.json are integer cents (1606.67 USD is written 160667). |
| data-learn | rule_meta_block | E | RULE: answer.json has an object `meta` = {"source": <input file name>, "rows_in": <number of data rows in the input file, duplicates included>, "rows_used": <number of distinct orders with a known amount>}. |
| data-learn | rule_clean_csv | E | RULE: write workspace/clean.csv with the header order_id,timestamp_utc,region,amount_cents; one row per distinct order with a known amount; timestamp_utc as YYYY-MM-DDTHH:MM:SSZ (UTC); region in canonical spelling (North, South, East, West); amount in integer  |
| logs-learn | rule_service_names | E | RULE: service names in the output are lower-case with '-' replaced by '_' (payment-service -> payment_service). |
| logs-learn | rule_sorted_errors | E | RULE: `errors` is sorted by service, then by timestamp_utc, ascending. |
| logs-learn | rule_schema_header | E | RULE: the top-level object has "schema_version": 2 and "generated_by": "log-triage". |

Baseline học đạt **18/18 kỹ thuật**, **0/9 quy ước**. Các check kỹ thuật đạt là bằng chứng phủ định lỗi A–D trong phạm vi những check này; không suy ra agent luôn tránh lỗi đó. Skill quy ước có thể giúp E nếu bao phủ đúng và được áp dụng.

Vết code học ghi sửa hàm dùng chung theo docstring và chạy pytest; baseline dữ liệu thử pandas/dateutil chưa có, rồi chuyển sang thư viện chuẩn, tạo answer.json và đọc lại. Các lỗi trung gian được sửa không được gọi là lỗi thực thi cuối lượt. Xem `results/baseline/*/trace.md`; mọi nhận xét cuối phải đối chiếu điểm chấm thực tế.

## 5. Điều kiện subagents

Explorer đọc đặc tả và báo cáo, không sửa; implementer thực hiện có phạm vi và kiểm chứng; reviewer kiểm tra độc lập, không sửa. Description nêu tình huống giao việc; mỗi vai trò nhận PATHS_NOTE.

| Task | subagent_calls | Loại được giao trong vết | Token | Giây |
|---|---:|---|---:|---:|
| code-learn | 0 | Không thấy lời giao việc | 131,054 | 112.1 |
| data-learn | 1 | general-purpose | 231,970 | 124.3 |
| logs-learn | 0 | Không thấy lời giao việc | 56,977 | 39.1 |

subagent_calls=0 vẫn là kết quả hợp lệ: model có công cụ task nhưng có thể chọn xử lý trực tiếp. Những tác vụ nhỏ có thể không cần phân vai; đây là giải thích khả dĩ, không xác nhận suy nghĩ nội bộ. Trace chỉ lưu luồng chính, callback token có cộng model call bên trong subagent. Phân tích giao việc cụ thể được bổ sung ở mục 8 từ prompt/báo cáo lưu trong trace mới.

## 6. Skill curator và development trước freeze

Self-evolving: skill do curator sinh

Curator đã gọi **3 lần** trên OpenRouter, đạt giới hạn một lần đầu và hai lần chạy lại của GUIDE. Chỉ feedback/vết baseline data-learn không có lỗi thực thi được đưa vào prompt; các task học bị lỗi bị loại. Không dùng lượt Gemini hoặc tập đánh giá để thay skill đã đóng băng.

| Lần | Kết quả | Lựa chọn |
|---|---|---|
| 1 | Ba tên chứa underscore bị validator chặn | Làm rõ regex trong prompt, không sửa output |
| 2 | Ba skill hợp lệ định dạng | Loại skill đường dẫn vì khuyên `/workspace` trong shell; loại skill tiền vì khuyên float/round để chống sai số |
| 3 | Bị chặn từ `orders`, là marker theo validator | Không sửa validator; chọn lại nguyên văn skill hợp lệ của lần 2 |

[skill-review.json](skill-review.json), `curator-attempt-{1,2,3}/` giữ prompt/phản hồi/token và bản gốc. Chọn lại artifact cũ không phải viết tay skill.

| Skill | Phạm vi và tính đúng | Độ dài/kích hoạt |
|---|---|---|
| produce-answer-and-clean-csv | Quy trình meta, loại trùng, UTC, CSV từ feedback học; không chứa tên input đánh giá. Schema region và ví dụ Q1 có rủi ro quá khớp. Thiếu chỉ dẫn rõ về tiền JSON và tham chiếu money-conversion chưa định nghĩa quy tắc làm tròn | 23 dòng toàn tệp, 19 dòng body; description `Use when` nhắm answer.json/meta/clean.csv |

Development mới ở `results/skills-auto-dev/<task>/`; ba lượt này dùng skill nguyên bản, cùng Gemini/model/cap với lượt chính. Không chạy curator thêm, không thay skill sau khi đã xem đánh giá. Phiên cũ có development chưa đủ; không dùng nó để đo nhiễu trên model mới.

| Task | Development trước freeze | Chính thức sau freeze | Δ điểm | Token dev / chính thức | skills_read dev / chính thức |
|---|---|---|---:|---|---|
| code-learn | 7/10 | Chưa chạy | — | 149,808 / — | 0 / — |
| data-learn | 6/8 | Chưa chạy | — | 68,937 / — | 1 / — |
| logs-learn | 6/9 | Chưa chạy | — | 49,858 / — | 0 / — |

### Vì sao bốn lượt trước không đọc skill

Đối chiếu phiên trước tại `results/pre-git-freeze/skills-auto/`: cả bốn lượt dưới đây có `skills_read=0`, trace không ghi `read_file` vào SKILL.md.

| Lượt cũ | Hành vi quan sát | Giải thích khả dĩ về kích hoạt |
|---|---|---|
| code-learn | Đọc mã/docstring, sửa pricing/report/export và chạy pytest | Skill chỉ nói answer.json/meta/clean.csv; không cung cấp quy ước type hints, regression tests hoặc changelog cho sửa mã |
| code-eval | Sửa bookings/billing, timeutil, schedule và chạy test | Đề yêu cầu sửa package; description không nhắm việc sửa mã, nên ít phù hợp với nhiệm vụ |
| logs-learn | Đọc app.log rồi ghi/đọc errors.json | Output là errors.json; skill yêu cầu order_id/region/amount_cents, không hướng dẫn service names, errors sorting hay schema log |
| logs-eval | Đọc worker.log rồi ghi/đọc errors.json | JSON triage log khác answer.json/meta/clean.csv; skill không bao phủ repeat_count/counts_by_service hoặc quy ước log mới |

Đây là suy luận từ description, đề bài và vết, không phải quan sát suy nghĩ nội bộ của model. Có công cụ nạp skill không bảo đảm model chọn đọc nó. Trong bốn lượt này không có bằng chứng skill giúp các check quy ước; UTC xuất hiện ở cả log và skill nhưng nội dung chưa được đọc. Không mở rộng description bằng tay hay tạo skill từ feedback đánh giá.

### Việc đọc skill trong lượt chính mới

| Lượt skills-auto mới | skills_read | Quan sát trong trace |
|---|---:|---|

## 7. Kết quả so sánh và đóng băng

| Task | baseline | subagents |
|---|---|---|
| code-learn | 7/10 | 7/10 |
| data-learn | 5/8 | 4/8 |
| logs-learn | 6/9 | 6/9 |
| **Mean score - learning tasks** | 0.66 | 0.62 |
| **Mean score - evaluation tasks** | - | - |
| **Mean tokens per run** | 84,529 | 140,000 |
| **Runs that read a skill** | 0/3 | 0/3 |

| Điều kiện | Vai trò | Kỹ thuật | Quy ước | Token TB |
|---|---|---|---|---:|
| baseline | learn | 18/18 | 0/9 | 84,529 |
| subagents | learn | 17/18 | 0/9 | 140,000 |

Hash skill `52427bc4ab4b6cac09d9544470d030f43135a9c624d60c5711b2806f3797890b`. Báo cáo không coi hash cục bộ là thay thế Git. Verifier gốc được chạy sau khi đủ lượt chính; kết quả lưu ở git-freeze-check.txt. Các lượt chính skills-auto phải sau thời điểm commit tag mới, các lượt development phải trước nó, hash/model/cap phải bằng nhau. Trạng thái thực tế: chưa tạo tag; chưa có lượt chính mới.

## 8. Phân tích

- subagents, learn: chênh baseline -0.042 trên thang 0–1.

Chỉ so sánh điều kiện sau khi có cùng độ phủ. Kết quả âm hoặc bằng nhau không làm mất giá trị thí nghiệm; không suy ra quan hệ nhân quả từ một lượt/task.

Các quan sát trace mới sẽ bổ sung sau khi chạy chính thức; chưa kết luận cơ chế từ điểm chưa có.

### Chi phí

| Condition | Số lượt | Điểm TB | Token TB | Điểm / 10.000 token |
|---|---:|---:|---:|---:|
| baseline | 3 | 0.664 | 84,529 | 0.0785 |
| subagents | 3 | 0.622 | 140,000 | 0.0444 |

Điểm/token được tính từ các lượt chính cùng model. Token không đồng nhất với tiền vì tier/cache/billing khác nhau. Dùng số lần gọi và trace để đánh giá chi phí giao việc, không mặc định đa tác tử hiệu quả hơn.

### Nhiễu development so với sau freeze

| Task | Development trước freeze | Chính thức sau freeze | Δ điểm | Token dev / chính thức | skills_read dev / chính thức |
|---|---|---|---:|---|---|
| code-learn | 7/10 | Chưa chạy | — | 149,808 / — | 0 / — |
| data-learn | 6/8 | Chưa chạy | — | 68,937 / — | 1 / — |
| logs-learn | 6/9 | Chưa chạy | — | 49,858 / — | 0 / — |

Chênh điểm chính thức trừ development trong ba cặp: chưa đủ cặp. Cùng skill/model/cap và không sửa skill, nên biến động giữa hai lần chạy là ước lượng nhiễu quan sát, không phải skill học thêm. Một cặp/task chưa đủ khoảng tin cậy hoặc kiểm định thống kê. Đối chiếu timestamp/hash nằm trong git-study-summary.json; không gán thay đổi token hoặc điểm cho curator mới.

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

Đã lưu 6/18 lượt chính và 3/3 development trên cùng model/cap với skill nguyên bản. Điểm và chi phí lấy từ bảng hiện có; kết luận cơ chế dựa vào trace và check. Quy trình Git mới chỉ xác nhận các lượt sau tag mới, không sửa lịch sử trước đó. Bước tiếp theo là lặp nhiều lần và dùng bộ đánh giá mới chưa quan sát, nếu muốn kiểm định chuyển giao mù.

## Phụ lục: tái lập và lịch sử

REPRODUCE.md có lệnh và các bước archive → development → hypotheses commit → freeze commit/tag → official → verifier/compare/report. Không gọi curator thêm, không push, không sửa tests/tasks/scripts/module có sẵn. Các hồ sơ cũ nằm riêng; HYPOTHESES.md, REPORT-before-eval.md, freeze.json và artifact curator ban đầu được giữ nguyên. Bonus chưa thực hiện.
