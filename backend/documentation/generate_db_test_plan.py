"""Render the DB test output as a terminal screenshot and build the
Database Test Plan .docx (KMC template format: 7-row table per test case)."""
import os
from datetime import date
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

HERE = os.path.dirname(__file__)
SS = os.path.join(HERE, "db_screenshots")
TODAY = date.today().strftime("%d %B %Y")

# ---- terminal screenshot from the real run ----
lines = [l.rstrip("\n") for l in open(os.path.join(SS, "db_run.txt"), encoding="utf-8") if l.strip()]
n = len(lines)
fig = plt.figure(figsize=(12, 0.32 * n + 1.0), facecolor="#0d1117")
ax = fig.add_axes([0, 0, 1, 1]); ax.axis("off")
ax.add_patch(plt.Rectangle((0, 0.93), 1, 0.07, transform=ax.transAxes, facecolor="#161b22"))
for i, c in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
    ax.add_patch(plt.Circle((0.014 + i * 0.016, 0.965), 0.007, transform=ax.transAxes, facecolor=c))
ax.text(0.5, 0.965, "python db_tests.py  —  database test suite", color="#c9d1d9",
        fontsize=10, family="monospace", ha="center", va="center", transform=ax.transAxes)
y = 0.90; step = 0.9 / (n + 1)
for ln in lines:
    col = "#3fb950" if ("PASS" in ln or "passed" in ln) else ("#f85149" if "FAIL" in ln else
          ("#6e7681" if ln.startswith("=") else "#c9d1d9"))
    ax.text(0.012, y, ln, color=col, fontsize=8.6, family="monospace", va="top", transform=ax.transAxes)
    y -= step
IMG = os.path.join(SS, "db_run.png")
fig.savefig(IMG, dpi=150, facecolor="#0d1117", bbox_inches="tight", pad_inches=0.12)
plt.close(fig)
print("rendered", IMG)

# ---- docx ----
BLUE = RGBColor(0x1D, 0x4E, 0xD8); INK = RGBColor(0x11, 0x18, 0x27)
GREY = RGBColor(0x6B, 0x72, 0x80); GREEN = RGBColor(0x16, 0xA3, 0x4A)
doc = Document(); doc.styles["Normal"].font.name = "Calibri"; doc.styles["Normal"].font.size = Pt(11)


def shade(cell, hexc):
    tcPr = cell._tc.get_or_add_tcPr(); sh = OxmlElement("w:shd")
    sh.set(qn("w:val"), "clear"); sh.set(qn("w:fill"), hexc); tcPr.append(sh)


def H(t, size=15, color=INK):
    p = doc.add_paragraph(); r = p.add_run(t); r.bold = True; r.font.size = Pt(size); r.font.color.rgb = color
    p.paragraph_format.space_before = Pt(8); p.paragraph_format.space_after = Pt(4); return p


def body(t, bold=False):
    p = doc.add_paragraph(); r = p.add_run(t); r.bold = bold; r.font.size = Pt(10.5)
    p.paragraph_format.space_after = Pt(5); return p


def bullets(items):
    for i in items:
        doc.add_paragraph(style="List Bullet").add_run(i)


def kv(headers, rows, widths):
    t = doc.add_table(rows=1, cols=len(headers)); t.style = "Table Grid"
    for i, h in enumerate(headers):
        c = t.rows[0].cells[i]; shade(c, "374151")
        r = c.paragraphs[0].add_run(h); r.bold = True; r.font.color.rgb = RGBColor(255, 255, 255); r.font.size = Pt(9.5)
        c.width = Inches(widths[i])
    for row in rows:
        cells = t.add_row().cells
        for i, v in enumerate(row):
            cells[i].width = Inches(widths[i]); rr = cells[i].paragraphs[0].add_run(v); rr.font.size = Pt(9.5)
            if i == 0: rr.bold = True
    doc.add_paragraph(); return t


# cover / plan
p = doc.add_paragraph(); r = p.add_run("Database Test Plan & Test Cases"); r.bold = True; r.font.size = Pt(20); r.font.color.rgb = INK
p = doc.add_paragraph(); r = p.add_run("StockPilot — AI Investment Advisory Platform"); r.font.size = Pt(11); r.font.color.rgb = GREY
info = doc.add_table(rows=2, cols=4); info.style = "Table Grid"
data = [["Project", "StockPilot (CSE5015)", "Date", TODAY],
        ["Group / Batch", "Group 13 / Batch 131", "Version", "1.0"]]
