### Giao việc và kiểm chứng trong lượt subagents mới

Ở `results/subagents/data-eval/trace.md`, lời giao việc cho `general-purpose` nêu rõ giữ sự kiện đầu theo id, xử lý total dạng chuỗi/sentinel -1, chuẩn hóa category và chuyển UTC trước khi chọn tháng 3. Nó yêu cầu năm trường kết quả nhưng không truyền nguyên câu Acme review bot của đề; các quy ước ẩn chưa có trong lời giao việc.

Subagent trả `march_revenue_utc=53056.44`, `march_orders_utc=43`, category toys, missing=7, duplicates=5. Agent chính đọc answer.json và input, thử dateutil nhưng chưa có thư viện, rồi chuyển sang thư viện chuẩn. Phép tính lại dùng `datetime.fromisoformat(...replace('Z', '+00:00'))` và kiểm tra `dt.year == 2024 and dt.month == 3`, không gọi `astimezone(timezone.utc)`. Vì vậy nó đang chọn tháng ở offset gốc. Hai check tháng/doanh thu UTC trượt; ba check kỹ thuật còn lại đạt, tổng 3/9. Agent chính nói đã chuyển UTC trong câu trả lời cuối nhưng script lưu trong trace không làm bước đó. Đây là lỗi D và kiểm chứng chưa đủ, không phải bằng chứng quy tắc UTC bị thiếu trong lời giao việc.

Lượt này có một subagent call, dùng 164.375 token; không có lượt thật chọn explorer/implementer/reviewer trong những lời giao việc đã quan sát. Không được quy hiệu quả của general-purpose cho ba vai trò chưa được dùng. So chi phí giữa các điều kiện phải xem cả độ phủ và lỗi thực thi, không chỉ độ dài lời giao việc.

### Development skill trước Git freeze

Lượt development data-learn mới đọc `produce-answer-and-clean-csv/SKILL.md`, tạo meta với rows_used=86 và đạt `rule_meta_block`, trong khi baseline học thiếu meta. Skill quy định distinct order với known amount nên thay đổi này phù hợp nội dung skill. Tuy nhiên development vẫn trượt `rule_money_in_cents` và `rule_clean_csv`, dù đã tạo/đọc cả answer.json lẫn clean.csv. Đọc skill không chứng minh mọi quy tắc đã được làm đúng; nội dung skill không yêu cầu rõ các trường tiền trong JSON chuyển sang integer cents.

Các quan sát development dùng `results/skills-auto-dev/`, không lấy kết quả chính cũ để gán cơ chế cho lượt mới.

### Skill trong các lượt chính sau tag

Sáu lượt mới xác nhận cùng mẫu kích hoạt: code-learn/code-eval/logs-learn/logs-eval có skills_read=0, data-learn/data-eval có skills_read=1. Description nhắm tạo answer.json có meta và clean.csv, khớp đề hai task dữ liệu; bốn task còn lại sửa package hoặc tạo errors.json, không khớp output/schema skill. Giải thích này dựa trên phạm vi và hành vi quan sát, không khẳng định suy nghĩ nội bộ. Bảng mục 6 giải thích riêng từng lượt và giữ trace cũ để đối chiếu.

Data-learn chính thức đạt rule_meta_block: answer.json có rows_in=101 và rows_used=86, phù hợp chỉ dẫn đếm distinct order với known amount; baseline học thiếu meta và trượt check này. Các check kỹ thuật đều đạt. Tuy nhiên rule_clean_csv vẫn trượt: trace có input S-1032 là `2024-01-07T23:15:00-05:00`, output clean.csv là `2024-01-07T23:15:00Z`, trong khi UTC đúng là `2024-01-08T04:15:00Z`. Agent đã đọc skill, tạo CSV, đọc mười dòng đầu và đếm 87 dòng, nhưng kiểm tra số dòng không phát hiện sai chuyển múi giờ. rule_money_in_cents cũng trượt; skill nói cents cho CSV nhưng chưa yêu cầu rõ cents cho JSON. Đây là ví dụ đọc và làm theo một phần.

