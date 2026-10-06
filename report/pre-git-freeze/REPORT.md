# Báo cáo Lab: Self evolving Agentic — phiên tiếp tục Gemini

Ngày thực hiện: 06/10/2026, Asia/Bangkok. Kết quả OpenRouter được giữ riêng trong `results/openrouter/` và `report/openrouter/`. Báo cáo này dùng các lượt Gemini cùng model/cap ở ba điều kiện chính; skill vẫn là đầu ra nguyên văn của curator OpenRouter, không sinh lại sau khi đã xem đánh giá.

## 1. Thông tin và cấu hình

| Họ tên | Mã sinh viên | Phần thực hiện |
|---|---|---|
| Mai Văn Trung (theo tên kho) | 2A202602513 | Harness, thực nghiệm và báo cáo với trợ lý Codex |

- Model đang dùng: `google_genai:gemini-3.1-flash-lite`, Gemini Developer API; temperature 0, recursion limit 60. Python 3.12.15, Deep Agents 0.7.21, langchain-google-genai 4.4.0; Docker Linux trên Windows/WSL2. Cấu hình trước lượt Gemini ở [gemini-plan.json](gemini-plan.json).
- Đã lưu **18/18** lượt chính, **18** không có lỗi thực thi. Không có lỗi thực thi không đồng nghĩa đạt toàn bộ check. Ngân sách Gemini đo được: **22** lượt task, **2,425,914** token; gồm lượt lặp và lỗi, loại bản sao trùng. Probe 3.8 dùng 56 token. Lượt bị dừng để sửa cô lập chưa có run.json nên token của nó không đo được; tổng trên là cận dưới.
- `.env` giữ hai khóa, kích hoạt `GEMINI_API_KEY` qua `LAB_MODEL`; ba biến Azure/OpenAI để trống vì factory có sẵn ưu tiên chúng. Không sửa `model.py`. Shell không kế thừa khóa, chạy UID 65534, không đọc được thư mục chứa khóa/check ẩn hoặc môi trường runner; [shell-isolation.json](shell-isolation.json) đạt.
- Không commit, push hoặc tạo tag theo yêu cầu người dùng. Không đạt tiêu chí commit `hypotheses`/tag `freeze` của rubric; mốc SHA-256 cục bộ chỉ bổ sung chứng cứ.

## 2. Giả thuyết trước đánh giá

[HYPOTHESES.md](HYPOTHESES.md) và [REPORT-before-eval.md](REPORT-before-eval.md) được giữ nguyên từ trước đánh giá OpenRouter. Không đăng ký lại sau khi biết điểm.