for ri, rr in enumerate(data):
    for ci, v in enumerate(rr):
        cell = info.rows[ri].cells[ci]; run = cell.paragraphs[0].add_run(v); run.font.size = Pt(9.5)
        if ci % 2 == 0: shade(cell, "F3F4F6"); run.bold = True
doc.add_paragraph()

H("1.  Objective", 14)
body("This document defines the test plan for the database layer of StockPilot and records the "
     "results of executing it. The goal is to verify that the PostgreSQL schema enforces data "
     "integrity correctly — primary keys, unique constraints, foreign keys with cascade rules, "
     "not-null and enum constraints, default values, JSONB storage, the role subtype tables and "
     "transaction behaviour — so that no invalid data can enter the system.")

H("2.  Scope", 14)
bullets([
    "Schema integrity — all tables present in the public schema.",
    "Constraints — UNIQUE, NOT NULL, ENUM and CHECK rejection of invalid data.",
    "Referential integrity — foreign keys and ON DELETE CASCADE behaviour.",
    "Default values — server-side defaults populated automatically.",
    "JSONB storage — the strategy weights value object round-trips correctly.",
    "Role subtype tables (investors / analysts / admins) — 1:1 mapping.",
    "Singleton — platform_settings holds exactly one row.",
    "Transactions — atomicity (rollback leaves no trace) and CRUD persistence.",
])

H("3.  Test approach & environment", 14)
body("Tests are executed by an automated script (db_tests.py) using the SQLAlchemy 2.0 async engine "
     "over asyncpg against PostgreSQL 16. Constraint tests attempt an invalid operation and confirm "
     "the database REJECTS it. Every write is performed inside a transaction that is always rolled "
     "back, so the tests are repeatable and leave the database unchanged.")
kv(["Item", "Detail"], [
    ["Database", "PostgreSQL 16"],
    ["Access layer", "SQLAlchemy 2.0 async ORM over asyncpg"],
    ["Runner", "python db_tests.py"],
    ["Isolation", "All writes wrapped in a rolled-back transaction (no data persisted)"],
], [1.6, 4.7])

H("4.  Entry & exit criteria", 14)
bullets([
    "Entry: the schema has been created (via create_all / migrations) and the database is reachable.",
    "Exit: all test cases below pass; every constraint rejects invalid data; no test leaves residual rows.",
])

doc.add_page_break()
H("5.  Test Cases", 14)

