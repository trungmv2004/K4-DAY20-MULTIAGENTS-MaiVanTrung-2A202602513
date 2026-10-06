"""GUIDE Phần 1 - Định nghĩa subagent (tác tử con).   >>> SINH VIÊN CÀI ĐẶT <<<

Pseudo-code: guides/pseudocode/02_subagents.md
Kiểm tra:    pytest tests/test_02_agent.py
"""


def get_subagents() -> list[dict]:
    """Trả về danh sách subagent (ít nhất 2, tên khác nhau).

    Mỗi phần tử là một dict có các khóa bắt buộc:
      "name":          tên duy nhất (chữ thường, có thể có dấu gạch ngang)
      "description":   khi nào tác tử chính nên giao việc cho subagent này (viết như một hướng dẫn hành động)
      "system_prompt": chỉ dẫn cho subagent
    Gợi ý vai trò: explorer (đọc và báo cáo), implementer (thực hiện), reviewer (kiểm tra độc lập).
    """
    return [
        {
            "name": "explorer",
            "description": "Delegate when you need to inspect specifications, shared code or raw data before deciding how to solve a task.",
            "system_prompt": (
                "You inspect files and report evidence. Read the supplied instructions, README and relevant docstrings. "
                "Identify shared causes of failures or data quality issues. Do not edit files. "
                "Return relevant paths, findings and uncertainties to the parent; do not claim unverified facts."
            ),
        },
        {
            "name": "implementer",
            "description": "Delegate when a scoped code fix or data/log transformation needs to be implemented and tested.",
            "system_prompt": (
                "Implement the task using the rules and paths supplied by the parent. Inspect relevant specifications first. "
                "Fix shared causes rather than symptoms, preserve source inputs and existing tests, and run Python or tests "
                "to verify the result. Report files actually changed, validation results and unresolved issues."
            ),
        },
        {
            "name": "reviewer",
            "description": "Delegate after implementation when outputs need an independent check against all task rules and edge cases.",
            "system_prompt": (
                "Review independently without editing files. Read the supplied rules and actual output files. "
                "Run relevant tests or validation commands; check schemas, edge cases and completion claims. "
                "Report concrete evidence, failed requirements and remaining uncertainties."
            ),
        },
    ]
