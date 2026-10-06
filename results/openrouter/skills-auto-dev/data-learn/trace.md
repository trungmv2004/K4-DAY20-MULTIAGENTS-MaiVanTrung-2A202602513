### Human
Analyse the sales data in `workspace/sales.csv` (see `workspace/README.md` for the column descriptions).

Write a file `workspace/answer.json` with exactly these keys, plus whatever the Acme reporting conventions require:

- `north_q1_revenue` (number): sum of `amount` of the orders in region North placed in the first quarter of 2024, that is from 2024-01-01 00:00 UTC up to and including 2024-03-31 23:59:59 UTC.
- `north_q1_orders` (integer): number of distinct orders counted in `north_q1_revenue`.
- `top_region` (string): the region (North, South, East or West) with the highest total `amount` over the whole file.
- `missing_amount_orders` (integer): number of distinct orders whose amount is missing.
- `duplicate_rows_removed` (integer): number of duplicate rows you removed.

Orders with a missing amount must not be added to any revenue.
Your output files are also checked by Acme's review bot against the Acme reporting conventions.
When you are done, reply with a short summary of how you cleaned the data.


### Tool call: ls
{"path": "/workspace"}

### Tool result
['/workspace/README.md', '/workspace/sales.csv']

### Tool call: read_file
{"file_path": "/workspace/README.md"}

### Tool result
@@ lines 1-8 of 8 @@
# sales.csv - data dictionary

| column | description |
|---|---|
| order_id | order identifier. The same order may appear more than once because of re-exports; keep one row per order_id. |
| date | when the order was placed. Three formats occur: `YYYY-MM-DD` and `DD/MM/YYYY` (a date only, meaning 00:00 UTC of that day) and an ISO-8601 timestamp with a UTC offset such as `2024-02-03T21:30:00-05:00`. |
| region | sales region (North, South, East, West). Spelling and capitalisation are not consistent. |
| amount | order amount in USD. The value `-999` means the amount is unknown (missing). |

### Tool call: read_file
{"file_path": "/workspace/sales.csv", "limit": 10}

### Tool result
@@ lines 1-10 of 102 | next offset 10 @@
order_id,date,region,amount
S-1090,2024-03-05T16:15:00+00:00,west,591.39
S-1022,09/02/2024,NORTH,379.22
S-1005,2024-05-26T12:30:00-05:00,West ,513.84
S-1020,2024-02-23, North,-999
S-1014,10/06/2024,west,335.88
S-1010,16/04/2024, East,145.97
S-1002,20/06/2024, South,-999
S-1076,2024-03-20, South,346.27
S-1032,2024-01-07T23:15:00-05:00,South,637.30

### Tool call: ls
{"path": "/skills"}

### Tool result
['/skills/produce-answer-and-clean-csv/']

### Tool call: read_file
{"file_path": "/skills/produce-answer-and-clean-csv/SKILL.md", "limit": 1000}

### Tool result
@@ lines 1-23 of 23 @@
---
name: produce-answer-and-clean-csv
description: Use when you must generate answer.json with a meta block and clean.csv according to the specification.
---
- Determine the input file name (source) from the provided path or arguments.
- Read all rows, counting total rows (`rows_in`).
- Track distinct order IDs and whether each has a known amount (not missing/sentinel).
- Compute `rows_used` as the count of distinct order IDs with a known amount.
- Build the meta object: `{ "source": <input file name>, "rows_in": <rows_in>, "rows_used": <rows_used> }`.
- Compute any required result fields (e.g., region totals, Q1 revenue, etc.) per the task logic.
- Assemble the final JSON dictionary containing the result fields plus the `meta` object.
- Write the dictionary to `workspace/answer.json` with proper JSON formatting (indent optional but valid).
- For clean.csv:
  - Define header: `order_id,timestamp_utc,region,amount_cents`.
  - For each distinct order with a known amount:
    - Use the first encountered row for that order_id.
    - Convert the timestamp to UTC and format as `YYYY-MM-DDTHH:MM:SSZ`.
    - Normalize region: trim whitespace, convert to title case, and map to canonical spelling (North, South, East, West).
    - Convert amount to integer cents using the money‑conversion rule.
    - Write one row with the fields in header order.
- Ensure each order_id appears exactly once in clean.csv.
- After writing, optionally verify line count matches `rows_

### Tool call: execute
{"command": "wc -l /workspace/sales.csv"}

### Tool result
[stderr] wc: /workspace/sales.csv: No such file or directory

Exit code: 1
[Command failed with exit code 1]

### Tool call: execute
{"command": "wc -l workspace/sales.csv"}

### Tool result
102 workspace/sales.csv

[Command succeeded with exit code 0]