# Báo cáo cá nhân: Self evolving Agentic

Ngày thực hiện thí nghiệm: 06/10/2026. Báo cáo tổng hợp kết quả hiện có trong kho mã nguồn; phần chi tiết và hồ sơ kiểm chứng nằm tại [report/REPORT.md](report/REPORT.md).

## 1. Thông tin cá nhân và cấu hình

| Họ tên | Mã sinh viên | Hình thức | Phần thực hiện |
|---|---|---|---|
| Mai Văn Trung | 2A202602513 | Cá nhân | Toàn bộ bài thực hành: harness, thí nghiệm, phân tích và báo cáo; có sử dụng trợ lý Codex |

Tôi hoàn thiện các hàm TODO trong `agent.py`, `subagents.py`, `runner.py` và `curator.py`. Bộ test ngoại tuyến đã đạt **29/29**, gồm 12 test mã có sẵn, 9 test agent, 6 test runner và 2 test curator; xem [kết quả test](report/pytest.txt).

- Mô hình chạy ma trận chính: `LAB_MODEL=google_genai:gemini-3.1-flash-lite`, sử dụng `GEMINI_API_KEY`; `LAB_TEMPERATURE=0`, `recursion_limit=60`.
- Môi trường: Python 3.12.15, Deep Agents 0.7.21, langchain-google-genai 4.4.0; Docker Linux trên Windows. Shell tác tử chạy UID 65534, không kế thừa khóa API và không đọc được thư mục chứa khóa/bộ chấm ẩn.
- Skill được curator sinh trong phiên OpenRouter trước đó, rồi giữ nguyên để sử dụng với Gemini. Tôi không trộn kết quả OpenRouter vào bảng chính Gemini.
- Có **18/18 bản ghi chính**, **17 lượt không lỗi thực thi** và **3/3 lượt development trước tag**. Phiên hoàn thiện Git có 17 lượt thử mới, gồm development và các lần thử lại, sử dụng **1.803.570 token**, có 3 lỗi recursion; sáu lượt baseline/subagents học được giữ từ phiên trước, không nằm trong ngân sách này.
- Commit giả thuyết: `7dc9055bfbb66ffa634460319f8b7e61ec7d6384`.
- Commit của tag `freeze`: `3d23bd90241677d23f14b648c7df9ddc1e7abbe9`, lúc `2026-10-06T12:51:01+07:00`.
- Commit kết quả/báo cáo sau freeze: `0ca0365`. Khóa thật chỉ nằm trong `.env` được Git ignore; không đưa khóa vào báo cáo và không push.

## 2. Giả thuyết trước tag `freeze` (Phần 4.0)

