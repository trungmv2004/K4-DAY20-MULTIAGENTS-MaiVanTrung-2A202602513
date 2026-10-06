# Chấm bài theo RUBRIC.md

Ngày chấm: 06/10/2026. Phạm vi: mã nguồn, kết quả và báo cáo hiện có trong workspace. Đây là điểm tự chấm đề xuất; điểm chính thức do giảng viên quyết định.

**Tổng đề xuất: 91/100. Thưởng: 0. Không áp dụng khoản phạt bổ sung nào theo bằng chứng đã kiểm tra.**

## Cách tính

Hạng mục 1 tính đúng công thức test của rubric. Các mục đọc báo cáo được chấm theo mức độ đáp ứng. Rubric chỉ mô tả mức đạt đầy đủ, không quy định trọng số thành phần cho 4.3 và 6.1; bản chấm này công khai cách chia: 4.3 có 2 điểm cho đủ kết quả và 1 điểm cho verifier; 6.1 có 3 điểm cho nội dung giả thuyết và 1 điểm cho commit trước freeze. Đây là lựa chọn chấm điểm thành phần, không phải trọng số được quy định sẵn trong rubric.

Nếu giảng viên áp dụng đạt/không đạt cho toàn bộ tiêu chí 4.3 và 6.1, hai mục này sẽ nhận 0 thay vì 2 và 3; giữ nguyên các mục khác thì tổng là **86/100**. Không coi kiểm tra SHA-256 cục bộ là thay thế cho quy trình Git.

| Hạng mục | Điểm đề xuất | Tối đa |
|---|---:|---:|
| 1. Harness | 30 | 30 |
| 2. Baseline và phân loại lỗi | 14 | 14 |
| 3. Subagents | 10 | 10 |
| 4. Skill do curator sinh | 14 | 16 |
| 5. So sánh và đóng băng | 5 | 10 |
| 6. Báo cáo | 18 | 20 |
| **Tổng** | **91** | **100** |

## Điểm từng tiêu chí

| Tiêu chí | Điểm | Bằng chứng và nhận xét |
|---|---:|---|
| 1 — test_02_agent | 10/10 | 9/9 test đạt: 10 × 9/9. |
| 1 — test_03_runner | 12/12 | 6/6 test đạt: 12 × 6/6. |
| 1 — test_04_curator | 8/8 | 2/2 test đạt: 8 × 2/2. Test_01_provided cũng đạt 12/12, không cộng điểm. |
| 2.1 — Baseline đầy đủ | 4/4 | Có run.json và trace.md cho cả sáu tác vụ; không lỗi thực thi, điểm/check/token nhất quán. |
| 2.2 — Phân loại lỗi | 10/10 | REPORT.md mục 4 phân loại chín check học thất bại, có tên task/check/detail. Nhóm E chiếm toàn bộ; bằng chứng phủ định A–D là 18/18 check kỹ thuật đạt. Không dùng lỗi API/quota làm lỗi tác tử. |
| 3.1 — Thiết kế subagent | 3/3 | Explorer, implementer, reviewer có vai trò, điều kiện gọi và phạm vi riêng; PATHS_NOTE được bổ sung khi build agent. |
| 3.2 — Kết quả subagents | 3/3 | Đủ sáu tác vụ hợp lệ trong results/subagents/. |
| 3.3 — Phân tích giao việc | 4/4 | REPORT.md mục 5 và 8 đối chiếu số lần gọi, hai lượt general-purpose, thông tin giao việc, sai lệch tính toán, kiểm chứng và chi phí token. Không suy diễn hiệu quả của ba vai trò chưa được gọi. Không trừ điểm vì số lần gọi thấp hoặc điểm tác vụ giảm: rubric cho phép kết quả này khi được phân tích. |
| 4.1 — Curator hoạt động | 5/5 | Một skill hợp lệ; nội dung khớp byte với artifact curator-attempt-2, không sửa tay. Ba lần curator có prompt/reply/usage/log; lý do chọn lại đầu ra lần 2 được ghi rõ. |
| 4.2 — Đánh giá skill | 5/5 | Mục 6 đánh giá tính tổng quát, điểm đúng/thiếu, schema dễ quá khớp, độ dài và description; giải thích hai skill bị loại và các lần thử lại. |
| 4.3 — Kết quả chính thức | 2/3 | Đủ sáu lượt skills-auto với cùng hash, không sửa skill. Mất 1 điểm theo cách chia thành phần ở trên vì verifier gốc thất bại: thiếu tag freeze. |
| 4.4 — Giải thích dùng skill | 2/3 | Có skills_read và vị trí đọc trong hai trace dữ liệu, ví dụ meta đạt và UTC/meta chưa được làm đúng. Mất 1 điểm vì chưa giải thích tường minh vì sao cả bốn lượt code/logs không đọc skill; bảng đếm và description cho biết phạm vi nhưng chưa trả lời đầy đủ phần “vì sao không đọc”. |
| 5.1 — Bảng so sánh | 5/5 | report/table.md khớp chính xác build_table(load_runs(...)) của lab.compare có sẵn; đủ ba điều kiện, sáu task và các hàng tổng hợp. |
| 5.2 — Đóng băng | 0/5 | scripts/verify_freeze.py trả exit 1: thiếu tag freeze và không có commit hypotheses trước tag. Kiểm tra cục bộ đạt không đáp ứng điều kiện Git. Giữ yêu cầu không commit/push của người dùng. |
| 6.1 — Giả thuyết | 3/4 | Có H1–H3, dự đoán, lý do và tài liệu tham khảo; hồ sơ cục bộ trước đánh giá còn lưu. Mất 1 điểm theo cách chia thành phần vì không commit trước tag freeze. |
| 6.2 — Phân tích kết quả | 7/8 | Phân tách học/đánh giá và kỹ thuật/quy ước, giải thích bằng trace/skills_read, phân tích token, chuyển giao/quá khớp và ba cặp lặp học. Mất 1 điểm vì các cặp Gemini đều sau freeze; development OpenRouter chỉ có data-learn bị lỗi, khác model/cap. Chưa có đầy đủ đối chiếu Phần 3.4 trước freeze với lượt sau freeze trên cùng cấu hình theo yêu cầu. Báo cáo đã nêu đúng giới hạn này. |
| 6.3 — Hạn chế | 4/4 | Mục 9 có sáu hạn chế, giải thích ảnh hưởng của protocol chưa đủ, đổi model, quy mô/nhiễu, Git, quota và trace bị giới hạn. |
| 6.4 — Trình bày và tái lập | 4/4 | Đủ mục báo cáo, gồm câu hỏi tour ở mục 3; có model, temperature, recursion limit, môi trường, lệnh trong REPRODUCE.md và trạng thái không commit được công khai. Trích hướng dẫn task/execute khớp tour.txt. |

