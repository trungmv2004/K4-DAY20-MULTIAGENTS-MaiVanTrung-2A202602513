# Báo cáo: Self evolving Agentic — phần thực hiện được

Ngày: 06/10/2026, Asia/Bangkok. Mã nguồn harness đã hoàn thiện và đạt 29/29 test ngoại tuyến. Thí nghiệm chưa hoàn tất vì khóa OpenRouter hết hạn mức model miễn phí; người dùng chọn giữ khóa hiện tại và hoàn thiện phần chạy được. Báo cáo không đưa ra kết luận so sánh ba điều kiện khi chưa có dữ liệu.

## 1. Thông tin và cấu hình

| Họ tên | Mã sinh viên | Phần thực hiện |
|---|---|---|
| Mai Văn Trung (theo tên thư mục kho) | 2A202602513 | Harness, cấu hình OpenRouter, chạy thử và báo cáo với trợ lý Codex |

- Model chạy task: `nvidia/nemotron-3-super-120b-a12b:free`, qua OpenRouter; nhiệt độ 0, recursion limit 60.
- Python 3.12.15; Deep Agents 0.7.21; Docker Linux trên Windows/WSL2. Cấu hình đầy đủ: [environment.json](environment.json); phiên bản thư viện: [requirements.lock.txt](requirements.lock.txt).
- Khóa nằm trong `.env` dưới tên `OPENROUTER_API_KEY`; `AZURE_OPENAI_KEY=${OPENROUTER_API_KEY}` cho phép dùng nguyên `model.py` được đề bài cung cấp. Không in khóa ra log. Shell agent không kế thừa môi trường tiến trình cha.
- Đã chạy 4 lượt task: baseline data một lần, code hai lần, logs một lần. Tổng token của 4 bản ghi là 578.200; lượt kiểm tra kết nối miễn phí dùng thêm 45 token. Đây là lượng token xử lý, không phải số tiền thanh toán. Test và tour dùng mô hình giả.
- Thử kết nối `openai/gpt-4.1-mini` thất bại với HTTP 402 trước khi chuyển sang model miễn phí. Lần chạy lại code gặp HTTP 429 với hạn mức 50 lượt gọi miễn phí/ngày đã hết. Thời điểm reset API báo: **07:00 ngày 07/10/2026, Asia/Bangkok**.
- Không commit, không push, không tạo tag. Vì vậy yêu cầu Git `hypotheses`/`freeze` của thang điểm chưa được đáp ứng. Chưa có `freeze.json` vì chưa sinh và kiểm tra skill thật.

## 2. Giả thuyết trước đánh giá

Giả thuyết đầy đủ và tài liệu tham chiếu được lưu riêng trong [HYPOTHESES.md](HYPOTHESES.md) trước khi có bất kỳ lần chạy đánh giá nào.

- H1: Subagents dự đoán không tăng điểm đánh giá rõ so với baseline nhưng tăng token; kiểm tra độc lập không cung cấp được các quy ước ẩn.
- H2: Skills-auto dự đoán có khả năng đạt điểm đánh giá cao nhất nếu phản hồi quy ước học được tổng quát hóa đúng; không dự đoán đạt toàn bộ check.
- H3: Mức tăng trên tác vụ học dự đoán lớn hơn hoặc bằng mức tăng trên tác vụ đánh giá vì dữ liệu và quy ước mới có thể làm giảm khả năng chuyển giao.

Chưa kiểm chứng H1–H3; không có commit giả thuyết và chưa đóng băng.

## 3. Làm quen Deep Agents

Tour thực tế được lưu trong [tour.txt](tour.txt), không tốn token API.

1. Model thấy `ls`, `read_file`, `write_file`, `edit_file`, `delete`, `glob`, `grep`, `execute`, `task`. `execute` chạy shell.
2. `general-purpose` có các công cụ như agent chính và có thể nghiên cứu hoặc làm tác vụ nhiều bước. Mỗi lần gọi mặc định là phiên tạm, chỉ thấy prompt giao việc và trả lại một báo cáo cuối; cần truyền đủ đề, quy tắc và đường dẫn. Chế độ `single` vẫn có subagent mặc định này.
3. Mô tả `task`: “Put full detail in the prompt and state exactly what it should return”. Mô tả `execute`: “Use absolute paths and avoid `cd` so the working directory stays stable”. Tour có system prompt rỗng. Harness dùng nguyên `BASE_PROMPT` và `PATHS_NOTE` của đề: đường dẫn shell phải tương đối theo sandbox. Sự khác biệt giữa đường dẫn ảo của công cụ tệp và đường dẫn shell cần được agent xử lý đúng; vết logs cho thấy model chưa làm được điều này ổn định.

