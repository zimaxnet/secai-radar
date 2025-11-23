## Questionnaire Generation Scaffold

Use this directory to script the questionnaire export that feeds the SecAI Radar app.

### Generate the walkthrough

```bash
python analysis/security_domains/questionnaire/generate_questionnaire.py
```

Defaults:

- Reads `analysis/security_domains/csv/ALL_CONTROLS.csv`.
- Writes a timestamped Markdown file under `analysis/security_domains/questionnaire/output/`.

Override inputs/outputs with `--csv`, `--output-dir`, or `--filename`.

> Extend the script as you refine stakeholder templates (for example, export to DOCX or include tenant-specific metadata).

Keep auxiliary tooling (prompt templates, intake forms, etc.) in this directory so the questionnaire workflow remains self-contained.

