# Cập nhật chấm điểm sau Git freeze

Ngày 06/10/2026. Bản tự chấm 91/100 trước khi được phép commit được giữ nguyên tại [pre-git-freeze/GRADING.md](pre-git-freeze/GRADING.md).

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