## 4. Đường cơ sở và phân loại lỗi

Các dòng dưới dùng lần chạy data hoàn tất và lần chạy code đầu tiên được lưu trong `results/platform-before-lf/code-learn/`. Không dùng các check thất bại sau HTTP 429 để suy luận về năng lực agent.

| Tác vụ | Check thất bại | Nhóm | Bằng chứng từ `detail` |
|---|---|---|---|
| data-learn | rule_money_in_cents | E | `money values in answer.json are integer cents` |
| data-learn | rule_meta_block | E | `answer.json has an object meta` với source, rows_in, rows_used |
| data-learn | rule_clean_csv | E | `write workspace/clean.csv` với timestamp UTC và amount_cents |
| code-learn, lần đầu | rule_type_hints | E | `every public function ... has type annotations` |
| code-learn, lần đầu | rule_regression_tests | E | `add tests/test_regressions.py ... at least 3` |
| code-learn, lần đầu | rule_changelog | E | `record each fix in CHANGELOG.md under ... ## Unreleased` |

Cả 6 lỗi quy ước quan sát được đều thuộc E. Data đạt 5/5 check kỹ thuật. Code lần đầu đạt 6/7 check kỹ thuật theo bản ghi; check còn lại là `tests_not_modified`, chịu ảnh hưởng CRLF của checkout Windows. Dấu băm sau chuẩn hóa LF là `79e05f4cc2e62a4f606d210b0b08a2cc21777245bc2f6ad244a126e9a2aee00d`, khớp bản Git và giá trị bộ chấm; dấu băm CRLF ban đầu khác. Đây là vấn đề nền tảng, không có bằng chứng agent sửa test. Runner hiện chỉ chuẩn hóa các tệp Python trong bản sao sandbox, giữ nguyên thư mục task nguồn. Lần chạy lại để xác nhận điểm đầy đủ bị chặn bởi quota, nên không tự điều chỉnh điểm đã lưu.

Vết code lần đầu cho thấy agent đọc README/docstring, sửa hàm dùng chung và chạy lại test đến `6 passed`. Data đọc README, xử lý trùng, giá trị thiếu, múi giờ và đọc lại answer.json. Đây là bằng chứng phủ định một số lỗi A–D trên hai lần chạy này, không đủ để khẳng định model không bao giờ mắc A–D. Không thấy bằng chứng nhóm F trong hai câu trả lời cuối.

Logs đạt 0/9 khi chạm giới hạn đệ quy. Vết cuối liên tục gọi `python3 /workspace/parse_log.py` hoặc `cd /workspace`, nhận `No such file or directory`; chưa tạo được errors.json. Ghi nhận riêng nhóm G: nhầm đường dẫn ảo và đường dẫn shell. Không diễn giải 9 check trượt khi task bị dừng thành 9 lỗi ngữ nghĩa độc lập, và không dùng lượt này trong curator hiện tại vì có `error`.

Skill quy ước có thể ngăn nhóm E nếu phản hồi được chuyển thành checklist đúng và model đọc/làm theo. Đây là giả thuyết, chưa có kết quả thực nghiệm skills-auto.

## 5. Điều kiện subagents

Đã cài 3 vai trò có description chỉ rõ khi giao việc:

| Subagent | Vai trò | Phạm vi |
|---|---|---|
| explorer | Đọc đặc tả, mã và dữ liệu trước khi chọn cách làm | Không sửa tệp; báo bằng chứng và điều chưa rõ |
| implementer | Thực hiện thay đổi đã khoanh vùng | Đọc đặc tả, sửa nguyên nhân chung, chạy kiểm chứng |
| reviewer | Kiểm tra độc lập sau thực hiện | Không sửa; đối chiếu quy tắc, schema, trường hợp biên |

`build_agent` nối nguyên `PATHS_NOTE` vào từng prompt subagent và thêm nguyên `SUBAGENTS_NOTE` cho agent chính. Chưa chạy điều kiện subagents với API; không có số liệu subagent_calls, chi phí hoặc chất lượng giao việc của điều kiện này. Các lượt baseline đã lưu đều có subagent_calls = 0; điều đó không thay thế thí nghiệm subagents.

## 6. Self-evolving và skill