- H1: Subagents không tăng điểm đánh giá rõ, nhưng tăng token vì phân vai không cung cấp quy ước Acme ẩn. [Anthropic](https://www.anthropic.com/engineering/multi-agent-research-system) là căn cứ về lợi ích/chi phí chia việc, không chứng minh lợi ích trên lab nhỏ.
- H2: Skills-auto có khả năng cao nhất nếu phản hồi học được tổng quát hóa đúng; quy ước mới có thể chưa được bao phủ. [SkillsBench](https://arxiv.org/abs/2602.12670) nghiên cứu lợi ích skill, không bảo đảm curator của lab tạo skill tốt.
- H3: Mức tăng do skill trên học dự đoán lớn hơn hoặc bằng trên đánh giá. [SkillEvolBench](https://arxiv.org/abs/2605.24117) là căn cứ cần phân biệt thích nghi cục bộ với chuyển giao.

Gemini là phép chuyển giao skill giữa model trong phiên tiếp tục. Các sai khác protocol gốc vẫn tồn tại, nên đây không phải kiểm chứng đăng ký trước hoàn chỉnh cho model mới.

## 3. Làm quen Deep Agents

Tour ngoại tuyến ở [tour.txt](tour.txt). Model thấy `ls`, `read_file`, `write_file`, `edit_file`, `delete`, `glob`, `grep`, `execute`, `task`; `execute` chạy shell. `general-purpose` có các công cụ tương tự, chỉ nhận prompt giao việc và trả về báo cáo cuối, nên agent chính phải truyền đủ đề/quy tắc/đường dẫn. Chế độ single vẫn có subagent mặc định.

Mô tả `task`: “Put full detail in the prompt and state exactly what it should return”. Mô tả `execute`: “Use absolute paths and avoid `cd` so the working directory stays stable”. Harness giữ nguyên prompt đề bài và quy ước shell tương đối `workspace/...`; file tools dùng gốc ảo. Không dùng tour làm bằng chứng đã gọi model thật.

## 4. Đường cơ sở và phân loại lỗi

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

Explorer đọc đặc tả và tìm nguyên nhân; implementer thực hiện thay đổi có phạm vi và kiểm chứng; reviewer kiểm tra độc lập, không sửa. Mỗi vai trò nhận nguyên PATHS_NOTE; agent chính nhận nguyên SUBAGENTS_NOTE.

| Task | Gọi task | Loại subagent thấy trong vết chính | Token | Giây |
|---|---|---|---|---|
| code-eval | 0 | Không giao việc | 88,282 | 73.6 |
| code-learn | 0 | Không giao việc | 131,054 | 112.1 |
| data-eval | 1 | {'general-purpose': 1} | 186,898 | 127.4 |
| data-learn | 1 | {'general-purpose': 1} | 231,970 | 124.3 |
| logs-eval | 0 | Không giao việc | 44,978 | 34.6 |
| logs-learn | 0 | Không giao việc | 56,977 | 39.1 |

`subagent_calls = 0` là kết quả hợp lệ, không có nghĩa harness thiếu công cụ. Vết chỉ chứa luồng chính; không quan sát đầy đủ công việc bên trong subagent. Số token callback có cộng các lời gọi model bên trong. Khi có giao việc, dùng prompt/báo cáo được lưu để kiểm tra đủ quy tắc và agent chính có kiểm chứng hay chưa; không giả định thiết kế ba vai trò bảo đảm cả ba đều được dùng.

Hai lần giao việc đều cho `general-purpose`; chưa có lượt thật chọn explorer/implementer/reviewer. Điều kiện này quan sát việc thêm vai trò và lời nhắc giao việc, nên chưa ước lượng được lợi ích khi ba vai trò chuyên biệt đó được sử dụng.

Ví dụ quan sát: subagents/data-learn giao cho `general-purpose`, truyền quy tắc loại trùng, sentinel -999, chuẩn hóa vùng/ngày và các trường kết quả. Báo cáo trả revenue 3189.59; baseline học tính 3130.24 và qua check revenue, còn lượt subagent trượt check này. Agent chính đọc lại output/input nhưng vết không ghi phép tính kiểm chứng độc lập sửa được sai lệch. Nội dung giao việc không nhắc câu Acme review bot trong đề; các quy ước ẩn vẫn chưa được cung cấp. Đây là bằng chứng một báo cáo subagent có thể sai dù lời giao việc dài.

Ở subagents/data-eval, lời giao việc cũng ghi rõ chuyển UTC để xác định tháng. Subagent báo đã chuyển UTC; agent chính đọc output rồi chạy tính lại bằng `datetime.fromisoformat` và kiểm tra `dt.month == 3` mà không chuyển `astimezone(timezone.utc)`. Check doanh thu và số đơn tháng UTC đều trượt. Đây là nhóm D và kiểm chứng chưa đủ: tính lại cùng cách sai không xác nhận tính đúng.

## 6. Self-evolving: skill do curator sinh

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

Development gốc OpenRouter data-learn 0/8 bị cắt ở 16 bước, đã đọc một skill; lưu trong `results/openrouter/skills-auto-dev/`. **Không so nó với Gemini để đo nhiễu.** Lượt Gemini ở `results/gemini-repeat/skills-auto/` và lượt chính cùng skill/model/cap đều sau freeze gốc, chỉ là lặp học bổ sung.

## 7. Kết quả so sánh và đóng băng

| Task | baseline | subagents | skills-auto |
|---|---|---|---|
| code-learn | 7/10 | 7/10 | 7/10 |
| data-learn | 5/8 | 4/8 | 6/8 |
| logs-learn | 6/9 | 6/9 | 6/9 |
| code-eval | 7/11 | 7/11 | 7/11 |
| data-eval | 5/9 | 3/9 | 5/9 |
| logs-eval | 6/10 | 6/10 | 6/10 |
| **Mean score - learning tasks** | 0.66 | 0.62 | 0.71 |
| **Mean score - evaluation tasks** | 0.60 | 0.52 | 0.60 |
| **Mean tokens per run** | 85,670 | 123,359 | 141,212 |
| **Runs that read a skill** | 0/6 | 0/6 | 2/6 |

Bảng do module compare có sẵn sinh, chỉ đọc ba condition cấp gốc. Lượt lặp, thử bị lỗi/thay model và OpenRouter được lưu riêng, không trộn vào bảng.

| Condition | Role | Lượt/lỗi | Kỹ thuật | Quy ước | Token TB | Giây TB | Lượt đọc skill |
|---|---|---|---|---|---|---|---|
| baseline | eval | 3/0 | 18/18 | 0/12 | 86,812 | 57.8 | 0/3 |
| baseline | learn | 3/0 | 18/18 | 0/9 | 84,529 | 75.3 | 0/3 |
| skills-auto | eval | 3/0 | 18/18 | 0/12 | 75,480 | 58.3 | 1/3 |
| skills-auto | learn | 3/0 | 18/18 | 1/9 | 206,944 | 96.1 | 1/3 |
| subagents | eval | 3/0 | 16/18 | 0/12 | 106,719 | 78.5 | 0/3 |
| subagents | learn | 3/0 | 17/18 | 0/9 | 140,000 | 91.8 | 0/3 |

Thống kê đầy đủ ở [observed-breakdown.json](observed-breakdown.json). Script `check_breakdown.py` gốc vẫn ẩn đánh giá vì không có tag; giữ nguyên script và lưu đầu ra tại [check_breakdown.txt](check_breakdown.txt).

Các lượt chính đã lưu không có lỗi thực thi. Lượt bị thay thế/lỗi API giữ dưới `results/gemini-attempts/` và `results/gemini-3.8-flash/`, không bị xóa.

Freeze cục bộ lúc `2026-10-06T04:41:01.817320+00:00`; hash skill `52427bc4ab4b6cac09d9544470d030f43135a9c624d60c5711b2806f3797890b`. Hash giả thuyết và skill gốc không đổi; đối chiếu [local_freeze_check.txt](local_freeze_check.txt), [check-status.json](check-status.json). `verify_freeze.py` gốc không đạt do không có Git commit/tag, kể cả khi kiểm tra cục bộ đạt.

## 8. Phân tích

- **subagents:** chênh baseline học -0.042, đánh giá -0.074 trên thang 0–1. Đây là mô tả một lượt/mỗi task, không phải kiểm định thống kê hoặc hiệu ứng nhân quả chắc chắn.
- **skills-auto:** chênh baseline học +0.042, đánh giá +0.000 trên thang 0–1. Đây là mô tả một lượt/mỗi task, không phải kiểm định thống kê hoặc hiệu ứng nhân quả chắc chắn.
- **Giả thuyết:** điểm đánh giá cao nhất quan sát được ở baseline, skills-auto. H2 chưa được hỗ trợ về lợi ích: skills-auto hòa baseline; đồng hạng không chứng minh skill có lợi. H3 phù hợp với hai mức tăng quan sát (+0.042 học, +0.000 đánh giá). H1 cần đọc đồng thời điểm và chi phí, vì việc thêm vai trò không bảo đảm agent chọn vai trò đó.
Điểm học tăng nhưng đánh giá không tăng là dấu hiệu chuyển giao yếu. Trong vết hiện có, skill còn thiếu hướng dẫn tiền JSON và model không làm đúng quy tắc meta/UTC; chưa đủ để quy toàn bộ chênh lệch cho quá khớp nội dung skill.
- **Kỹ thuật/quy ước:** dùng phân tách mục 7, không quy mọi tăng điểm cho skill. Đọc skill chỉ chứng minh nạp nội dung, không chứng minh tuân thủ hoặc nhân quả. Các check mới trong đánh giá không được đưa vào skill sau freeze. Bảng check cụ thể dưới đây đối chiếu skills-auto với baseline; ô trống nghĩa thiếu lượt.

| Task dữ liệu | Check | Baseline | Skills-auto |
|---|---|---|---|
| data-learn | duplicate_rows_removed | đạt | đạt |
| data-learn | missing_amount_orders | đạt | đạt |
| data-learn | north_q1_orders | đạt | đạt |
| data-learn | north_q1_revenue | đạt | đạt |
| data-learn | rule_clean_csv | trượt | trượt |
| data-learn | rule_meta_block | trượt | đạt |
| data-learn | rule_money_in_cents | trượt | trượt |
| data-learn | top_region | đạt | đạt |
| data-eval | duplicate_events_removed | đạt | đạt |
| data-eval | march_orders_utc | đạt | đạt |
| data-eval | march_revenue_utc | đạt | đạt |
| data-eval | missing_total_orders | đạt | đạt |
| data-eval | rule_clean_csv | trượt | trượt |
| data-eval | rule_meta_block | trượt | trượt |
| data-eval | rule_money_in_cents | trượt | trượt |
| data-eval | rule_sorted_keys_format | trượt | trượt |
| data-eval | top_category | đạt | đạt |

Ví dụ đạt sau khi dùng skill: `rule_meta_block` ở data-learn; baseline không có meta, skills-auto tạo source/rows_in/rows_used và qua check. Vết ghi rows_in=101, rows_used=86, bám hướng dẫn đếm đơn có tiền biết được. Đây là thay đổi phù hợp với nội dung skill, với giới hạn một lượt baseline.
Ví dụ không làm đúng dù đã đọc: CSV data-learn được tạo và đọc lại nhưng vẫn trượt `rule_clean_csv`. Vết input có S-1032 tại `2024-01-07T23:15:00-05:00`, còn CSV ghi `2024-01-07T23:15:00Z`; chuyển UTC đúng phải là `2024-01-08T04:15:00Z`. Gắn Z mà giữ nguyên giờ địa phương không thực hiện chỉ dẫn chuyển UTC của skill. Check có thể còn lý do khác; vết này đủ chứng minh một lỗi cụ thể.
Ở data-eval, agent đã đọc skill nhưng `rule_meta_block` vẫn trượt: vết answer.json ghi rows_in=88 và rows_used=83, cùng kết quả 5 duplicate và 7 đơn thiếu tiền. Skill yêu cầu chỉ đếm đơn có tiền biết được, tức 88−5−7=76, nên rows_used=83 cho thấy không làm theo quy tắc này. `rule_clean_csv` cũng trượt; vết/câu trả lời cuối không chứng minh đã kiểm chứng một CSV hợp lệ. Skill không yêu cầu rõ tiền trong answer.json thành integer cents, và không bao phủ check mới `rule_sorted_keys_format`; cả hai vẫn trượt. Giữ nguyên skill thay vì chỉnh theo phản hồi đánh giá.
Vết data-learn: đọc skill ở tool call [3]; tool call đầu là `ls`. skills_read=1 chứng minh đã đọc, nhưng chưa làm đúng yêu cầu FIRST action khi có công cụ khác trước đó.
Vết data-eval: đọc skill ở tool call [4]; tool call đầu là `ls`. skills_read=1 chứng minh đã đọc, nhưng chưa làm đúng yêu cầu FIRST action khi có công cụ khác trước đó.

- **Chi phí:** điểm TB trên mỗi 10.000 token dùng các lượt chính cùng model; bảng dưới có thể chứa điểm của lượt lỗi nếu có. Chỉ so điều kiện khi cùng độ phủ. Không chuyển token thành tiền vì tier/billing/cache có thể khác.

| Condition | Lượt | Token TB | Điểm TB | Điểm / 10.000 token |
|---|---|---|---|---|
| baseline | 6 | 85,670 | 0.631 | 0.0736 |
| subagents | 6 | 123,359 | 0.573 | 0.0464 |
| skills-auto | 6 | 141,212 | 0.651 | 0.0461 |

Subagents dùng 1.44 lần token baseline, chênh điểm TB toàn bộ task -0.058. Chi phí tăng chưa được bù bằng cải thiện điểm quan sát. H1 phù hợp về hướng trong số liệu này, với giới hạn chọn subagent/nhiễu đã nêu.

- **Rò rỉ/quá khớp:** skill vẫn khớp byte với artifact curator và validator gốc. Curator không nhận dữ liệu đánh giá; không sửa skill sau quan sát. Schema region cố định là rủi ro chuyển giao sang dữ liệu category; xem vết dữ liệu đánh giá để kiểm tra tác động. Việc validator chặn từ chung `orders` không tự chứng minh đã đọc tập đánh giá.
- **Nhiễu:** các lặp Gemini dưới đây cùng skill/model/cap. Một cặp/task chỉ cho thấy biến động quan sát, không đủ ước lượng khoảng tin cậy; đều sau freeze gốc nên không thay thế development đầy đủ theo GUIDE.

| Task | Lặp học bổ sung | Lượt chính | Chênh điểm chính − lặp | Token lặp / chính |
|---|---|---|---|---|
| code-learn | 0.700 | 0.700 | +0.000 | 205,522 / 168,449 |
| data-learn | 0.750 | 0.750 | +0.000 | 69,076 / 205,500 |
| logs-learn | 0.667 | 0.667 | +0.000 | 49,858 / 246,885 |

Ba cặp học đều chênh điểm 0 với cùng skill; không có biến động điểm quan sát trong cặp này. Token vẫn biến động: data-learn từ 69.076 lên 205.500 (khoảng 2,98 lần), dù đều 6/8. Vì vậy điểm ổn định ở một cặp không chứng minh chi phí ổn định, và các chênh token nhỏ giữa condition cần được kiểm chứng bằng nhiều lượt lặp.

## 9. Hạn chế và tính hợp lệ

1. **Protocol gốc chưa đủ trước freeze:** thiếu baseline/subagents học và development code/logs trước curator/freeze; bổ sung Gemini không thể sửa lịch sử đó. Skill chỉ học từ feedback data-learn OpenRouter.
2. **Đổi model:** bảng mới giữ model/cap thống nhất, nhưng skill đến từ model khác. Không trộn hoặc so chênh token OpenRouter/Gemini như hiệu ứng skill.
3. **Quy mô/nhiễu:** ba task mỗi role, một lượt chính mỗi condition/task và tối đa một lặp skill học; temperature 0 không bảo đảm lặp y hệt. Không khái quát sang mọi model hoặc công việc thực tế.
4. **Git:** yêu cầu không commit/push được ưu tiên; không có chứng cứ commit/tag theo rubric. Freeze cục bộ chỉ kiểm tra thời gian/hash và trạng thái run.
5. **Hạ tầng/quota:** 3.8 Flash bị quota 20/ngày; lượt đầu bị chủ động dừng sau khi shell liệt kê kho mount. Vết không thấy đọc `.env`, protected files không đổi, nhưng token lượt bị dừng không đo được. Shell đã được cô lập và kiểm chứng trước mọi lượt mới.
6. **Vết giới hạn:** render_trace chỉ giữ luồng chính và cắt nội dung ở 1.500 ký tự; không khẳng định đã quan sát toàn bộ mã/script hoặc công việc bên trong subagent. Chuẩn hóa CRLF chỉ thực hiện trên Python trong bản sao sandbox.

## 10. Kết luận

Harness đạt 29 test ngoại tuyến, kiểm tra cô lập shell đạt và phiên Gemini lưu 18/18 lượt chính, 18 lượt không lỗi thực thi. Skill giữ nguyên sau freeze giúp qua meta trên data-learn (6/8 so baseline 5/8), còn điểm đánh giá TB vẫn bằng baseline (0,597). Subagents đạt điểm đánh giá thấp hơn (0,523) và dùng 1,44 lần tổng token baseline; hai lần giao việc chỉ dùng general-purpose. Kết quả mô tả phép chuyển giao skill với protocol gốc chưa đầy đủ và thiếu commit/tag theo chỉ dẫn người dùng. Bước tiếp theo nên là thí nghiệm mới tách dữ liệu, đủ học/development trước freeze và nhiều lượt lặp, giữ nguyên lịch sử phiên này.

## Phụ lục: lệnh, artifact và phần còn thiếu

Thứ tự: kiểm tra danh sách model/probe 3.8; lưu plan và tách OpenRouter; dừng lượt mount chưa cô lập; kiểm chứng shell UID riêng; 3.8 báo quota ngày; chuyển 3.1 Flash-Lite và chạy tuần tự học baseline/subagents, lặp skill học, đánh giá baseline/subagents, skill cả sáu task; summarize/compare; kiểm tra freeze và protected files. Không chạy curator thêm, không thực hiện bonus 6e (cần hai lần lặp thêm trên mọi condition/eval).

[REPRODUCE.md](REPRODUCE.md) có lệnh tái chạy; [remaining-work.json](remaining-work.json) giữ danh sách thiếu/lỗi; [gemini-summary.json](gemini-summary.json) giữ thống kê/budget; [protected-file-check.json](protected-file-check.json) kiểm tra tệp/hàm được bảo vệ; [pytest.txt](pytest.txt) giữ kết quả test. `report/REPORT.md` và `table.md` được sinh từ run.json thật; không thêm điểm cho lượt chưa chạy.

