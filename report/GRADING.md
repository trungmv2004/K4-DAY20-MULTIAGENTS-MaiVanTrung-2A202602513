# Cập nhật chấm điểm sau Git freeze

Ngày 06/10/2026. Bản tự chấm 91/100 trước khi được phép commit được giữ nguyên tại [pre-git-freeze/GRADING.md](pre-git-freeze/GRADING.md).

Lần chấm này đối chiếu cả [báo cáo cá nhân đã điền](../REPORT_TEMPLATE.md), [báo cáo chi tiết](REPORT.md), mã nguồn và các bản ghi thực nghiệm. Làm cá nhân không bị trừ điểm: RUBRIC không quy định khoản trừ cho hình thức này. Đây là điểm tự chấm đề xuất, không thay thế quyết định của giảng viên.

**Điểm tự chấm bảo thủ: 99/100.** Nếu chỉ xét điều kiện commit trước tag mới của mục 6.1, mục này đủ 4/4 và tổng là 100/100. Bản chấm bảo thủ giữ 3/4 vì GUIDE 4.0 yêu cầu commit trước khi thấy bất kỳ điểm đánh giá nào; commit mới không khôi phục lịch sử đã thấy đánh giá cũ. Giảng viên quyết định cách xử lý giới hạn này; không tự tuyên bố đây là một đăng ký mù mới.

| Hạng mục | Điểm bảo thủ | Tối đa |
|---|---:|---:|
| Harness | 30 | 30 |
| Baseline và phân loại lỗi | 14 | 14 |
| Subagents | 10 | 10 |
| Skill curator | 16 | 16 |
| So sánh và đóng băng | 10 | 10 |
| Báo cáo | 19 | 20 |
| **Tổng** | **99** | **100** |

Thưởng 0; chưa có bằng chứng cần áp khoản phạt bổ sung. Điểm này đánh giá harness, hồ sơ và phân tích theo rubric, không phải tỷ lệ task đạt toàn bộ check.

## Đối chiếu toàn bộ tiêu chí

| Tiêu chí RUBRIC | Điểm đề xuất | Căn cứ |
|---|---:|---|
| 1. Agent | 10/10 | 9/9 test agent đạt. |
| 1. Runner | 12/12 | 6/6 test runner đạt. |
| 1. Curator | 8/8 | 2/2 test curator đạt; 12/12 test mã có sẵn cũng đạt. |
| 2.1 Baseline | 4/4 | Đủ sáu cặp run.json/trace.md; một bản ghi lỗi thực thi được công khai, xem giới hạn bên dưới. |
| 2.2 Phân loại lỗi | 10/10 | Chín check học thất bại có tên task/check và detail; tất cả nhóm E, kèm bằng chứng phủ định A–D bằng 18/18 check kỹ thuật. |
| 3.1 Thiết kế subagent | 3/3 | Ba vai trò explorer/implementer/reviewer có description và phạm vi riêng. |
| 3.2 Kết quả subagents | 3/3 | Sáu bản ghi và trace, không lỗi thực thi. |
| 3.3 Phân tích subagents | 4/4 | Số lời gọi, hai lần general-purpose, quy tắc truyền đi, lỗi UTC và token được đối chiếu với trace. |
| 4.1 Curator hoạt động | 5/5 | Skill hợp lệ khớp byte với đầu ra curator lần 2; có hồ sơ ba lần gọi thật. |
| 4.2 Chất lượng skill | 5/5 | Nhận xét tổng quát hóa, đúng/sai, độ dài/description; giải thích các lần chạy lại và loại skill. |
| 4.3 Kết quả skills-auto | 3/3 | Sáu lượt không lỗi thực thi; verifier gốc báo OK. |
| 4.4 Dùng skill | 3/3 | Giải thích riêng bốn lượt không đọc; hai lượt đọc nhưng áp dụng một phần có ví dụ meta/UTC/CSV. |
| 5.1 Bảng so sánh | 5/5 | Bảng sinh lại bằng lab.compare khớp report/table.md và bảng trong báo cáo cá nhân. |
| 5.2 Đóng băng | 5/5 | Hypotheses trước tag; sáu lượt skills-auto sau tag, đúng hash, skill không đổi. |
| 6.1 Giả thuyết | 3/4 bảo thủ | Có H1–H3, lý do và nguồn, commit trước tag mới; đã biết đánh giá cũ. Theo riêng điều kiện trước tag của RUBRIC: 4/4. |
| 6.2 Phân tích kết quả | 8/8 | Học/đánh giá, kỹ thuật/quy ước, trace, token, quá khớp và ba cặp development/chính thức cùng cấu hình đều được phân tích. |
| 6.3 Hạn chế | 4/4 | Bảy hạn chế có giải thích ảnh hưởng tới kết luận. |
| 6.4 Trình bày/tái lập | 4/4 | Đủ mười mục, ba câu hỏi làm quen, model/tham số/lệnh/commit và tài liệu tái lập. |
| Thưởng | 0/5 | Chưa hoàn thành một thí nghiệm mở rộng đầy đủ; không tính development bắt buộc thành bonus. |

Khoản giảm bảo thủ ở 6.1 là đánh giá giới hạn theo GUIDE 4.0, không phải mức phạt cố định được RUBRIC quy định. Vì vậy tổng theo các điều kiện ghi trực tiếp trong RUBRIC là 100/100; tổng bảo thủ khi xét lịch sử đánh giá là 99/100.

## Kiểm tra lại khi chấm báo cáo cá nhân