`curate_skills` đã cài đặt và đạt 2/2 test của `test_04_curator.py`: chỉ nhận bản ghi học, đưa tên/detail/vết vào prompt, bỏ skill sai định dạng/rò rỉ/path traversal, không gọi model nếu không có lỗi học. Bản ghi có lỗi thực thi được loại khỏi evidence để tránh học từ task chưa hoàn tất.

Chưa gọi curator thật; số skill thật = 0; số lần xóa hoặc chạy lại curator = 0. `skills/auto/` vẫn chỉ có README có sẵn. Không viết tay skill để thay đầu ra model. Chưa có đánh giá chất lượng nội dung, số dòng hay skills_read của skill thật; chưa chạy Phần 3.4.

## 7. Bảng kết quả hiện có

Bảng sau do `lab.compare` sinh, khớp [table.md](table.md). Đây là bảng chưa đủ dữ liệu: chỉ có baseline học; code/logs chứa lỗi nên trung bình 0,24 không phải ước lượng hiệu quả của baseline trong điều kiện chạy thành công.

| Task | baseline |
|---|---|
| code-learn | 1/10 |
| data-learn | 5/8 |
| logs-learn | 0/9 |
| **Mean score - learning tasks** | 0.24 |
| **Mean score - evaluation tasks** | - |
| **Mean tokens per run** | 144,855 |
| **Runs that read a skill** | 0/3 |

| Lượt đã lưu | Điểm | Token | Tool calls | Giây | Tình trạng |
|---|---|---|---|---|---|
| baseline/data-learn | 5/8 | 118.082 | 18 | 64,1 | Hoàn tất; trượt 3 quy ước |
| code-learn lần đầu, platform-before-lf | 6/10 | 143.634 | 23 | 76,1 | Hoàn tất; 3 quy ước và 1 check bị CRLF |
| baseline/logs-learn | 0/9 | 312.988 | 30 | 136,3 | GraphRecursionError; giữ vết cuối |
| baseline/code-learn chạy lại | 1/10 | 3.496 | 1 | 2,9 | HTTP 429; không hoàn tất |

Mọi bản ghi đều có `skills_modified=false`, nhưng chưa có skill được nạp nên điều này không chứng minh quy trình freeze. Phần thống kê từ script gốc lưu ở [check_breakdown.txt](check_breakdown.txt); script chỉ hiển thị học khi chưa có tag freeze. Các kết quả này còn bao gồm lượt lỗi và không bao gồm lần code đầu đã lưu riêng.

Script gốc báo baseline học đạt 6/18 check kỹ thuật và 0/9 quy ước, trung bình 144.855 token. Con số 6/18 bao gồm hai lượt bị dừng nên không dùng làm bằng chứng phủ định A–D. `verify_freeze.py` trả mã 1 với `FAIL: git tag freeze not found`; kiểm tra cục bộ cũng trả mã 1 vì chưa tạo mốc đóng băng. Trạng thái và đầu ra được lưu trong [check-status.json](check-status.json), [git_freeze_check.txt](git_freeze_check.txt), [local_freeze_check.txt](local_freeze_check.txt). Không báo các kiểm tra freeze này là đã đạt.

## 8. Phân tích

1. Chưa có dữ liệu subagents/skills-auto hoặc đánh giá, nên không thể kết luận điều kiện nào cải thiện điểm, hay có quá khớp giữa học và đánh giá.
2. Data có 5/5 check kỹ thuật đạt và 0/3 quy ước. Code lần đầu có 6/7 kỹ thuật đạt và 0/3 quy ước; check CRLF cần loại khỏi giải thích năng lực. Chưa biết skill giúp check quy ước cũ hay mới vì chưa có skill và không xem bộ chấm đánh giá để viết skill.
3. Không có ví dụ check được skill giúp đạt; mọi skills_read hiện có bằng 0 vì không nạp skill. Chưa có cơ sở phân biệt “không đọc”, “đọc không làm theo” hay “skill sai”.
4. Chi phí được đo thật cho baseline: data 118.082 token, code lần đầu 143.634, logs 312.988, lượt code bị quota 3.496. Trung bình hai lượt hoàn tất là 130.858 token, nhưng code có sai lệch nền tảng. Không thể so hiệu quả điểm/token giữa các điều kiện. Chi phí tự khai báo của model miễn phí không bằng token=0.
5. Không đưa nội dung tập đánh giá vào prompt curator; chưa chạy curator hoặc tạo skill. `validate_skill` chặn định danh đánh giá theo cơ chế có sẵn. Chưa đủ dữ liệu để đánh giá mức tổng quát hoặc quá khớp; chỉ có kiểm tra offline cho cơ chế ngăn rò rỉ.
6. Chưa chạy skills-auto học trước/sau đóng băng, nên không có ước lượng nhiễu. Không dùng hai lượt code khác cấu hình chuẩn hóa và một lượt lỗi API như phép đo nhiễu của cùng điều kiện.

