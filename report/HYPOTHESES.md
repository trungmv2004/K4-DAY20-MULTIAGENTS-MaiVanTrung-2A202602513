# Giả thuyết trước đánh giá

Ngày lập: 06/10/2026, múi giờ Asia/Bangkok. Chưa chạy thí nghiệm đánh giá, chưa sinh skill thực tế và chưa đóng băng skill. Đây là đăng ký giả thuyết cục bộ; không có commit `hypotheses` theo yêu cầu không commit của người dùng.

- H1: Subagents có thể hỗ trợ đọc đặc tả và kiểm tra độc lập nhưng không tự suy ra được các quy ước Acme ẩn; dự đoán điểm đánh giá không tăng rõ so với baseline và token tăng. Căn cứ: baseline học đã giải được nhiều check kỹ thuật nhưng bỏ sót quy ước; phân vai bổ sung công việc kiểm tra và chi phí gọi mô hình. [Anthropic](https://www.anthropic.com/engineering/multi-agent-research-system) mô tả lợi ích và chi phí của việc chia việc cho nhiều agent, nhưng bài nghiên cứu đó không chứng minh lợi ích trên các tác vụ nhỏ của lab này.
- H2: Skills-auto có khả năng đạt điểm đánh giá cao nhất nếu curator chuyển phản hồi quy ước học thành checklist dùng được ở tác vụ mới. Chưa có căn cứ để dự đoán đạt toàn bộ check; quy ước mới của tập đánh giá có thể chưa được bao phủ. [SkillsBench](https://arxiv.org/abs/2602.12670) cho thấy skill biên soạn có thể giúp tác tử, nhưng không thể suy trực tiếp lợi ích đó cho skill do curator của lab tự sinh.
- H3: Mức tăng điểm do skill trên tác vụ học dự đoán lớn hơn hoặc bằng mức tăng trên tác vụ đánh giá. Curator nhận phản hồi của tập học, còn tập đánh giá có dữ liệu và quy ước mới. [SkillEvolBench](https://arxiv.org/abs/2605.24117) cho thấy thích nghi cục bộ có thể không chuyển thành kỹ năng dùng lại ổn định; cần tách tập học/đánh giá và giữ nguyên skill sau đóng băng.

Các giả thuyết trên chưa được kiểm chứng. Không sửa lại dự đoán sau khi đã xem kết quả đánh giá; khi tiếp tục lab, lưu dấu băm tệp này trong `freeze.json` trước khi chạy đánh giá.
