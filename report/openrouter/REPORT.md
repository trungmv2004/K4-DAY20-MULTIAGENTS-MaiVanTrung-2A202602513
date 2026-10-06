# Báo cáo Lab: Self evolving Agentic

Ngày thực hiện: **06/10/2026**, múi giờ Asia/Bangkok.

Đã hoàn thiện harness, sinh và giữ một skill thật từ curator, đóng băng cục bộ và thực hiện các lượt đánh giá dữ liệu. Khóa OpenRouter mới đã hết quota miễn phí; người dùng chọn dùng hết hạn mức và lưu phần thiếu. Các lượt đánh giá chưa hoàn tất vì giới hạn đệ quy và đường dẫn shell sai. Báo cáo này không tuyên bố đã hoàn thành toàn bộ thí nghiệm hoặc chứng minh hiệu quả của skill.

## 1. Thông tin và cấu hình

| Họ tên | Mã sinh viên | Phần thực hiện |
|---|---|---|
| Mai Văn Trung (theo tên thư mục kho) | 2A202602513 | Harness, cấu hình OpenRouter, thực nghiệm và báo cáo với trợ lý Codex |

- Model task và curator: `nvidia/nemotron-3-super-120b-a12b:free`, qua OpenRouter; temperature = 0.
- Python 3.12.15, Deep Agents 0.7.21; Docker Linux trên Windows/WSL2. Xem [environment.json](environment.json), [requirements.lock.txt](requirements.lock.txt).
- Baseline học dùng recursion limit 60. Kiểm tra skill học và hai lượt đánh giá dữ liệu dùng 16 để dành quota. Thử chạy lại skills-auto/data-eval với 40 bước bị HTTP 429 ngay đầu lượt. Việc tăng giới hạn sau khi thấy lượt bị cắt được ghi rõ trong [evaluation-retry.json](evaluation-retry.json), không coi đây là cấu hình đã đăng ký trước.
- Khóa thật nằm trong `.env` ở `OPENROUTER_API_KEY`; `AZURE_OPENAI_KEY=${OPENROUTER_API_KEY}` dùng cổng tương thích OpenAI mà không sửa `model.py`. Khóa không được đưa vào sản phẩm. Shell agent không kế thừa biến môi trường tiến trình cha.
- Đã thực hiện **9 lượt task khác nhau**, tính cả các lượt lỗi và hai phiên dùng khóa khác nhau; **930.355 token**. Curator gọi **3 lần**, **11.652 token**. Hai lần kiểm tra kết nối miễn phí dùng 45 và 31 token. Tổng token ghi nhận của các hoạt động này: **942.083**; không tính token giả của pytest/tour hoặc coi số token là số tiền thanh toán.
- Các bản sao lưu cùng lượt được nhận diện bằng condition/task/timestamp và chỉ tính một lần khi tổng hợp token.
- Khóa mới được kiểm tra có `total_credits=0`. API cuối phiên trả HTTP 429, `X-RateLimit-Limit=50`, `X-RateLimit-Remaining=0`; thời điểm reset được báo là **07:00 ngày 07/10/2026, Asia/Bangkok**.
- Không commit, không push, không tạo tag. Không có commit Git `hypotheses`/`freeze`; tiêu chí này của rubric chưa được đáp ứng. Dấu mốc cục bộ nằm trong [freeze.json](freeze.json), lúc **11:41:01 ngày 06/10/2026**.

## 2. Giả thuyết trước đánh giá

Giữ nguyên [HYPOTHESES.md](HYPOTHESES.md) đã viết trước mọi lần chạy đánh giá. Bản nháp [REPORT-before-eval.md](REPORT-before-eval.md), dấu băm giả thuyết và dấu băm skill được lưu trước khi chạy tập đánh giá. Không sửa dự đoán sau khi thấy điểm.