Data-eval đã đọc cùng skill nhưng rule_meta_block vẫn trượt: output rows_in=88, rows_used=83, duplicates=5, missing=7. Quy tắc known amount trong skill đòi 88−5−7=76, nên 83 chỉ là số distinct event chưa loại tiền thiếu. Tác tử ban đầu dùng datetime.timezone sai cách import, sửa lỗi rồi qua cả năm check kỹ thuật, gồm tháng/doanh thu UTC. Không coi lỗi trung gian đã sửa là lỗi thực thi cuối lượt. rule_clean_csv, rule_money_in_cents và rule_sorted_keys_format đều trượt; không thấy lời tạo/đọc clean.csv trong trace này. Quy ước mới sorted keys/format không có trong skill và không được bổ sung sau khi xem đánh giá.

Trace dữ liệu chính thức bắt đầu bằng ls; việc đọc SKILL.md diễn ra sau các công cụ đầu tiên. Vì vậy skills_read=1 không chứng minh đã làm đúng lời nhắc FIRST action hoặc toàn bộ nội dung skill. Không đổi prompt/skill để ép lượt sau đạt hơn.

Trên các lượt chính mới, skill cải thiện data-learn từ 5/8 lên 6/8 qua meta, còn data-eval giữ 5/9. Đây là chuyển giao hạn chế; lỗi meta/UTC khi áp dụng và nội dung thiếu quy tắc cũng giải thích kết quả, nên không quy toàn bộ việc không tăng điểm cho quá khớp.

### Giả thuyết, chi phí và lượt baseline bị cắt

H1 phù hợp hướng điểm quan sát: subagents thấp hơn baseline khoảng 0,074 trên đánh giá và dùng nhiều token hơn ở bảng chính, nhưng hai lần giao việc đều general-purpose; chưa kiểm chứng hiệu quả ba vai trò riêng. H2 chưa được hỗ trợ về tăng điểm đánh giá: skills-auto hòa điểm output baseline. H3 phù hợp chênh quan sát +0,042 trên học và +0,000 trên đánh giá; một lượt/task không chứng minh hiệu ứng nhân quả.

Baseline/data-eval mới đã thử ba lần, cả ba đều GraphRecursionError ở cap 60. Trace lặp cùng câu lệnh đếm distinct id và cho kết quả 83; output answer.json đã có và qua năm check kỹ thuật, nhưng model không kết thúc đúng cap. Hai lần đầu ở results/git-study-attempts/, lần cuối giữ tại thư mục chính. Không sửa error hoặc timestamp để biến chúng thành lượt hoàn tất. Vì vậy 5/9 là điểm output dở dang, không phải thành công thực thi; tỷ lệ hoàn tất và chi phí retry là một phần kết quả hệ thống.

Bản tham chiếu nguyên trạng trước Git tại results/pre-git-freeze/baseline/data-eval/ không lỗi thực thi, cùng model/cap, cũng đạt 5/9 và cùng các check. Nó hỗ trợ nhận xét về điểm output nhưng không thay cho lượt mới sau tag. Các so sánh với baseline hiện tại cần giữ giới hạn về việc model chưa kết thúc; không gọi đây là một phép so sánh ba điều kiện hoàn tất không lỗi.

Bảng chi phí chính dùng 98.945 token/lượt baseline, 118.670 subagents, 85.855 skills-auto. Subagents khoảng 1,20 lần baseline ở bảng này; skills-auto có điểm/token cao nhất quan sát, nhưng baseline/data-eval bị cắt làm tăng chi phí. Kiểm tra độ nhạy chỉ dùng token bản tham chiếu đã hoàn tất 122.909 thay cho 200.819 của lượt bị cắt: baseline khoảng 85.960 token/lượt, gần 85.855 của skills-auto. Do đó chưa thể kết luận skill làm giảm token mạnh; lợi thế chính trong dữ liệu này là thêm một check meta học, không phải cải thiện đánh giá. Độ nhạy không thay số liệu gốc trong table.md.

Ngân sách phiên mới còn bao gồm cả hai lần baseline lỗi đã lưu ngoài bảng chính, tổng 17 lượt thử với ba lỗi, 1.803.570 token. Điểm/token của một bảng chính không đại diện toàn bộ chi phí tìm được kết quả hoặc retry. Ba cặp development/chính thức đều chênh điểm 0, nhưng token code-learn 149.808→177.852, data-learn 68.937→76.614 và logs-learn 49.858→49.868 vẫn biến động; không suy ra mọi chênh nhỏ giữa điều kiện là tác động của skill.