- Chạy lại toàn bộ pytest ngoại tuyến trong Docker: 29/29 đạt, exit 0.
- Chạy lại scripts/verify_freeze.py nguyên bản trong Docker Linux: `checked 6 runs of skill conditions: OK`, exit 0.
- Đối chiếu trực tiếp 18 bản ghi: số check đạt/tổng và score nhất quán, đủ trace; chỉ baseline/data-eval có lỗi thực thi.
- Bảng sinh lại khớp nguyên bảng trong báo cáo cá nhân; đủ mười mục và mọi liên kết tệp cục bộ đều tồn tại.
- Skill vẫn khớp byte với đầu ra curator và hash đã đóng băng. Ba development nằm trước tag, ba lượt học chính thức sau tag, cùng hash/model/cap; chênh điểm đều 0.

Verifier được chấm trong môi trường Linux đã dùng để chạy thí nghiệm. Hàm hash có sẵn dùng chuỗi đường dẫn tương đối: chạy trực tiếp trên Windows tạo dấu phân cách khác Linux và có thể báo lệch hash dù byte skill không đổi; Python Windows còn cần UTF-8 để đọc nội dung Git tiếng Việt. Không sửa hàm hash hoặc verifier để che khác biệt môi trường.

## Những tiêu chí đã bổ sung

| Tiêu chí | Điểm hiện tại | Bằng chứng |
|---|---:|---|
| 4.3 Kết quả chính thức | 3/3 | Đủ sáu skills-auto, không lỗi thực thi; scripts/verify_freeze.py gốc exit 0, checked 6 runs: OK. |
| 4.4 Giải thích sử dụng skill | 3/3 | REPORT.md mục 6 giải thích riêng bốn lượt code/logs không đọc skill, phân biệt suy luận về description với hành vi thấy trong trace; mục 8 có meta đạt, UTC/meta chưa đúng dù đã đọc. Sáu lượt mới cũng có cùng mẫu đọc 0/0/1/1/0/0 theo từng họ. |
| 5.2 Quy trình Git freeze | 5/5 | Commit hypotheses 7dc9055 trước commit/tag freeze 3d23bd9; skill nguyên trạng, sáu lượt skills-auto chính thức sau tag. |
| 6.1 Giả thuyết | 3/4 bảo thủ; 4/4 theo điều kiện trước tag mới | H1–H3, lý do và nguồn gốc được giữ, đã commit trước tag mới. Đã biết đánh giá phiên cũ nên vẫn có giới hạn GUIDE 4.0. |
| 6.2 Phân tích kết quả | 8/8 | Có ba development thật trước tag và ba lượt học chính thức sau tag, cùng skill/model/cap, Δ điểm đều 0. Phân tách kỹ thuật/quy ước và học/đánh giá; giải thích trace, tiền/UTC/meta, chi phí/token, lỗi thực thi, độ nhạy chi phí và quá khớp. |

Các điểm giữ nguyên: test_02 10/10, test_03 12/12, test_04 8/8; test_01 12/12 không cộng điểm. Baseline 4/4 và phân loại lỗi học 10/10; subagents 3+3+4=10; curator 5/5 và đánh giá skill 5/5; bảng so sánh 5/5; hạn chế 4/4, trình bày/tái lập 4/4.

## Lỗi thực thi còn lại

Có 18 run.json/trace hợp lệ về cấu trúc, 17 lượt không lỗi thực thi. Baseline/data-eval đã thử ba lần ở cap 60, đều GraphRecursionError. Output dở dang đạt 5/9; không coi đây là một lượt hoàn tất. Hai lỗi trước ở results/git-study-attempts/, lỗi cuối được giữ nguyên trong kết quả chính. Bản tham chiếu trước Git không lỗi cũng đạt 5/9 được lưu riêng, không dùng để thay thế record mới.

Không trừ thêm vào 2.1 chỉ vì trường error khác null: bản ghi lỗi vẫn có đủ trường/check/trace và runner phải ghi lỗi theo rubric. Phần phân loại lỗi chỉ dùng task học không lỗi. Tuy nhiên lỗi làm hạn chế phép so sánh ba điều kiện hoàn tất; báo cáo nêu rõ giới hạn, chi phí retry và không coi lỗi này là bằng chứng về quy ước E. Nếu giảng viên yêu cầu baseline phải không lỗi mới được tính hợp lệ, mục 2.1 có thể mất thêm 1 điểm.

Verifier freeze gốc vẫn đạt: nó kiểm tra skill, commit/tag và thời gian; không kiểm tra agent baseline có kết thúc hay không. git-study-validation.json giữ ok=false vì còn lỗi thực thi, đồng thời ghi git_freeze=true và các kiểm tra tính toàn vẹn đạt. Không đổi error/timestamp, model/cap, skill hoặc bộ chấm để làm xanh trạng thái.

## Hồ sơ kiểm chứng

- [git-freeze.json](git-freeze.json): SHA/thời gian thật của commit hypotheses và tag.
- [git-freeze-check.txt](git-freeze-check.txt): đầu ra verifier gốc kiểm tra đủ sáu lượt.
- [git-study-summary.json](git-study-summary.json): ba cặp development/chính thức, Δ=0, cùng hash/model/cap; 17 lượt thử mới, ba lỗi, 1.803.570 token.
- [git-study-validation.json](git-study-validation.json): kiểm tra nguồn được bảo vệ, credential, bảng, timing và lỗi còn lại.
- [REPORT.md](REPORT.md): phân tích có dữ liệu thật, công khai lịch sử và giới hạn.

Không push. Không sửa nội dung skill, tests/tasks/scripts hoặc các hàm/hằng số có sẵn.
