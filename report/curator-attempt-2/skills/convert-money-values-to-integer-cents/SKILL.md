---
name: convert-money-values-to-integer-cents
description: Use when you need to output monetary values as integer cents in JSON or CSV files.
---
- Receive the monetary value as a number (float, string, or decimal).
- If the value is a string, strip whitespace and any currency symbols.
- Convert to a float (or Decimal) safely.
- Multiply by 100 to shift two decimal places.
- Round to the nearest integer using `round` or equivalent to avoid floating‑point bias.
- Cast the result to an integer type (`int`).
- Verify that the integer represents cents correctly (e.g., 1606.67 → 160667).
- When writing JSON, ensure the integer is not serialized as a float (most libraries handle ints correctly).
- When writing CSV, output the integer without decimal points or formatting.
- Keep a record of the conversion for audit or debugging if needed.