## Kiểm tra đã thực hiện trong lượt chấm

- Chạy lại `report/run.ps1 python -m pytest -q`: exit 0, toàn bộ 29 test đạt. Cấu hình đã có `-q`, nên thêm `-q` chỉ in các dấu chấm và `[100%]`; phân bổ 12 + 9 + 6 + 2 khớp bộ test của rubric.
- Đọc và kiểm tra đủ 18 run.json, trace không rỗng, trường error bằng null; số check, điểm và tổng token nhất quán.
- Đối chiếu table.md bằng hàm của lab.compare gốc: khớp.
- Chạy validate_skill gốc: không có vấn đề. So sánh byte với skill trong curator-attempt-2: khớp.
- Git diff trên host của tests/, tasks/, scripts/ và năm module có sẵn: rỗng. So sánh nội dung với HEAD trong Docker sau chuẩn hóa CRLF/LF và so sánh AST các hằng số/hàm được bảo vệ: đạt. Khác biệt xuống dòng giữa Windows/Linux không được tính là sửa nội dung.
- Quét 141 artifact văn bản trong report/, results/, skills/: không thấy giá trị khóa đang cấu hình trong .env. Không xuất giá trị khóa vào kết quả chấm. Tham chiếu thêm protected-file-check.json và final-validation.json cho việc .env được ignore và kiểm tra trước đó.
- `python scripts/verify_freeze.py`: exit 1, `FAIL: git tag freeze not found`.
- `python report/verify_local_freeze.py`: exit 0, sáu lượt skills-auto đạt kiểm tra cục bộ. Đây là bằng chứng bổ sung về hash/thời gian, không được tính là verifier Git đạt.

Không gọi API, không chạy thêm thí nghiệm model, không sửa báo cáo nghiên cứu/skill/mã nguồn để tăng điểm, không commit, không push trong lượt chấm.

## Thưởng và khoản phạt

**Thưởng 0/5:** chưa thực hiện đầy đủ một hướng Phần 6; ba lượt lặp học không đủ thiết kế 6e trên mọi điều kiện/tác vụ đánh giá. Quy trình Git cũng chưa hoàn thành.

**Phạt bổ sung 0:** chưa thấy bằng chứng lộ khóa trong artifact, sửa tay skill, chép đáp án đánh giá vào skill, sửa phần mã được bảo vệ hoặc bảng kết quả không khớp. Thiếu Git đã được xử lý trong các tiêu chí liên quan; không tự áp thêm khoản phạt -10 cho việc thiếu tag. Bản chấm không xác định việc nộp trễ hay sao chép giữa các nhóm vì không có dữ liệu lớp để đối chiếu.

## Các điểm còn thiếu

1. Git freeze: tiêu chí 4.3, 5.2 và 6.1 chưa đạt đầy đủ. Không thể tạo commit/tag hiện tại rồi coi đó là lịch sử trước các lượt đã chạy. Muốn đáp ứng toàn bộ cần một thí nghiệm mới thực hiện đúng trình tự, nếu người dùng sau này cho phép commit.
2. Mục 4.4: bổ sung phân tích lý do bốn lượt code/logs không đọc skill dựa trên description, đề bài và trace; cần phân biệt nhận xét suy đoán với điều quan sát trực tiếp.
3. Mục 6.2: cần lượt development trước freeze và lượt chính sau freeze trên cùng bộ skill/model/tham số trong một thí nghiệm mới. Ba cặp sau freeze hiện có vẫn hữu ích để mô tả biến động, nhưng không sửa được thiếu sót trình tự ban đầu.

Điểm tác vụ chưa tăng trên đánh giá không tự làm mất điểm báo cáo: rubric chấp nhận kết quả âm hoặc hòa baseline nếu phân tích có bằng chứng và đúng giới hạn.
