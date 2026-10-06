# TÙY CHỌN: chạy lab trong container để shell của tác tử không chạm vào máy chủ của bạn.
# Build: docker build -t lab-deepagents-local .
# Real API runs on Windows: .\report\run_gemini.ps1
# The wrapper protects the credentials and hidden checks from the agent shell.
FROM python:3.12-slim
WORKDIR /lab
COPY pyproject.toml ./
COPY src ./src
RUN pip install --no-cache-dir -e .
RUN apt-get update && apt-get install -y --no-install-recommends git util-linux && rm -rf /var/lib/apt/lists/*
CMD ["bash"]