- H1: Subagents dự đoán không tăng điểm đánh giá rõ so với baseline nhưng tăng token; phân vai và kiểm tra độc lập không tự cung cấp các quy ước ẩn. [Anthropic](https://www.anthropic.com/engineering/multi-agent-research-system) mô tả lợi ích và chi phí của việc chia việc; không thể suy trực tiếp kết quả nghiên cứu đó cho tác vụ nhỏ của lab.
- H2: Skills-auto dự đoán có khả năng đạt điểm đánh giá cao nhất nếu phản hồi quy ước học được tổng quát hóa đúng; không dự đoán đạt toàn bộ check. [SkillsBench](https://arxiv.org/abs/2602.12670) cung cấp căn cứ về lợi ích có thể có của skill biên soạn, không bảo đảm lợi ích của skill curator tự sinh.
- H3: Mức tăng điểm do skill trên học dự đoán lớn hơn hoặc bằng mức tăng trên đánh giá vì dữ liệu và quy ước mới có thể giảm chuyển giao. [SkillEvolBench](https://arxiv.org/abs/2605.24117) cho thấy thích nghi cục bộ có thể không thành kỹ năng dùng lại ổn định.

Chưa đủ dữ liệu chạy thành công để kiểm chứng hoặc bác bỏ H1–H3.

## 3. Làm quen Deep Agents

Tour model giả được lưu trong [tour.txt](tour.txt).

1. Công cụ model nhìn thấy: `ls`, `read_file`, `write_file`, `edit_file`, `delete`, `glob`, `grep`, `execute`, `task`. `execute` chạy shell.
2. `general-purpose` có các công cụ như agent chính và có thể nghiên cứu hoặc làm tác vụ nhiều bước. Mỗi lần gọi mặc định tạo một phiên tạm, chỉ nhận prompt giao việc và trả về một báo cáo cuối; cần truyền đủ đề, quy tắc và đường dẫn. Chế độ `single` vẫn có subagent mặc định này.
3. Mô tả `task`: “Put full detail in the prompt and state exactly what it should return”. Mô tả `execute`: “Use absolute paths and avoid `cd` so the working directory stays stable”. Tour có system prompt rỗng. Harness giữ nguyên `BASE_PROMPT` và `PATHS_NOTE` của đề, yêu cầu đường dẫn shell tương đối theo sandbox. Vết thực nghiệm cho thấy model chưa xử lý ổn định sự khác biệt giữa đường dẫn ảo của file tools và đường dẫn shell.

## 4. Đường cơ sở và phân loại lỗi

Bảng dùng baseline data-learn hoàn tất và code-learn lần đầu hoàn tất được giữ trong `results/platform-before-lf/code-learn/`. Không dùng check trượt sau HTTP 429 làm bằng chứng về năng lực agent.

| Tác vụ | Check thất bại | Nhóm | Bằng chứng từ `detail` |
|---|---|---|---|
| data-learn | rule_money_in_cents | E | `money values in answer.json are integer cents` |
| data-learn | rule_meta_block | E | `answer.json has an object meta` với source, rows_in, rows_used |
| data-learn | rule_clean_csv | E | `write workspace/clean.csv` với timestamp UTC và amount_cents |
| code-learn, lần đầu | rule_type_hints | E | `every public function ... has type annotations` |
| code-learn, lần đầu | rule_regression_tests | E | `add tests/test_regressions.py ... at least 3` |
| code-learn, lần đầu | rule_changelog | E | `record each fix in CHANGELOG.md under ... ## Unreleased` |

Cả 6 lỗi quy ước quan sát ở hai lượt hoàn tất đều thuộc E. Data đạt 5/5 check kỹ thuật. Code lần đầu đạt 6/7 kỹ thuật; check `tests_not_modified` bị ảnh hưởng CRLF của checkout Windows. Dấu băm LF `79e05f4cc2e62a4f606d210b0b08a2cc21777245bc2f6ad244a126e9a2aee00d` khớp bản Git và bộ chấm; dấu băm CRLF khác. Runner đã chuẩn hóa Python **chỉ trong bản sao sandbox**, giữ nguyên task nguồn. Code lần chạy mới đạt 7/7 kỹ thuật, xác nhận check integrity đã qua; lượt này vẫn có GraphRecursionError, nên không gọi là task hoàn tất.

Code lần đầu đọc README/docstring, sửa hàm dùng chung và chạy test đến `6 passed`. Data đọc README, xử lý trùng, giá trị thiếu, múi giờ và đọc lại answer.json. Đây là bằng chứng phủ định một số lỗi A–D trong những lượt này, không đủ để khẳng định model luôn tránh A–D. Không có bằng chứng nhóm F trong hai câu trả lời cuối được lưu.

Logs đạt 0/9 khi chạm giới hạn 60. Code mới cũng dừng ở giới hạn 60. Vết lặp các lệnh như `python3 /workspace/parse_log.py`, `pytest /workspace/tests/test_report.py` hoặc `cd /workspace`, nhận lỗi không tìm thấy đường dẫn. Ghi nhận riêng nhóm G: nhầm đường dẫn ảo và đường dẫn shell. Không diễn giải mọi check trượt khi task bị cắt thành các lỗi ngữ nghĩa độc lập.

Curator chỉ nhận bản ghi **data-learn hoàn tất**; các bản ghi học có `error` được loại khỏi prompt. Do đó skill không được học phản hồi quy ước của code/logs trong lượt sinh này. Skill quy ước có thể ngăn nhóm E nếu nội dung đúng và model áp dụng được, nhưng chưa có kết quả output hoàn tất chứng minh điều đó.

## 5. Điều kiện subagents

| Subagent | Vai trò | Phạm vi |
|---|---|---|
| explorer | Đọc đặc tả, mã và dữ liệu trước khi chọn cách làm | Không sửa; báo bằng chứng và điều chưa rõ |
| implementer | Thực hiện thay đổi đã khoanh vùng | Đọc đặc tả, sửa nguyên nhân chung, chạy kiểm chứng |
| reviewer | Kiểm tra độc lập sau thực hiện | Không sửa; đối chiếu quy tắc, schema và trường hợp biên |

`build_agent` nối nguyên `PATHS_NOTE` vào từng subagent và thêm nguyên `SUBAGENTS_NOTE` cho agent chính. Các test subagent đã đạt. Chưa có lượt condition `subagents` thật vì quota được ưu tiên cho sinh skill và đánh giá theo lựa chọn người dùng; còn thiếu cả 6 lượt của điều kiện này. Vì vậy chưa có số liệu chất lượng giao việc, kiểm tra báo cáo subagent hoặc chênh lệch token/thời gian.

Các bản ghi baseline và skills-auto đã lưu có subagent_calls = 0. Điều này chỉ mô tả các lượt đó, không thay thế thí nghiệm subagents.

## 6. Self-evolving: skill curator sinh

Curator thật gọi 3 lần, gồm lần đầu và tối đa 2 lần chạy lại theo GUIDE. Prompt/phản hồi/token của từng lần được lưu trong `report/curator-attempt-1/`, `curator-attempt-2/`, `curator-attempt-3/`.

| Lần | Kết quả | Xử lý và lý do |
|---|---|---|
| 1 | 3 khối dùng tên có underscore, bị validator từ chối | Làm rõ regex tên và cấm underscore trong prompt curator; không sửa output |
| 2 | 3 skill hợp lệ định dạng | Bỏ `ensure-correct-file-paths`: gợi ý `/workspace` là gốc thật, dễ gây nhầm shell. Bỏ `convert-money-values-to-integer-cents`: khuyên float/round để chống sai số, không phải hướng dẫn tài chính tổng quát an toàn |
| 3 | 1 khối bị validator từ chối vì chứa từ `orders` | Validator có sẵn xem `orders` là định danh đánh giá dù từ này cũng là thuật ngữ chung trong feedback. Giữ validator nguyên trạng; không sửa skill để vượt kiểm tra |

Sau lần 3, chọn lại **nguyên văn** `produce-answer-and-clean-csv` đã sinh ở lần 2. Đây là lựa chọn lại artifact do model tạo, không phải biên soạn tay. Hai skill kém chất lượng không nằm trong `skills/auto/`; bản gốc được lưu để kiểm tra. Nội dung skill giữ lại khớp byte với bản lưu lần 2, và không đổi sau freeze. Xem [skill-review.json](skill-review.json).

| Skill | Tổng quát | Đúng/sai và giới hạn | Độ dài, description, việc đọc |
|---|---|---|---|
| produce-answer-and-clean-csv | Quy trình xuất meta và clean.csv, không chứa tên input học hay định danh đánh giá. Schema region và ví dụ Q1 làm phạm vi nghiêng về dạng dữ liệu học | Meta, loại trùng, UTC và CSV bám feedback học. Thiếu yêu cầu rõ cho tiền trong answer.json; tham chiếu “money-conversion rule” chưa định nghĩa làm tròn. Vì vậy chưa bao phủ đủ cả ba quy ước và còn rủi ro khi dữ liệu đổi miền | 23 dòng toàn tệp, 19 dòng body. Description bắt đầu `Use when` nhưng phụ thuộc answer.json/meta/clean.csv. skills_read = 1 ở lượt học và lượt đánh giá 16 bước |

Skill yêu cầu các tên output Acme như answer.json, clean.csv, meta; đây là quy ước được phép giữ theo hướng dẫn chất lượng. Không có đáp án đánh giá được đưa vào skill. Trên data-eval, input có `category` còn skill quy định schema `region`; có rủi ro quá khớp schema, nhưng chưa có output để kết luận tác động thực tế.

Lượt kiểm tra học trước freeze: data-learn **0/8**, 35.538 token, 7 tool calls, 64,2 giây, skills_read = 1, skills_modified = false, GraphRecursionError ở 16 bước. Vết cho thấy model đọc skill sau README/mẫu input, không làm đúng yêu cầu `FIRST action`; chỉ kiểm tra số dòng rồi bị cắt, chưa tạo answer.json hoặc clean.csv. Lưu riêng trong `results/skills-auto-dev/data-learn/`.

## 7. Kết quả so sánh và đóng băng

Bảng sau do `lab.compare` sinh, khớp [table.md](table.md). Chỉ các lượt đã quan sát được xuất hiện; cột subagents và các task chưa chạy không được thêm số liệu giả. Các trung bình còn chứa lượt có lỗi, không phải ước lượng hiệu quả khi task chạy hoàn tất.

| Task | baseline | skills-auto |
|---|---|---|
| code-learn | 7/10 | - |
| data-learn | 5/8 | - |
| logs-learn | 0/9 | - |
| data-eval | 0/9 | 0/9 |
| **Mean score - learning tasks** | 0.44 | - |
| **Mean score - evaluation tasks** | 0.00 | 0.00 |
| **Mean tokens per run** | 172,711 | 56,843 |
| **Runs that read a skill** | 0/4 | 1/1 |

| Lượt trong bảng | Token | Tool calls | Giây | skills_read | Tình trạng |
|---|---|---|---|---|---|
| baseline/code-learn mới | 196.041 | 30 | 104,5 | 0 | GraphRecursionError, limit 60 |
| baseline/data-learn | 118.082 | 18 | 64,1 | 0 | Hoàn tất; 5/8 check |
| baseline/logs-learn | 312.988 | 30 | 136,3 | 0 | GraphRecursionError, limit 60 |
| baseline/data-eval | 63.733 | 8 | 35,2 | 0 | GraphRecursionError, limit 16 |
| skills-auto/data-eval | 56.843 | 7 | 44,0 | 1 | GraphRecursionError, limit 16 |

Hai lượt đánh giá 16 bước có chạy model thật, nhưng chưa tạo answer.json/clean.csv. Vết skills-auto ghi `cd /workspace && python3 ...` rồi `can't cd to /workspace`. Lượt thử lại skills-auto ở 40 bước bị 429, token = 0, không thực hiện được công việc; lưu riêng dưới `results/attempts/skills-auto/data-eval/quota429-limit40-.../`. Bảng chọn các lượt 16 bước có hoạt động model, không chọn lượt quota-only để tạo trung bình token thấp giả. Các bản ghi được sao chép nguyên văn, không sửa điểm.

Thống kê từ script gốc `check_breakdown.py`, lưu ở [check_breakdown.txt](check_breakdown.txt):

```text
condition     role    technical  house rules  mean tokens  read a skill
baseline      learn    12/18         0/9          209,037      0/3
(evaluation rows are hidden until the git tag `freeze` exists)
```

Thống kê bổ sung sau mốc đóng băng cục bộ từ [observed-breakdown.json](observed-breakdown.json):

| Điều kiện/vai trò | Lượt / lượt lỗi | Kỹ thuật | Quy ước | Token trung bình | Lượt đọc skill |
|---|---|---|---|---|---|
| baseline/learn | 3 / 2 | 12/18 | 0/9 | 209.037 | 0/3 |
| baseline/eval | 1 / 1 | 0/5 | 0/4 | 63.733 | 0/1 |
| skills-auto/eval | 1 / 1 | 0/5 | 0/4 | 56.843 | 1/1 |

Skill đã đóng băng có SHA-256 thư mục `52427bc4ab4b6cac09d9544470d030f43135a9c624d60c5711b2806f3797890b`. Kiểm tra phạm vi đã chạy xác nhận skill và giả thuyết không đổi, lượt skill đánh giá bắt đầu sau freeze và skills_modified = false; xem [partial-freeze-integrity.json](partial-freeze-integrity.json). Điều này chỉ xác nhận tính nguyên vẹn, không chứng minh task thành công hoặc đủ thí nghiệm.

`verify_freeze.py` gốc trả mã 1 vì không có tag freeze. `verify_local_freeze.py` đầy đủ cũng trả mã 1 vì còn thiếu 5/6 lượt skill chính thức và lượt hiện có có error. Đầu ra nằm trong [git_freeze_check.txt](git_freeze_check.txt), [local_freeze_check.txt](local_freeze_check.txt), [check-status.json](check-status.json). Không báo các kiểm tra đầy đủ này là đã đạt.

## 8. Phân tích

1. **Điểm học/đánh giá:** chưa có đủ ba điều kiện hoặc lượt skills-auto học chính thức sau freeze để so mức cải thiện. Data-learn development 0/8 và data-eval 0/9 đều bị cắt, không chứng minh skill làm giảm điểm, không kiểm chứng được H2/H3. Chưa có dữ liệu subagents để kiểm chứng H1.
2. **Kỹ thuật/quy ước:** baseline data đạt 5/5 kỹ thuật, 0/3 quy ước. Code mới đạt 7/7 kỹ thuật nhưng bị dừng; baseline logs và hai lượt data-eval chưa hoàn tất. Check mới `rule_sorted_keys_format` chỉ được thấy sau freeze; skill không đề cập quy tắc này. Tuy nhiên không thể xác định skill giúp hoặc hại check mới vì chưa có output.
3. **Đọc và áp dụng skill:** skills_read = 1 ở development và evaluation chứng minh việc đọc. Vết đánh giá cho thấy model còn dùng đường dẫn shell sai; vết học chưa có output. Không có check đã đạt nhờ skill để đưa làm ví dụ thành công. Meta/CSV có trong skill nhưng chưa được thực hiện, và yêu cầu tiền JSON còn thiếu. Không đồng nhất “đã đọc” với “đã làm theo”.
4. **Chi phí:** ở cặp data-eval cùng limit 16, skills-auto dùng 56.843 token, baseline 63.733: chênh 6.890 token, khoảng 10,8%. Cả hai chưa hoàn tất nên không suy ra tiết kiệm khi giải đúng task. Hai cột token trung bình trong bảng trộn số lượng/loại task khác nhau; không so trực tiếp để tuyên bố điều kiện hiệu quả hơn. Chưa thể đánh giá điểm trên mỗi token của subagents.
5. **Rò rỉ/quá khớp:** curator chỉ dùng feedback/vết data-learn; prompt và artifact được lưu trước đánh giá, validator được giữ nguyên, skill/hypotheses không đổi sau freeze. Chưa thấy bằng chứng sao chép đáp án đánh giá. Schema region cố định và description phụ thuộc định dạng output là rủi ro quá khớp; chưa có số liệu hoàn tất xác nhận mức độ. Việc validator chặn từ chung `orders` là hạn chế của bộ lọc định danh, không phải bằng chứng tự động rằng model đã đọc tập đánh giá.
6. **Nhiễu:** development có một lượt data-learn trước freeze, chưa có lượt cùng task/skill/cap sau freeze chạy xong. Không thể ước lượng nhiễu. Không so 0/8 trên học với 0/9 trên đánh giá như hai lần lặp của cùng task; không coi lượt HTTP 429 là lặp ngẫu nhiên của model.

## 9. Hạn chế và tính hợp lệ

1. **Quota:** còn thiếu 13/18 lượt chính thức; 4/5 lượt đang được chọn có error. Chỉ baseline data-learn không lỗi thực thi, nhưng vẫn trượt quy ước. Chưa có task nào trong bảng đạt toàn bộ check.
2. **Giới hạn bước/đường dẫn:** nhiều lượt dừng vì model nhầm đường dẫn; limit 16 cắt các lượt dữ liệu trước khi tạo output. Điểm 0 không tách được năng lực xử lý dữ liệu khỏi vấn đề harness/model và ngân sách bước.
3. **Nguồn skill nhỏ:** curator chỉ nhận một task học, không nhận feedback code/logs. Không thể đánh giá tiến hóa xuyên ba họ task như thiết kế đầy đủ.
4. **Protocol một phần:** thiếu baseline/subagents học đầy đủ trước curator và thiếu development toàn bộ trước freeze. Mốc cục bộ được lập trước đánh giá nhưng không thay thế commit/tag theo rubric. Thử đổi limit sau lượt đánh giá bị cắt là thay đổi sau quan sát, đã ghi riêng.
5. **Ít lượt lặp/model duy nhất:** chưa có đo nhiễu hay kiểm chứng trên model khác; không ngoại suy cho mọi mô hình hoặc tác vụ thực tế. Nếu đổi model trong tương lai phải tách cấu hình và báo cáo lại các so sánh tương ứng.
6. **CRLF/vết giới hạn:** CRLF đã được xử lý ở bản sao sandbox; bản đầu vẫn giữ để kiểm toán. `render_trace` giới hạn 1.500 ký tự mỗi nội dung, chỉ chứa luồng chính; không dùng vết để khẳng định đã xem toàn bộ script hay công việc bên trong subagent.

## 10. Kết luận

Harness đạt 29 test ngoại tuyến và curator đã sinh một skill hợp lệ được giữ nguyên văn. Model đọc skill trong các lượt dữ liệu, nhưng các lượt học/đánh giá bị dừng trước khi tạo output. Chưa đủ bằng chứng kết luận skill cải thiện hiệu quả hoặc so sánh subagents với baseline. Dấu băm và thời gian đóng băng cục bộ được xác minh, còn yêu cầu Git và độ phủ thí nghiệm chưa đạt. Bước tiếp theo là chạy lại các lượt bị cắt với ngân sách phù hợp và hoàn thiện các lượt còn thiếu, giữ nguyên skill/giả thuyết đã đóng băng.

## Phụ lục: trạng thái và chạy tiếp

Mã TODO đã hoàn thiện trong agent.py, subagents.py, runner.py, curator.py. Toàn bộ tests/tasks/scripts và các module được đề bài bảo vệ giữ nguyên; `BASE_PROMPT`, các hằng số prompt, `render_trace`, `main`, `validate_skill`, `parse_skill_blocks` không đổi. Kết quả pytest mới nhất: **29 passed in 8.68s**, lưu tại [pytest.txt](pytest.txt).

| Phần GUIDE | Trạng thái |
|---|---|
| 0–1: môi trường, tour, harness/test | Đã thực hiện |
| 2: baseline/subagents học | Chưa đủ; baseline code/logs cần chạy lại, subagents chưa chạy |
| 3.1–3.3: curator và đánh giá chất lượng | Đã thực hiện 3 lượt gọi; giữ 1 skill, loại 2 skill kém chất lượng |
| 3.4: skills-auto học | Có data-learn bị cắt; code/logs chưa chạy |
| 4.0–4.1: giả thuyết/freeze | Có mốc cục bộ trước đánh giá; không có commit/tag |
| 4.2: đánh giá/chạy chính thức | Có baseline/skills-auto data-eval bị cắt; còn thiếu các lượt khác |
| 4.3–5: bảng/báo cáo | Đã tổng hợp mọi dữ liệu có thật và ghi hạn chế/phần thiếu |
| 6: tùy chọn | Không thực hiện khi thí nghiệm chính còn thiếu |

Danh sách cụ thể: [remaining-work.json](remaining-work.json) gồm **13 lượt chưa chạy, 4 lượt chính thức cần chạy lại**, development data cần chạy lại và development code/logs chưa chạy. Không thêm bản ghi giả cho các lượt chưa gọi model.

Thứ tự phiên tiếp tục: kiểm tra khóa mới và pytest; thử baseline code mới; gọi curator 3 lần và kiểm tra chất lượng; giữ lại artifact hợp lệ từ lần 2; kiểm tra skill trên data-learn với limit 16; lưu giả thuyết/báo cáo và đóng băng; chạy skills-auto/data-eval 16; baseline/data-eval 16; thử skills-auto/data-eval 40 gặp 429; dừng gọi API và tổng hợp. Các artifact cũ được giữ nguyên dưới `results/attempts/`, `results/platform-before-lf/`; development được giữ ở `results/skills-auto-dev/`.

Sau khi quota phục hồi, **không chạy lại curator hoặc sửa skill của thí nghiệm này**. Hướng dẫn chi tiết ở [REPRODUCE.md](REPRODUCE.md). Ví dụ chạy tiếp với script giữ bản ghi cũ, dừng khi gặp lỗi:

```powershell
.\report\run.ps1 python report/continue_lab.py frozen-learning --recursion-limit 60
.\report\run.ps1 python report/continue_lab.py evaluation --recursion-limit 60
.\report\run.ps1 python report/verify_local_freeze.py
```

`frozen-learning` chỉ hoàn thiện lượt baseline/subagents học để so sánh, không dùng feedback mới để thay skill đã đóng băng; thứ tự học này vẫn là sai khác so với GUIDE và phải tiếp tục ghi rõ. Những lượt 16 bước đã có không đủ làm ước lượng nhiễu khi chạy lại ở 60 bước. Để thiết kế một thí nghiệm đầy đủ mới, cần tách riêng toàn bộ kết quả/skill/giả thuyết và đăng ký trước khi xem tập đánh giá mới; không xóa lịch sử hiện có hoặc coi skill đã đọc đánh giá như skill mới chưa tiếp xúc.
