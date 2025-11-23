## Report Output Staging

Generated deliverables (Word, PDF, or interim Markdown) should land under this folder.

### Quick start

```bash
python analysis/security_domains/output/render_report.py
```

Defaults:

- Reads `analysis/security_domains/csv/ALL_CONTROLS.csv`.
- Writes a timestamped Markdown summary under `analysis/security_domains/output/report/`.

Extend or replace this script with DOCX templating when you wire up the production reporting toolchain. Keep only sanitized/demo outputs in source control.