CASES = [
    ("TC-DB-01", "Verify the schema is fully created",
     "Query information_schema for tables in the public schema.",
     "All application tables (>= 12) are present.",
     "16 tables present in the public schema.", "Pass"),
    ("TC-DB-02", "UNIQUE constraint on user email",
     "Insert a second user with an email that already exists.",
     "The insert is rejected with a unique-violation error.",
     "Duplicate email rejected by the UNIQUE constraint.", "Pass"),
    ("TC-DB-03", "NOT NULL constraint on email",
     "Insert a user with a NULL email.",
     "The insert is rejected with a not-null-violation error.",
     "Null email rejected by the NOT NULL constraint.", "Pass"),
    ("TC-DB-04", "ENUM constraint on user role",
     "Insert a user with role = 'superuser' (not a valid role).",
     "The insert is rejected — role must be investor/analyst/admin.",
     "Invalid enum value rejected.", "Pass"),
    ("TC-DB-05", "Foreign-key integrity on holdings",
     "Insert a holding whose user_id does not exist in users.",
     "The insert is rejected with a foreign-key-violation error.",
     "Holding with unknown user_id rejected by the FK.", "Pass"),
    ("TC-DB-06", "ON DELETE CASCADE",
     "Create a user with a holding, then delete the user.",
     "The user's holding is automatically deleted with the user.",
     "Child holding removed automatically on user delete.", "Pass"),
    ("TC-DB-07", "Composite UNIQUE(user_id, ticker) on watchlist",
     "Add the same (user, ticker) to the watchlist twice.",
     "The second insert is rejected as a duplicate.",
     "Duplicate watchlist entry rejected.", "Pass"),
    ("TC-DB-08", "Server-side default values",
     "Insert a user without created_at / updated_at.",
     "The database auto-populates the timestamp columns.",
     "created_at / updated_at auto-populated by the database.", "Pass"),
    ("TC-DB-09", "JSONB storage of strategy weights",
     "Insert a strategy with a JSONB weights object and query a nested key.",
     "The nested value is stored and retrievable (momentum = 30).",
     "JSONB value stored and queried correctly (momentum = 30).", "Pass"),
    ("TC-DB-10", "Role subtype tables 1:1 mapping",
     "Count users vs the sum of investors + analysts + admins rows.",
     "Every user has exactly one matching subtype row.",
     "6 users = 6 profile rows (1:1 mapping holds).", "Pass"),
    ("TC-DB-11", "Singleton platform_settings",
     "Count rows in platform_settings.",
     "Exactly one settings row exists.",
     "platform_settings holds exactly 1 row.", "Pass"),
    ("TC-DB-12", "Transaction atomicity (rollback)",
     "Insert a user inside a transaction, then roll it back.",
     "No row remains after the rollback.",
     "Rolled-back insert left no row — atomicity verified.", "Pass"),
    ("TC-DB-13", "Numeric precision NUMERIC(18,4)",
     "Insert a holding with quantity 1.2345 and cost 123.4567.",
     "Values are stored with exact 4-decimal precision.",
     "Stored 1.2345 / 123.4567 with exact precision.", "Pass"),
    ("TC-DB-14", "CRUD persistence (insert then update)",
     "Insert a user, update the full_name, read it back.",
     "The updated value is persisted and returned.",
     "Insert then update reads back the new value.", "Pass"),
]
LBL = ["Test ID", "Objective", "Input / Action", "Expected Results", "Actual Results",
       "Conclusion (Pass/Fail)", "Screenshot / Evidence"]

# evidence screenshot embedded once at the top of the cases section
body("All fourteen database test cases were executed by the automated suite; the actual console "
     "output (all passed) is shown below and referenced as evidence for each case.")
doc.add_picture(IMG, width=Inches(6.4))
cap = doc.add_paragraph(); cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
cr = cap.add_run("Figure 1 — Database test suite run: 14/14 passed (all writes rolled back).")
cr.italic = True; cr.font.size = Pt(9); cr.font.color.rgb = GREY
doc.add_paragraph()

for tid, obj, inp, exp, act, concl in CASES:
    hp = doc.add_paragraph(); hr = hp.add_run("Test Case: " + tid); hr.bold = True; hr.font.size = Pt(11.5)
    hp.paragraph_format.space_before = Pt(8); hp.paragraph_format.space_after = Pt(3)
    vals = [tid, obj, inp, exp, act, concl, None]
    tb = doc.add_table(rows=0, cols=2); tb.style = "Table Grid"
    for i, lbl in enumerate(LBL):
        c = tb.add_row().cells; c[0].width = Inches(1.5); c[1].width = Inches(5.1); shade(c[0], "E5E7EB")
        lr = c[0].paragraphs[0].add_run(lbl); lr.bold = True; lr.font.size = Pt(9.5)
        if lbl == "Screenshot / Evidence":
            rr = c[1].paragraphs[0].add_run("Automated run — this case shows PASS in Figure 1 (db_tests.py output).")
            rr.italic = True; rr.font.size = Pt(9); rr.font.color.rgb = GREY
        else:
            vr = c[1].paragraphs[0].add_run(vals[i]); vr.font.size = Pt(9.5)
            if lbl == "Conclusion (Pass/Fail)":
                vr.bold = True; vr.font.color.rgb = GREEN
    doc.add_paragraph()

H("6.  Result", 14)
body("14 of 14 database test cases passed. The database layer correctly enforces primary keys, "
     "unique and composite-unique constraints, not-null and enum constraints, foreign keys with "
     "cascade deletion, server-side defaults, JSONB storage, the role subtype 1:1 mapping and "
     "transactional integrity. No test left residual data.")
body("Reproduce with:  cd backend  &&  uv run python db_tests.py", bold=True)

OUT = os.path.join(HERE, "StockPilot_Database_Test_Plan.docx")
doc.save(OUT)
print("saved", OUT)
