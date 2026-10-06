# Chạy lại lab với OpenRouter trên Windows

Chạy PowerShell từ thư mục gốc của kho. Yêu cầu Docker Desktop đang chạy Linux containers.

**Trạng thái hiện tại:** đã đóng băng cục bộ một skill, đã chạy thử học/đánh giá dữ liệu nhưng các lượt bị cắt, và khóa mới đã hết quota. Xem `REPORT.md` và `remaining-work.json`. Không chạy lại các bước sinh skill/development/freeze bên dưới trên thí nghiệm hiện tại. Để tiếp tục phần thiếu mà giữ nguyên skill/giả thuyết:

```powershell
.\report\run.ps1 python report/continue_lab.py frozen-learning --recursion-limit 60
.\report\run.ps1 python report/continue_lab.py evaluation --recursion-limit 60
.\report\run.ps1 python report/verify_local_freeze.py
```

Lượt mới dùng giới hạn 60 khác các lượt dữ liệu 16 bước trước đó; giữ và ghi rõ cả hai cấu hình. `frozen-learning` chỉ bổ sung dữ liệu so sánh baseline/subagents, không gọi curator. Việc bổ sung học sau freeze là sai khác so với thứ tự GUIDE, không được mô tả là đã thực hiện đúng protocol đầy đủ.

```powershell
docker build -t lab-deepagents-local .
.\report\run.ps1 python -m pytest
.\report\run.ps1 python scripts/tour.py
```

Trong `.env`, giữ khóa thật ở `OPENROUTER_API_KEY` trước dòng nội suy:

```dotenv
OPENROUTER_API_KEY=<khóa của bạn>
LAB_TEMPERATURE=0
AZURE_OPENAI_ENDPOINT=https://openrouter.ai/api/v1
AZURE_OPENAI_KEY=${OPENROUTER_API_KEY}
AZURE_OPENAI_DEPLOYMENT_MODEL=nvidia/nemotron-3-super-120b-a12b:free
```

`model.py` có sẵn đọc cấu hình cổng tương thích OpenAI; `python-dotenv` nội suy khóa. Không dùng Docker `--env-file .env` vì Docker không nội suy `${OPENROUTER_API_KEY}`. Tệp `.env` bị loại khỏi Git và Docker build context. Shell của agent chỉ nhận PATH, HOME và PYTHONDONTWRITEBYTECODE.

Thứ tự thí nghiệm theo GUIDE cho một thí nghiệm mới, chưa có mốc đóng băng:

```powershell
.\report\run.ps1 python -m lab.runner --condition baseline --tasks data-learn
.\report\run.ps1 python -m lab.runner --condition baseline --tasks code-learn logs-learn
.\report\run.ps1 python -m lab.runner --condition subagents --tasks learn
.\report\run.ps1 python -m lab.curator
.\report\run.ps1 python -m lab.runner --condition skills-auto --tasks learn
```

Đọc các kết quả học và skill, viết H1–H3 trước khi chạy đánh giá. Lưu kết quả thử skill vào `results/skills-auto-dev/` trước khi chạy chính thức. Bản thực hiện này dùng `report/HYPOTHESES.md`, `report/REPORT-before-eval.md` và `report/freeze.json` làm bằng chứng đóng băng cục bộ vì người dùng yêu cầu không commit. Sau đóng băng không sửa skill.

```powershell
.\report\run.ps1 python -m lab.runner --condition baseline --tasks eval
.\report\run.ps1 python -m lab.runner --condition subagents --tasks eval
.\report\run.ps1 python -m lab.runner --condition skills-auto --tasks all
.\report\run.ps1 python -m lab.compare
.\report\run.ps1 python scripts/check_breakdown.py
.\report\run.ps1 python report/verify_local_freeze.py
```

Chạy lại cùng điều kiện ghi đè kết quả. Muốn giữ dữ liệu chính thức, truyền `--results results-repeat` cho runner. Không chạy lại curator sau đóng băng. Model miễn phí có hạn mức và độ sẵn sàng thay đổi; mọi lỗi API phải được giữ riêng, không dùng làm bằng chứng lỗi quy trình của agent.

`scripts/verify_freeze.py` gốc yêu cầu commit `hypotheses` và tag `freeze`, vì vậy không thể đạt yêu cầu này trong phiên không commit. Kiểm tra cục bộ bổ sung xác nhận dấu băm, thời gian, đủ sáu lần chạy skill và không sửa skill; không thay thế yêu cầu Git của thang điểm.

Đối với thí nghiệm mới chưa đóng băng, script giữ các lượt cũ và dừng khi gặp lỗi:

```powershell
.\report\run.ps1 python report/continue_lab.py learn
# Đánh giá skill sinh ra theo GUIDE 3.3 trước bước tiếp theo.
.\report\run.ps1 python report/continue_lab.py development
# Cập nhật báo cáo học trước đóng băng.
.\report\run.ps1 python report/continue_lab.py freeze
.\report\run.ps1 python report/continue_lab.py evaluation
.\report\run.ps1 python report/verify_local_freeze.py
```

Giữ nguyên model đã dùng cho các lượt giữ lại. Nếu đổi model, tách kết quả hoặc chạy lại mọi điều kiện để tránh so sánh khác cấu hình. `learn` chỉ chạy lại lượt thiếu/có lỗi, rồi sinh skill nếu chưa có. `freeze` không cho ghi đè dấu mốc hoặc đăng ký sau khi đã có kết quả đánh giá. `evaluation` ghi riêng các lượt bị thay thế, kiểm tra dấu băm và chạy lại toàn bộ tác vụ skills-auto bắt đầu trước dấu mốc đóng băng.

Tham chiếu cấu hình: [OpenRouter quickstart](https://openrouter.ai/docs/quickstart), [tool calling](https://openrouter.ai/docs/guides/features/tool-calling).
