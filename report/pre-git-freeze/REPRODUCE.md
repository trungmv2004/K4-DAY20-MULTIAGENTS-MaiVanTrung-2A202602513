# Chạy tiếp lab bằng Gemini trên Windows

Chạy PowerShell từ thư mục gốc của kho; Docker Desktop dùng Linux containers.

## Cấu hình

`.env` giữ `GEMINI_API_KEY` và `OPENROUTER_API_KEY`. Provider đang hoạt động:

```dotenv
GEMINI_API_KEY=your-key-here
LAB_MODEL=google_genai:gemini-3.1-flash-lite
LAB_TEMPERATURE=0
AZURE_OPENAI_ENDPOINT=
AZURE_OPENAI_KEY=
AZURE_OPENAI_DEPLOYMENT_MODEL=
```

`model.py` ưu tiên bộ ba Azure/OpenAI khi cả ba được điền, nên phải để chúng trống khi dùng Gemini. LangChain nhận trực tiếp `GEMINI_API_KEY`; nếu có `GOOGLE_API_KEY`, biến đó được ưu tiên. Không truyền khóa trên dòng lệnh, không commit `.env`.

## Chạy và kiểm tra

```powershell
docker build -t lab-deepagents-local .
.\report\run.ps1 python -m pytest
.\report\run_gemini.ps1 python report/check_shell_isolation.py
.\report\run_gemini.ps1 python report/continue_gemini.py all --recursion-limit 60
.\report\run.ps1 python report/summarize_gemini.py
.\report\run.ps1 python report/verify_local_freeze.py
.\report\run.ps1 python -m lab.compare
```

`run_gemini.ps1` dùng bản sao kho riêng trong container. Thư mục `/host` và `/lab` chỉ tiến trình runner được truy cập; shell agent chạy dưới UID 65534, không có quyền đọc khóa, check ẩn hoặc môi trường tiến trình cha. Chỉ đồng bộ `results/` và `report/` ra kho sau khi kết thúc; không đồng bộ task/test/skill nguồn. Không dùng wrapper `run.ps1` thông thường để chạy model thật vì mount `/lab` trong chế độ đó vẫn có thể được shell đọc.

Script chạy tuần tự: baseline/subagents học; lặp skills-auto học; baseline/subagents đánh giá; skills-auto cả sáu task. Nó giữ lượt đã hoàn tất trên đúng model, lưu lượt bị thay thế ở `results/gemini-attempts/`, và dừng khi quota hoặc lỗi thực thi ngăn tiếp tục. Lượt lặp học nằm ở `results/gemini-repeat/`, dùng cùng skill/model/cap và diễn ra sau freeze gốc; đây không phải development trước freeze theo GUIDE.

Chạy riêng `learning`, `repeat`, `evaluation` thay cho `all`. Kết quả chính Gemini ở `results/{baseline,subagents,skills-auto}/`. OpenRouter được giữ ở `results/openrouter/`, `results/attempts/`, `results/platform-before-lf/`; báo cáo cũ ở `report/openrouter/`. Bảng chính chỉ đọc ba điều kiện ở cấp gốc, không trộn model.

**Giữ nguyên** `skills/auto/`, `report/HYPOTHESES.md`, `report/freeze.json` và `report/REPORT-before-eval.md`. Curator đã gọi ba lần (đạt giới hạn GUIDE), không chạy lại sau khi đã xem đánh giá. Skill do OpenRouter sinh được chuyển sang Gemini; đây là phiên tiếp tục, không phải một thí nghiệm mới đăng ký từ đầu.

Không commit, push hoặc tạo tag. `scripts/verify_freeze.py` vẫn không đạt vì thiếu commit/tag; kiểm tra cục bộ không thay thế tiêu chí Git. `scripts/check_breakdown.py` ẩn đánh giá khi chưa có tag; `report/observed-breakdown.json` bổ sung thống kê kết quả có thật sau mốc cục bộ.

Tham khảo: [LangChain API key](https://reference.langchain.com/python/langchain-google-genai/_common/_BaseGoogleGenerativeAI/google_api_key), [Gemini model](https://ai.google.dev/gemini-api/docs/latest-model), [hạn mức](https://ai.google.dev/gemini-api/docs/rate-limits).