- **H1 — subagents so với baseline:** Subagents không tăng rõ điểm đánh giá nhưng có thể tăng token. Việc chia vai trò không tự cung cấp những quy ước Acme ẩn mà baseline học đã vi phạm. Tài liệu [Multi-agent research system của Anthropic](https://www.anthropic.com/engineering/multi-agent-research-system) là căn cứ tham khảo về lợi ích và chi phí giao việc, không bảo đảm hiệu quả trên các tác vụ nhỏ của lab.
- **H2 — skills-auto so với baseline:** Skills-auto có khả năng đạt điểm cao nhất nếu curator tổng quát hóa đúng phản hồi học và tác tử áp dụng skill. Những quy ước mới ở tập đánh giá có thể chưa được bao phủ. [SkillsBench](https://arxiv.org/abs/2602.12670) là tài liệu tham khảo về đánh giá skill; kết quả của tài liệu không bảo đảm skill trong lab sẽ hữu ích.
- **H3 — học so với đánh giá:** Mức cải thiện do skill trên tác vụ học lớn hơn hoặc bằng mức cải thiện trên tác vụ đánh giá. Skill có thể thích nghi với schema học nhưng chuyển giao chưa tốt; [SkillEvolBench](https://arxiv.org/abs/2605.24117) là tài liệu tham khảo cho việc phân biệt thích nghi và chuyển giao.

Các giả thuyết gốc được giữ trong [HYPOTHESES.md](report/HYPOTHESES.md) và đã có trong `report/REPORT.md` ở commit `hypotheses` trước tag mới. Tôi đã biết kết quả đánh giá của phiên cũ trước khi hoàn thiện Git; do đó phiên tiếp tục này không phải đăng ký mù lần đầu. Việc điền tài liệu này sau thí nghiệm không thay thế hồ sơ giả thuyết đã commit.

## 3. Làm quen Deep Agents (Phần 0.3)

1. Tác tử mặc định có các công cụ tệp `ls`, `read_file`, `write_file`, `edit_file`, `delete`, `glob`, `grep`; công cụ shell `execute`; và công cụ giao việc `task`. `execute` cho phép chạy lệnh trong sandbox.
2. `general-purpose` có các công cụ tương tự agent chính. Mỗi lần gọi mặc định không giữ trạng thái: subagent chỉ thấy prompt giao việc và trả lại một báo cáo cuối, không tự nhận toàn bộ hội thoại của agent chính. Vì vậy lời giao việc phải có đủ mục tiêu, đường dẫn, quy tắc và kết quả cần trả về.
3. System prompt mặc định rỗng nếu không truyền `system_prompt`. Một câu hướng dẫn từ mô tả `task` là “Put full detail in the prompt and state exactly what it should return”; từ `execute` là “Use absolute paths and avoid `cd` so the working directory stays stable”. Trong harness của lab, tôi giữ nguyên `PATHS_NOTE` về đường dẫn shell tương đối `workspace/...` và gốc ảo của công cụ tệp.

Bằng chứng: [tour.txt](report/tour.txt). Tour dùng mô hình giả, không tốn token và không chứng minh đã gọi model thật.

## 4. Đường cơ sở và phân loại lỗi (Phần 2.2)

Tôi phân loại chín check thất bại của ba tác vụ **học** trong `results/baseline/`; không dùng lỗi API hoặc lượt bị cắt ở tập đánh giá để thay cho bằng chứng học.

| Tác vụ | Check thất bại | Nhóm lỗi | Bằng chứng từ `detail` |
|---|---|---|---|
| code-learn | rule_type_hints | E | Hàm public phải có type annotations cho mọi tham số và giá trị trả về. |
| code-learn | rule_regression_tests | E | Phải thêm `tests/test_regressions.py` với ít nhất ba test tương ứng các lỗi đã sửa. |
| code-learn | rule_changelog | E | Phải ghi từng bản sửa dưới `## Unreleased` theo dạng `- fix(<function name>): ...`. |
| data-learn | rule_money_in_cents | E | Tiền trong `answer.json` phải là integer cents; ví dụ 1606.67 USD được viết thành 160667. |
| data-learn | rule_meta_block | E | Phải có `meta` gồm `source`, `rows_in` tính cả trùng và `rows_used` là số đơn khác nhau có tiền đã biết. |
| data-learn | rule_clean_csv | E | Phải tạo CSV có header `order_id,timestamp_utc,region,amount_cents`, thời gian UTC và số tiền nguyên cents. |
| logs-learn | rule_service_names | E | Tên service phải viết thường và thay `-` bằng `_`. |
| logs-learn | rule_sorted_errors | E | `errors` phải sắp theo service rồi timestamp UTC tăng dần. |
| logs-learn | rule_schema_header | E | Đối tượng gốc phải có `schema_version: 2` và `generated_by: log-triage`. |

Các `detail` có tiền tố `RULE:` và tên check bắt đầu bằng `rule_`, nên nhóm E — vi phạm quy ước tổ chức — chiếm toàn bộ lỗi cuối lượt học. Baseline học đạt **18/18 check kỹ thuật**, **0/9 check quy ước**; đây là bằng chứng phủ định lỗi A–D trong phạm vi bộ check, không chứng minh tác tử luôn tránh chúng. Trace code cho thấy tác tử đọc đặc tả và chạy test; trace dữ liệu cho thấy tác tử tạo rồi đọc lại kết quả. Skill có thể phòng ngừa lỗi E nếu ghi đúng quy ước và được áp dụng, nhưng skill hiện tại chỉ bao phủ một phần họ dữ liệu.

Bằng chứng: [code-learn](results/baseline/code-learn/run.json), [data-learn](results/baseline/data-learn/run.json), [logs-learn](results/baseline/logs-learn/run.json) và [thống kê check](report/check_breakdown.txt).

## 5. Điều kiện `subagents` (Phần 2.3)

Tôi định nghĩa ba vai trò: `explorer` đọc đặc tả và tìm nguyên nhân, không sửa tệp; `implementer` thực hiện công việc có phạm vi và kiểm chứng; `reviewer` kiểm tra độc lập, không sửa. Mỗi `description` nêu khi nào nên giao việc, và mỗi vai trò được bổ sung nguyên `PATHS_NOTE`.

| Tác vụ | subagent_calls | Subagent được gọi | Token | Thời gian (giây) |
|---|---:|---|---:|---:|
| code-learn | 0 | Không giao việc | 131,054 | 112.1 |
| data-learn | 1 | general-purpose | 231,970 | 124.3 |
| logs-learn | 0 | Không giao việc | 56,977 | 39.1 |
| code-eval | 0 | Không giao việc | 82,670 | 68.9 |
| data-eval | 1 | general-purpose | 164,375 | 143.6 |
| logs-eval | 0 | Không giao việc | 44,978 | 29.2 |

Bốn lượt không giao việc vẫn là kết quả hợp lệ: tác tử có thể chọn giải quyết trực tiếp các tác vụ nhỏ. Đây là giải thích khả dĩ từ hành vi, không phải quan sát suy nghĩ nội bộ. Hai lượt giao việc đều dùng `general-purpose`; tôi chưa có bằng chứng thực nghiệm về hiệu quả khi sử dụng ba vai trò chuyên biệt đã định nghĩa.

Ở data-learn, lời giao việc truyền quy tắc bỏ trùng, sentinel -999 và chuẩn hóa dữ liệu, nhưng không nhắc nguyên câu Acme review bot. Subagent trả doanh thu 3189.59, trong khi baseline đạt check với 3130.24; agent chính đọc lại output/input nhưng không sửa được sai lệch bằng kiểm chứng độc lập.

Ở data-eval, lời giao việc có yêu cầu chuyển UTC trước khi xác định tháng. Agent chính tính lại bằng `datetime.fromisoformat` rồi xét `dt.month == 3` mà không chuyển `astimezone(timezone.utc)`, nên trượt hai check tháng/doanh thu UTC và đạt 3/9. Đây là lỗi D và kiểm chứng chưa đủ, không phải thiếu quy tắc UTC trong lời giao việc. Token trung bình subagents cao hơn baseline khoảng **1,20 lần** trong bảng chính; cần tính đến lỗi recursion của baseline khi diễn giải chi phí.

Bằng chứng: [trace data-learn](results/subagents/data-learn/trace.md), [trace data-eval](results/subagents/data-eval/trace.md). Trace chỉ lưu luồng chính; callback token có cộng các lời gọi model bên trong subagent.

## 6. Self-evolving: skill do curator sinh (Phần 3)

Curator đã gọi **ba lần** trong phiên OpenRouter: một lần đầu và hai lần chạy lại theo giới hạn GUIDE. Prompt chỉ dùng feedback/vết baseline data-learn không lỗi thực thi, không nhận tập đánh giá. Tôi giữ nguyên đầu ra curator, không sửa tay nội dung skill.

| Lần | Kết quả | Cách xử lý và lý do |
|---|---|---|
| 1 | Ba tên chứa underscore bị validator chặn | Làm rõ regex tên trong prompt, không sửa output. |
| 2 | Ba skill hợp lệ về định dạng | Loại hai skill: một khuyên dùng `/workspace` trong shell sai quy ước đường dẫn; một khuyên float/round cho chuyển tiền, chưa xử lý chắc sai số. |
| 3 | Validator chặn marker `orders` | Giữ nguyên validator; chọn lại nguyên văn skill hợp lệ từ lần 2. |

| Skill | Tổng quát hay riêng cho tác vụ học? | Đúng hay sai? | Độ dài, description và sử dụng ở Phần 3.4 |
|---|---|---|---|
| produce-answer-and-clean-csv | Tổng quát được thao tác đếm meta, bỏ trùng và tạo CSV; schema region cố định và ví dụ Q1 có nguy cơ quá khớp. | Chỉ dẫn meta/UTC phù hợp nhưng thiếu yêu cầu tiền JSON là integer cents; tham chiếu money-conversion chưa định nghĩa rõ quy tắc làm tròn. | 23 dòng toàn tệp, 19 dòng body. Description nhắm answer.json có meta và clean.csv; development data-learn đọc một skill, code/logs không đọc. |

Skill còn lại ở [SKILL.md](skills/auto/produce-answer-and-clean-csv/SKILL.md); nguồn gốc và lựa chọn được lưu trong [skill-review.json](report/skill-review.json) cùng các thư mục `report/curator-attempt-{1,2,3}/`. Skill hiện tại khớp byte với bản curator lần 2.

Development mới trước tag được lưu ở [results/skills-auto-dev/](results/skills-auto-dev/). Ba lượt dùng cùng skill, model và cap 60 với lượt chính; cả ba không lỗi thực thi.

| Tác vụ skills-auto chính thức | skills_read | Giải thích từ description và trace |
|---|---:|---|
| code-learn | 0 | Đề yêu cầu sửa package và chạy test; skill nhắm answer.json/meta/clean.csv, không hướng dẫn type hints, regression tests hoặc changelog. |
| code-eval | 0 | Tác tử sửa package bookings; tình huống này không khớp description về báo cáo dữ liệu. |
| logs-learn | 0 | Đề yêu cầu errors.json; skill về order_id/region/amount_cents không bao phủ quy ước service, sắp lỗi và schema log. |
| logs-eval | 0 | Output log triage khác schema dữ liệu của skill; skill không hướng dẫn counts_by_service hoặc quy ước source_line mới. |
| data-learn | 1 | Đề yêu cầu báo cáo dữ liệu, khớp description; trace có lời đọc SKILL.md và tạo meta/CSV, nhưng chỉ làm đúng một phần. |
| data-eval | 1 | Đề cũng tạo answer.json nên có sự phù hợp; trace đọc skill nhưng meta/CSV/tiền JSON vẫn chưa đạt check. |

Đây là suy luận về tình huống kích hoạt từ đề, description và trace. Tôi không khẳng định biết suy nghĩ nội bộ của model. Hai lượt dữ liệu bắt đầu bằng `ls`, đọc skill sau đó; `skills_read=1` không chứng minh tuân thủ yêu cầu FIRST action.

## 7. Kết quả so sánh (Phần 4.3, 4.4)

Bảng sau được lấy nguyên từ [report/table.md](report/table.md), do `lab.compare` có sẵn sinh ra. Điểm là tỷ lệ check đạt, không phải điểm chấm bài theo RUBRIC.

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
| **Mean tokens per run** | 98,945 | 118,670 | 85,855 |
| **Runs that read a skill** | 0/6 | 0/6 | 2/6 |

Đầu ra [scripts/check_breakdown.py](scripts/check_breakdown.py):

```text
condition     role    technical  house rules  mean tokens  read a skill
baseline      eval     18/18         0/12         113,361      0/3
baseline      learn    18/18         0/9           84,529      0/3
subagents     eval     16/18         0/12          97,341      0/3
subagents     learn    17/18         0/9          140,000      0/3
skills-auto   eval     18/18         0/12          70,266      1/3
skills-auto   learn    18/18         1/9          101,444      1/3
```

**Lỗi còn lại:** Baseline data-eval bị `GraphRecursionError` ở cap 60 trong cả ba lần thử. Tác tử lặp lệnh đếm distinct id; output dở dang đạt 5/9 nhưng không được coi là lượt hoàn tất. Tôi lưu hai lỗi trước ở [results/git-study-attempts/](results/git-study-attempts/), giữ nguyên lỗi cuối tại [run.json chính](results/baseline/data-eval/run.json), không đổi model/cap để lấp kết quả. Vì vậy có 18 bản ghi nhưng chỉ 17 lượt không lỗi thực thi.

Các lượt chính có `skills_modified=false`. Verifier gốc trả exit 0, **`checked 6 runs of skill conditions: OK`**; xem [git-freeze-check.txt](report/git-freeze-check.txt). Development nằm trước tag, sáu lượt skills-auto chính thức nằm sau tag; hash skill giữ nguyên `52427bc4ab4b6cac09d9544470d030f43135a9c624d60c5711b2806f3797890b`. [git-study-validation.json](report/git-study-validation.json) ghi kiểm tra Git/tính toàn vẹn đạt nhưng `ok=false` vì lỗi baseline còn lại.

## 8. Phân tích

### 8.1. So sánh học và đánh giá

Skills-auto tăng điểm trung bình học khoảng **0,042** so với baseline, chủ yếu do data-learn tăng từ 5/8 lên 6/8; điểm đánh giá không tăng. Subagents giảm khoảng **0,042** trên học và **0,074** trên đánh giá. H1 phù hợp hướng điểm/chi phí quan sát, H2 chưa được hỗ trợ về cải thiện đánh giá, H3 phù hợp với mức tăng trên học lớn hơn đánh giá.

Tăng ở học nhưng không tăng ở đánh giá cho thấy chuyển giao hạn chế; chưa đủ kết luận toàn bộ nguyên nhân là quá khớp. Skill thiếu quy tắc và model áp dụng chưa đúng cũng giải thích kết quả. So sánh điểm output baseline phải giữ giới hạn rằng data-eval chưa kết thúc; bản tham chiếu cũ không lỗi cũng đạt 5/9 được giữ riêng, không thay cho bản ghi chính mới.

### 8.2. Check kỹ thuật và check quy ước

Baseline và skills-auto đều đạt 18/18 kỹ thuật trên mỗi vai trò. Skill giúp một check quy ước học, `rule_meta_block`, nâng mức đạt từ 0/9 lên 1/9; quy ước đánh giá vẫn 0/12. Các quy ước mới như `rule_sorted_keys_format`, `rule_version_bump` và `rule_source_line` không được skill hiện tại bao phủ. Hai check kỹ thuật UTC bị mất ở subagents/data-eval là lỗi xử lý dữ liệu/kiểm chứng, không phải lỗi E.

### 8.3. Một check được giúp và các check chưa được giúp

Ở [trace data-learn](results/skills-auto/data-learn/trace.md), tác tử đọc skill và tạo meta có `rows_in=101`, `rows_used=86`; `rule_meta_block` đạt, còn baseline thiếu meta. Thay đổi này phù hợp chỉ dẫn đếm đơn khác nhau có tiền đã biết trong skill, nhưng một cặp lượt chưa chứng minh quan hệ nhân quả.

`rule_clean_csv` vẫn trượt dù đã đọc skill, tạo CSV và đếm 87 dòng. Input S-1032 có thời gian `2024-01-07T23:15:00-05:00`, CSV ghi `2024-01-07T23:15:00Z`, trong khi UTC đúng là `2024-01-08T04:15:00Z`. Kiểm tra số dòng không phát hiện lỗi chuyển múi giờ; đây là ví dụ làm theo một phần.

Ở [trace data-eval](results/skills-auto/data-eval/trace.md), meta ghi `rows_in=88`, `rows_used=83`, nhưng có 5 bản trùng và 7 đơn thiếu tiền. Theo chỉ dẫn known amount, rows_used phải là **88−5−7=76**. Vì vậy đọc skill chưa đủ để qua meta. Tiền JSON vẫn chưa ở dạng integer cents, và quy ước sorted keys mới không có trong skill; cả hai check đều trượt.

### 8.4. Chi phí và hiệu quả đa tác tử

| Điều kiện | Điểm TB | Token TB, làm tròn | Điểm / 10.000 token |
|---|---:|---:|---:|
| baseline | 0.631 | 98,945 | 0.0637 |
| subagents | 0.573 | 118,671 | 0.0483 |
| skills-auto | 0.651 | 85,856 | 0.0759 |

Bảng mục 7 dùng phép chia nguyên cho token trung bình theo `lab.compare`; bảng phân tích trên làm tròn số trung bình, nên có thể lệch một token. Skills-auto có điểm/token cao nhất quan sát. Subagents dùng khoảng 1,20 lần token baseline và điểm thấp hơn; chưa có bằng chứng rằng giao việc bù được chi phí trong lần đo này.

Tuy nhiên baseline bị recursion nên tốn token mà không kết thúc. Kiểm tra độ nhạy bằng token bản tham chiếu data-eval cũ đã hoàn tất, 122.909 thay cho 200.819 của lượt lỗi, cho baseline khoảng **85.960 token/lượt**, gần skills-auto. Vì vậy tôi không kết luận skill giảm token mạnh. Các lần lỗi ngoài bảng chính vẫn nằm trong ngân sách tổng; token không tự chuyển thành chi phí tiền vì còn phụ thuộc billing/cache/tier.

### 8.5. Rò rỉ dữ liệu và quá khớp

Curator chỉ nhận phản hồi học; skill giữ nguyên byte từ lần sinh thứ hai, không thêm tên input hoặc quy tắc đánh giá sau khi xem kết quả. Schema region cố định và ví dụ Q1 có nguy cơ khó chuyển sang schema category của đánh giá. Tôi giữ artifact prompt/reply, hash và lịch sử kết quả để kiểm chứng; việc validator chặn từ chung `orders` không tự chứng minh có rò rỉ.

Tôi đã biết đánh giá phiên trước. Tag mới xác nhận thời gian/hash của lượt mới, không xóa việc đã tiếp xúc đánh giá; đây là giới hạn tính hợp lệ cần công khai.

### 8.6. Nhiễu trước và sau đóng băng

| Tác vụ | Development trước tag | Chính thức sau tag | Δ điểm | Token development / chính thức | skills_read trước / sau |
|---|---|---|---:|---|---|
| code-learn | 7/10 | 7/10 | 0.000 | 149,808 / 177,852 | 0 / 0 |
| data-learn | 6/8 | 6/8 | 0.000 | 68,937 / 76,614 | 1 / 1 |
| logs-learn | 6/9 | 6/9 | 0.000 | 49,858 / 49,868 | 0 / 0 |

Ba cặp có cùng hash/model/cap, không sửa skill, và đúng thứ tự trước/sau tag; dữ liệu đối chiếu nằm trong [git-study-summary.json](report/git-study-summary.json). Chênh điểm quan sát đều bằng 0 nhưng token vẫn thay đổi. Điều này không chứng minh mọi lần chạy đều ổn định hoặc chi phí cố định; một cặp/task chưa đủ ước lượng khoảng tin cậy, nên không đọc mọi chênh lệch nhỏ giữa điều kiện thành hiệu quả học.

## 9. Hạn chế và tính hợp lệ

1. **Ít tác vụ và ít lần lặp:** chỉ ba task mỗi vai trò, một lượt chính và một cặp development/chính thức cho skill học. Không đủ suy rộng hoặc kiểm định ý nghĩa thống kê; temperature 0 không bảo đảm lặp y hệt.
2. **Đã biết đánh giá cũ:** commit/tag mới không khôi phục đăng ký mù trước lần đánh giá đầu tiên; giả thuyết và skill gốc được giữ để hạn chế điều chỉnh theo kết quả.
3. **Skill chuyển giữa provider/model:** curator học từ data-learn OpenRouter rồi áp dụng trên Gemini. Không thể kết luận về quy trình curator Gemini học từ đủ ba họ tác vụ; bảng chính giữ model/cap thống nhất và không trộn điểm OpenRouter.
4. **Baseline data-eval chưa kết thúc:** 5/9 là điểm output dở dang sau recursion, làm hạn chế so sánh hiệu quả của ba điều kiện và có thể tăng chi phí baseline. Lỗi và chi phí thử lại được giữ trong báo cáo.
5. **Vai trò và trace bị giới hạn:** hai lời giao việc đều general-purpose, chưa có lượt sử dụng ba vai trò riêng; trace chỉ luồng chính và cắt nội dung dài, nên không quan sát đầy đủ công việc bên trong subagent.
6. **Dữ liệu do giảng viên thiết kế và schema skill hẹp:** thành công một check meta không bảo đảm hiệu quả trên dự án thực tế; schema region có nguy cơ quá khớp.
7. **Sáu lượt học được giữ từ phiên trước:** cùng model/cap nhưng khác thời điểm với lượt mới; đây là yếu tố bổ sung hạn chế suy luận nhân quả.

## 10. Kết luận

Tôi hoàn thành bài thực hành cá nhân với harness đạt 29/29 test, 18 bản ghi chính và ba development trước tag; 17 lượt chính không lỗi thực thi. Skill giữ nguyên giúp data-learn tăng từ 5/8 lên 6/8 qua check meta, còn điểm đánh giá trung bình không tăng. Subagents có điểm thấp hơn và nhiều token hơn trong bảng chính, nhưng chưa kiểm chứng ba vai trò riêng và baseline data-eval còn lỗi recursion. Verifier gốc xác nhận đủ sáu lượt skills-auto sau tag hợp lệ, và ba cặp điểm học trước/sau freeze đều chênh 0. Tôi đề xuất lặp nhiều lần và dùng một bộ đánh giá mới chưa quan sát để kiểm chứng chuyển giao, đồng thời đo cả tỷ lệ kết thúc và chi phí retry.

## Phụ lục

**Lệnh và thứ tự thực hiện:** Cài đặt các TODO, kiểm tra ngoại tuyến/tour, chạy baseline/subagents học và curator trong phiên ban đầu; sau đó giữ skill nguyên bản, lưu kết quả cũ riêng và hoàn thiện Git bằng các lệnh sau. Ba development được chạy trước commit/tag; các lượt chính mới chạy sau tag.

```powershell
docker build -t lab-deepagents-local .
.\report\run.ps1 python -m pytest
.\report\run.ps1 python scripts/tour.py
.\report\run_gemini.ps1 python report/check_shell_isolation.py
.\report\run_gemini.ps1 python report/complete_git_freeze.py development
.\report\run.ps1 python report/git_study_report.py
git add -A
git commit -m "hypotheses: preserve predictions and complete pre-freeze development"
git commit --allow-empty -m "freeze skills"
git tag freeze
.\report\run_gemini.ps1 python report/complete_git_freeze.py official
.\report\run.ps1 python report/git_study_report.py
.\report\run.ps1 env GIT_CONFIG_COUNT=2 GIT_CONFIG_KEY_0=safe.directory GIT_CONFIG_VALUE_0=/lab GIT_CONFIG_KEY_1=core.autocrlf GIT_CONFIG_VALUE_1=true python scripts/verify_freeze.py
.\report\run.ps1 python -m lab.compare
.\report\run.ps1 env GIT_CONFIG_COUNT=2 GIT_CONFIG_KEY_0=safe.directory GIT_CONFIG_VALUE_0=/lab GIT_CONFIG_KEY_1=core.autocrlf GIT_CONFIG_VALUE_1=true python scripts/check_breakdown.py
```

Các lệnh tạo tag mô tả lịch sử đã thực hiện; không chạy lại để di chuyển tag hiện có. Cấu hình Git trong lệnh Docker chỉ cho phép đọc bind mount và xử lý CRLF, không sửa verifier. Baseline data-eval được thử lại sau khi lưu bản ghi lỗi riêng; chi tiết tái lập ở [REPRODUCE.md](report/REPRODUCE.md).

**Thử thách mở rộng:** chưa thực hiện đủ một hướng Phần 6. Ba cặp học dùng để đo nhiễu Phần 3.4/4.2, không phải bonus 6e vì chưa lặp thêm hai lần cho mọi điều kiện trên tập đánh giá.

**Hồ sơ:** [manifest Git freeze](report/git-freeze.json), [kế hoạch](report/git-study-plan.json), [báo cáo chi tiết](report/REPORT.md), [phân tích trace](report/git-study-observations.md) và [bản lưu phiên trước](report/pre-git-freeze/REPORT.md). Tôi không sửa skill bằng tay, không sửa bộ test/task/module có sẵn và không đưa khóa API vào Git.
