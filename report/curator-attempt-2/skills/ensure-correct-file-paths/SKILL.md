---
name: ensure-correct-file-paths
description: Use when you need to read or write files in a workspace and are unsure about the correct path format.
---
- Check the current working directory with `pwd` or equivalent.
- Prefer relative paths rooted at the workspace (e.g., `workspace/file.csv`) unless an absolute path is confirmed.
- If you suspect an absolute path, verify the workspace root (often `/workspace` or the directory shown by `pwd`).
- Use `os.path.join` or path‑library helpers to construct paths instead of string concatenation.
- Before opening a file for reading, confirm its existence with a file‑existence check or try‑catch.
- Before writing, ensure the target directory exists; create it if needed (`mkdir -p` or equivalent).
- After opening, perform a quick read/write test (e.g., read first line) to catch permission issues early.
- Log the final path used for debugging.
- If a command fails with “No such file or directory”, re‑examine the path and retry.