## 9. Hạn chế và tính hợp lệ

1. Thiếu hai điều kiện và toàn bộ tập đánh giá: không thể kiểm chứng H1–H3 hoặc báo cáo kết quả ba điều kiện.
2. Hạn mức OpenRouter và vòng lặp đường dẫn làm task bị dừng: điểm 0/9 và 1/10 không phản ánh riêng chất lượng suy luận. Cần chạy lại và giữ các lượt lỗi làm evidence phụ.
3. CRLF Windows làm một check integrity sai: sửa ở ranh giới sandbox đã qua test harness nhưng chưa có lượt model xác nhận lại điểm code. Không sửa bộ chấm hoặc số liệu cũ.
4. Chỉ một model miễn phí, dữ liệu nhỏ, chưa có lặp thí nghiệm: chưa thể ngoại suy hoặc định lượng độ biến thiên.
5. Không commit/tag theo chỉ thị người dùng: chưa đáp ứng tiêu chí freeze Git. Cơ chế dấu băm cục bộ đã chuẩn bị nhưng chưa chạy; ngay cả khi chạy cũng không tương đương bằng chứng lịch sử Git mà rubric yêu cầu.

## 10. Kết luận

Harness đã hoàn thiện và đạt 29 test ngoại tuyến. Baseline data giải đúng các check kỹ thuật nhưng bỏ sót ba quy ước Acme. Code lần đầu cho kết quả sửa lỗi kỹ thuật tốt, nhưng có sai lệch integrity do CRLF. Chưa thể khẳng định lợi ích của subagents hoặc skill do curator vì các thí nghiệm còn thiếu. Khi hạn mức khả dụng, tiếp tục theo GUIDE, đánh giá skill thật rồi đóng băng trước tập đánh giá.

## Phụ lục: tái lập và việc còn lại

Các bước đã thực hiện theo thứ tự:

1. Đọc README/GUIDE, pseudo-code, rubric và test; không sửa các tệp đề bài bảo vệ.
2. Thử cài venv Windows, nhưng pip không tải được setuptools; chuyển sang Docker Linux.
3. Cài 4 module TODO, build image, chạy pytest: 29 passed; chạy tour model giả.
4. Cấu hình OpenRouter bằng nội suy khóa; thử gpt-4.1-mini gặp 402, chuyển Nemotron miễn phí và kiểm tra kết nối thành công.
5. Chạy baseline data-learn, rồi code-learn/logs-learn. Lưu code lần đầu riêng khi xác nhận sai lệch CRLF.
6. Chuẩn hóa Python trong bản sao sandbox; chạy lại pytest: 29 passed. Chạy lại baseline code-learn gặp quota 429.
7. Người dùng chọn giữ khóa; dừng các lần gọi API mới, tạo bảng và báo cáo từ bản ghi thật.

Hướng dẫn Docker và lệnh cụ thể: [REPRODUCE.md](REPRODUCE.md). Script chạy tiếp [continue_lab.py](continue_lab.py) giữ các lượt cũ, dừng khi có lỗi và tách các checkpoint:

```powershell
.\report\run.ps1 python report/continue_lab.py learn
# Đọc và đánh giá SKILL.md thật theo GUIDE 3.3; không sửa tay nội dung skill.
.\report\run.ps1 python report/continue_lab.py development
# Cập nhật báo cáo bằng kết quả học và nhận xét skill trước khi đóng băng.
.\report\run.ps1 python report/continue_lab.py freeze
.\report\run.ps1 python report/continue_lab.py evaluation
.\report\run.ps1 python report/verify_local_freeze.py
```

Giữ cùng model để so sánh; quota mới có thể vẫn không đủ hoàn tất một phiên, script có thể tiếp tục sau khi hạn mức phục hồi. Khi đổi model cần tách kết quả và chạy lại các điều kiện tương ứng. Sau khi có dữ liệu đầy đủ, tạo lại bảng, phân tích vết và cập nhật báo cáo; không sửa skill đã đóng băng. Không thực hiện thử thách tùy chọn Phần 6 khi thí nghiệm chính còn thiếu.
