# Documentation & Report Artifacts

This folder contains **academic/report deliverables and their generator scripts** for the
StockPilot CSE5015 project. **None of it is part of the running application** — the whole
folder can be deleted after the project is submitted, with no effect on the backend.

## Contents

### Generated documents (deliverables)
| File | What it is |
|---|---|
| `st.docx` / `st_corrected.docx` | The full formatted project proposal (corrected + reorganised) |
| `StockPilot_Chapters_1_and_2.docx` | Chapter 1 & 2 write-up |
| `StockPilot_Feasibility_Report.docx` / `_v2.docx` | Feasibility study report |
| `StockPilot_Survey_Findings.docx` | Requirement-gathering survey findings |
| `StockPilot_System_Functionality_Corrected.docx` | Corrected 5-layer system functionality |
| `StockPilot_Expert_Interview.pdf` | Expert (QA engineer) interview record |
| `StockPilot_Database_Documentation.pdf` | Database-layer documentation |
| `StockPilot_Backend_Documentation.pdf` | Backend documentation |
| `StockPilot_AI_ML_Guide.pdf` | AI/ML guide |
| `StockPilot_Gantt_Chart.pod` / `.xml` | Gantt chart (ProjectLibre / MS Project) |

### Generator scripts
| Script | Regenerate with |
|---|---|
| `generate_db_docs.py` | `uv run python documentation/generate_db_docs.py` |
| `generate_gantt.py` | `uv run python documentation/generate_gantt.py` |
| `generate_interview_pdf.py` | `uv run python documentation/generate_interview_pdf.py` |
| `generate_ai_ml_docs.py`, `generate_docs.py` | (earlier backend/AI-ML PDFs) |

## To remove after the project is finished

1. Delete this whole folder:
   ```bash
   rm -rf backend/documentation
   ```
2. (Optional) Remove the **doc-only Python dependencies** that were added just for
   generating these files — they are NOT used by the application:
   ```bash
   uv remove reportlab python-docx pdfplumber openpyxl pymupdf
   ```
   > Keep **vectorbt** — it IS used by the live backtesting engine.
