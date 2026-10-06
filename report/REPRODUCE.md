# Tái lập phiên hoàn thiện Git freeze

Người dùng đã cho phép commit/tag freeze. Không push. Hồ sơ cũ nằm ở report/pre-git-freeze/ và results/pre-git-freeze/; không sửa chúng để thay đổi lịch sử.

## Môi trường và khóa

Chạy PowerShell tại gốc kho, Docker Desktop dùng Linux containers. .env được ignore; giữ khóa thật tại đó, không truyền khóa trên dòng lệnh hay đưa vào commit.

```dotenv
GEMINI_API_KEY=your-key-here
LAB_MODEL=google_genai:gemini-3.1-flash-lite
LAB_TEMPERATURE=0
AZURE_OPENAI_ENDPOINT=
AZURE_OPENAI_KEY=
AZURE_OPENAI_DEPLOYMENT_MODEL=
```

Giữ OPENROUTER_API_KEY nếu có; lượt mới chỉ dùng Gemini. model.py ưu tiên bộ ba Azure nếu điền đủ, nên để trống chúng. Không đổi model/cap giữa development và lượt chính.

```powershell
docker build -t lab-deepagents-local .
.\report\run.ps1 python -m pytest
.\report\run_gemini.ps1 python report/check_shell_isolation.py
```

run_gemini.ps1 tạo bản sao kho riêng; shell agent chạy UID 65534, không đọc khóa/check ẩn/môi trường runner. Chỉ đồng bộ report/results đã đổi về host. Không dùng wrapper Docker thông thường để chạy model thật.

## Thứ tự đã thực hiện

1. Lưu git-study-plan.json; giữ skill curator nguyên bản. Lưu cả ma trận cũ riêng, giữ sáu baseline/subagents học cùng model/cap ở cấp gốc. Chuyển các đánh giá cũ và skills-auto cũ vào results/pre-git-freeze/. Không gọi curator thêm.
2. Chạy ba development học mới vào results/skills-auto-dev/<task>/; chưa tạo tag.

```powershell
.\report\run_gemini.ps1 python report/complete_git_freeze.py development
.\report\run.ps1 python report/git_study_report.py
```

3. Xác nhận đủ ba development không lỗi, cùng hash/model/cap. REPORT.md giữ H1–H3 gốc, nguồn/lý do, công khai đã thấy đánh giá cũ. Commit hypotheses, rồi commit freeze riêng và tạo tag.

```powershell
git add -A
git diff --cached --name-only
git commit -m "hypotheses: preserve predictions and complete pre-freeze development"
git commit --allow-empty -m "freeze skills"
git tag freeze
```

Chỉ tạo tag khi chưa tồn tại; không di chuyển tag, sửa lịch sử hay giả mạo thời gian. .env phải được ignore và không có trong staging. Sau khi tạo tag, git-freeze.json ghi SHA hypotheses/tag, thời gian commit tag, hash skill và trạng thái development lấy từ Git thật.

4. Chạy 12 lượt mới: baseline/subagents đánh giá và skills-auto cả sáu task. Cộng sáu baseline/subagents học thành 18 lượt chính.

```powershell
.\report\run_gemini.ps1 python report/complete_git_freeze.py official
.\report\run.ps1 python report/git_study_report.py
```

Script giữ lượt hoàn tất thuộc đúng phiên, lưu lỗi và dừng nếu hết quota. Nếu cần chạy lại lỗi, lưu bản ghi lỗi riêng trước; không sửa run.json để biến lỗi thành thành công.

5. Kiểm tra verifier gốc, bảng và breakdown; hoàn thiện phân tích trace/báo cáo, rồi commit kết quả cuối. Giữ tag/skill nguyên trạng, không push.

```powershell
.\report\run.ps1 env GIT_CONFIG_COUNT=2 GIT_CONFIG_KEY_0=safe.directory GIT_CONFIG_VALUE_0=/lab GIT_CONFIG_KEY_1=core.autocrlf GIT_CONFIG_VALUE_1=true python scripts/verify_freeze.py
.\report\run.ps1 python -m lab.compare
.\report\run.ps1 env GIT_CONFIG_COUNT=2 GIT_CONFIG_KEY_0=safe.directory GIT_CONFIG_VALUE_0=/lab GIT_CONFIG_KEY_1=core.autocrlf GIT_CONFIG_VALUE_1=true python scripts/check_breakdown.py
```

Hai cấu hình Git chỉ áp dụng cho tiến trình đọc bind mount trong Docker và xử lý CRLF Windows; không sửa verifier hoặc repository config.

## Đối chiếu và giới hạn

git-study-summary.json lưu ba cặp development/chính thức và chênh điểm. Development phải trước commit tag; sáu skills-auto chính thức phải sau tag, cùng hash/model/cap, skills_modified=false. Các lượt lặp cũ sau freeze cục bộ không thay thế development mới.

Đã thấy đánh giá phiên trước: tạo tag mới không khôi phục lịch sử đó. Giữ giả thuyết/skill gốc, không gọi đây là đăng ký mù lần đầu. Cần bộ đánh giá mới chưa biết nếu muốn kiểm định chuyển giao mù.

continue_gemini.py, summarize_gemini.py và verify_local_freeze.py mô tả phiên cục bộ cũ; không dùng chúng để sinh lại báo cáo chính phiên Git. freeze.json, HYPOTHESES.md, REPORT-before-eval.md và đầu ra curator ban đầu được giữ nguyên.
