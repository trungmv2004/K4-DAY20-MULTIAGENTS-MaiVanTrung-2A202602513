# B?o c?o tr??c ??nh gi? ? th? nghi?m ch?a ?? h?n m?c

Ng?y 06/10/2026, Asia/Bangkok. Gi? kh?a m?i; ng??i d?ng y?u c?u d?ng h?t h?n m?c v? l?u ph?n thi?u. Kh?ng commit ho?c push.

## 1. C?u h?nh
Nemotron 3 Super 120B A12B free qua OpenRouter, temperature=0, Docker Linux, Deep Agents 0.7.21. Baseline d?ng recursion_limit=60; ki?m tra skill/??nh gi? d? li?u d?ng 16 ?? d?nh h?n m?c.

## 2. Gi? thuy?t ?? vi?t tr??c m?i l?n ??nh gi?
# Giả thuyết trước đánh giá

Ngày lập: 06/10/2026, múi giờ Asia/Bangkok. Chưa chạy thí nghiệm đánh giá, chưa sinh skill thực tế và chưa đóng băng skill. Đây là đăng ký giả thuyết cục bộ; không có commit `hypotheses` theo yêu cầu không commit của người dùng.

- H1: Subagents có thể hỗ trợ đọc đặc tả và kiểm tra độc lập nhưng không tự suy ra được các quy ước Acme ẩn; dự đoán điểm đánh giá không tăng rõ so với baseline và token tăng. Căn cứ: baseline học đã giải được nhiều check kỹ thuật nhưng bỏ sót quy ước; phân vai bổ sung công việc kiểm tra và chi phí gọi mô hình. [Anthropic](https://www.anthropic.com/engineering/multi-agent-research-system) mô tả lợi ích và chi phí của việc chia việc cho nhiều agent, nhưng bài nghiên cứu đó không chứng minh lợi ích trên các tác vụ nhỏ của lab này.
- H2: Skills-auto có khả năng đạt điểm đánh giá cao nhất nếu curator chuyển phản hồi quy ước học thành checklist dùng được ở tác vụ mới. Chưa có căn cứ để dự đoán đạt toàn bộ check; quy ước mới của tập đánh giá có thể chưa được bao phủ. [SkillsBench](https://arxiv.org/abs/2602.12670) cho thấy skill biên soạn có thể giúp tác tử, nhưng không thể suy trực tiếp lợi ích đó cho skill do curator của lab tự sinh.
- H3: Mức tăng điểm do skill trên tác vụ học dự đoán lớn hơn hoặc bằng mức tăng trên tác vụ đánh giá. Curator nhận phản hồi của tập học, còn tập đánh giá có dữ liệu và quy ước mới. [SkillEvolBench](https://arxiv.org/abs/2605.24117) cho thấy thích nghi cục bộ có thể không chuyển thành kỹ năng dùng lại ổn định; cần tách tập học/đánh giá và giữ nguyên skill sau đóng băng.

Các giả thuyết trên chưa được kiểm chứng. Không sửa lại dự đoán sau khi đã xem kết quả đánh giá; khi tiếp tục lab, lưu dấu băm tệp này trong `freeze.json` trước khi chạy đánh giá.

## 3. C?ng c?
Tour ?? l?u trong tour.txt; execute ch?y shell, task giao vi?c cho subagent t?m. File tools c? ???ng d?n ?o; shell c?n ???ng d?n t??ng ??i theo BASE_PROMPT ???c gi? nguy?n.

## 4. D? li?u h?c v? l?i
Baseline data-learn ho?n t?t 5/8: 5/5 k? thu?t, 0/3 quy ??c. Code l?n ch?y m?i ??t 7/10 nh?ng c? GraphRecursionError do ???ng d?n; logs c? 0/9 c? GraphRecursionError. Ch? data-learn ho?n t?t ???c d?ng cho curator.

## 5. Subagents
Ba vai tr? explorer/implementer/reviewer ?? c?i v? qua test; ch?a c? l??t ch?y condition subagents th?t.

## 6. Skill v? ch?t l??ng
Curator g?i 3 l?n (2 l?n ch?y l?i, ??ng gi?i h?n GUIDE). L?n 1 b? t? ch?i t?n c? underscore; l?n 2 sinh 3 skill h?p l?; b? skill ???ng d?n sai v? ti?n khuy?n d?ng float/round ?? ch?ng sai s?. L?n 3 b? validator ch?n t? chung orders. Gi? nguy?n v?n produce-answer-and-clean-csv t? l?n 2, kh?ng s?a tay. Skill 23 d?ng, body 19 d?ng; c? quy ??c meta/clean.csv nh?ng thi?u y?u c?u r? cho ti?n trong answer.json v? m? t? l?m tr?n.

## 7. Ki?m tra skill tr?n h?c
data-learn: 0/8, 35538 token, skills_read=1, skills_modified=False, error=GraphRecursionError: Recursion limit of 16 reached without hitting a stop condition. You can increase the limit by setting the `recursion_limit` config key.
For troubleshooting, visit: https://docs.langchain.com/oss/python/langgraph/errors/GRAPH_RECURSION_LIMIT.
Model ??c skill nh?ng kh?ng ??c ??u ti?n v? ch?a t?o output tr??c gi?i h?n 16. Kh?ng coi ??y l? b?ng ch?ng skill l?m gi?m n?ng l?c.

## 8. Ph?n t?ch d? ki?n
Ch?a c? ?i?m ??nh gi?. S? t?ch l??t l?i, ph?n bi?t ??c skill v?i l?m theo, v? kh?ng suy lu?n so s?nh ba ?i?u ki?n khi thi?u d? li?u.

## 9. H?n ch?
Quota 50 l??t c?a t?i kho?n mi?n ph?; t?p h?c/??nh gi? v? ?i?u ki?n ch?a ??; recursion limit kh?c nhau; model l?p ???ng d?n; skill ch? nh?n feedback m?t t?c v? h?c. Ch?a ho?n t?t protocol GUIDE 2/3.4.

## 10. Tr?ng th?i tr??c ??nh gi?
??ng b?ng c?c b? m?t skill ?? ki?m tra chuy?n giao tr?n data-eval. Kh?ng c? Git freeze; kh?ng s?a skill sau m?c n?y. ??y l? th? nghi?m m?t ph?n, kh?ng tuy?n b? ?? ho?n th?nh b?i lab.
