# AGENTS.md

## Project purpose

This is a beginner apprenticeship portfolio project.

The goal is to build a small, working and interview-defensible Python data pipeline using the ORR Table 1410 station-usage CSV.

The pipeline should:

1. Fetch the raw CSV.
2. Preserve the raw file unchanged.
3. Clean the data with pandas.
4. Write a processed CSV.
5. Validate the processed data and exit non-zero when validation fails.
6. Use clear Git commits.
7. Be explainable in plain English.

Prioritise simplicity, correctness and understanding over advanced architecture.

## User environment

The user works on Windows using:

- PowerShell
- VS Code
- Git and GitHub
- a local Python virtual environment
- beginner-level Python, pandas, Git and Linux knowledge

At the start of coding sessions, remind the user to activate:

```powershell
.\venv\Scripts\Activate.ps1
