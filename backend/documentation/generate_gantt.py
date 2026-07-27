"""Generate a ProjectLibre-compatible .pod (MS Project XML) Gantt chart for StockPilot.

Structured as genuine Agile Scrum with:
- Fixed 2-week sprint cadence
- Vertical slices per sprint (design + build + test in EVERY sprint)
- User-story-oriented task names
- Full Scrum ceremonies (Planning, Daily Standups, Review, Retrospective)
- Product Backlog items pulled into each sprint
"""
import xml.etree.ElementTree as ET
from xml.dom import minidom
from datetime import datetime, timedelta
import os

OUT = os.path.join(os.path.dirname(__file__), "StockPilot_Gantt_Chart.pod")

# ── Resources ──
RESOURCES = [
    {"id": 1, "name": "Pasindu Heshan",         "initials": "PH", "role": "Project Manager & AI/ML Engineer (CL/HDCSE/CMU/131/41) - VS Code, Jupyter, numpy, pandas, ta, Transformers, XGBoost"},
    {"id": 2, "name": "Methmina Senadeera",     "initials": "MS", "role": "Backend Developer & System Architect (CL/HDCSE/CMU/131/13) - VS Code, Python, FastAPI, Postman, Draw.io"},
    {"id": 3, "name": "Senali Santhushya",      "initials": "SS", "role": "Frontend Developer & System Analyst (CL/HDCSE/CMU/131/15) - React, Chart.js, Node.js, VS Code"},
    {"id": 4, "name": "Sachin Eranga Fernando", "initials": "SF", "role": "QA Engineer & Database Designer (CL/HDCSE/CMU/131/37) - PostgreSQL, Draw.io, Postman"},
    {"id": 5, "name": "Anne Sheree Fernando",   "initials": "AF", "role": "UI/UX Designer & Frontend Engineer (CL/HDCSE/CMU/131/77) - Figma, Canva, VS Code"},
]

# Short-name lookup used in task assignments below
R = {"Pasindu": 1, "Methmina": 2, "Senali": 3, "Sachin": 4, "Sheree": 5}
ALL = [R["Pasindu"], R["Methmina"], R["Senali"], R["Sheree"], R["Sachin"]]

def d(s):
    return datetime.strptime(s, "%Y-%m-%d")

def fmt(dt):
    return dt.strftime("%Y-%m-%dT08:00:00")

def fmt_end(dt):
    return dt.strftime("%Y-%m-%dT17:00:00")

uid_counter = [0]
def uid():
    uid_counter[0] += 1
    return uid_counter[0]

TASKS = []

def add_summary(name, start, finish, level=1):
    u = uid()
    TASKS.append({"uid": u, "name": name, "start": start, "finish": finish,
                  "milestone": False, "resources": [], "summary": True,
                  "outline_level": level, "predecessors": [], "duration_days": None, "notes": ""})
    return u

def add_task(name, start, finish, resources, level=2, predecessors=None, milestone=False, notes=""):
    u = uid()
    delta = (d(finish) - d(start)).days
    if delta == 0:
        duration = 1
    else:
        bdays = 0
        cur = d(start)
        end = d(finish)
        while cur <= end:
            if cur.weekday() < 5:
                bdays += 1
            cur += timedelta(days=1)
        duration = max(bdays, 1)
    TASKS.append({"uid": u, "name": name, "start": start, "finish": finish,
                  "milestone": milestone, "resources": resources,
                  "summary": False, "outline_level": level,
                  "predecessors": predecessors or [], "duration_days": duration, "notes": notes})
    return u

# ════════════════════════════════════════════════════════════════
# PRODUCT BACKLOG INITIALIZATION & SPRINT 0 (Pre-Sprint)
# Jun 30 - Jul 13 | 2 weeks | Goal: Proposal approved
# ════════════════════════════════════════════════════════════════
add_summary("Sprint 0: Project Inception & Proposal (Jun 30 - Jul 13)", "2026-06-30", "2026-07-13")

# Ceremonies
add_summary("Scrum Ceremonies", "2026-06-30", "2026-07-13", level=2)
t1 = add_task("Product Backlog Creation & Initial Prioritization", "2026-06-30", "2026-06-30",
              ALL, level=3, notes="Define all user stories, epics, acceptance criteria. Prioritize by MoSCoW.")
t2 = add_task("Sprint 0 Planning Meeting", "2026-06-30", "2026-06-30",
              ALL, level=3, predecessors=[t1], notes="Select backlog items for Sprint 0. Define sprint goal: approved proposal.")
t_standup_0 = add_task("Daily Standups (async Slack check-ins)", "2026-07-01", "2026-07-13",
                       ALL, level=3, predecessors=[t2], notes="15-min daily sync: what I did, what I'll do, blockers.")

# Vertical Slice: Requirements + Initial Prototyping + Validation
add_summary("Sprint Backlog Items", "2026-06-30", "2026-07-13", level=2)

# Design slice
t3 = add_task("US-001: Define problem statement & project scope", "2026-07-01", "2026-07-03",
              [R["Senali"], R["Pasindu"]], level=3, predecessors=[t2],
              notes="As a stakeholder, I need a clear problem definition so the project scope is bounded.")
t4 = add_task("US-002: Research similar systems & technology stack", "2026-07-01", "2026-07-04",
              [R["Pasindu"], R["Methmina"]], level=3, predecessors=[t2],
              notes="As a developer, I need a literature review of existing tools so I can justify our tech choices.")

# Build slice (early prototyping alongside proposal writing)
t5 = add_task("US-003: Create system architecture diagram & tech stack selection", "2026-07-03", "2026-07-07",
              [R["Pasindu"], R["Methmina"]], level=3, predecessors=[t4],
              notes="As a developer, I need an architecture blueprint so the team can start parallel work.")
t6 = add_task("US-004: Design low-fidelity wireframes for core screens", "2026-07-03", "2026-07-07",
              [R["Sheree"]], level=3, predecessors=[t2],
              notes="As a user, I can see proposed UI layouts so I understand the system vision.")

# Test/Validation slice
t7 = add_task("US-005: Define initial QA strategy & acceptance criteria", "2026-07-03", "2026-07-07",
              [R["Sachin"]], level=3, predecessors=[t2],
              notes="As a QA, I need testing approach defined early so I can validate from Sprint 1.")
t8 = add_task("US-006: Compile and format proposal document", "2026-07-04", "2026-07-07",
              [R["Senali"]], level=3, predecessors=[t3, t4],
              notes="As a team, we need a formatted proposal combining all research and designs.")

# Milestones
t9 = add_task("MILESTONE: Proposal Submission", "2026-07-08", "2026-07-08",
              ALL, level=3, milestone=True, predecessors=[t5, t6, t7, t8])
t10 = add_task("Prepare and rehearse proposal presentation", "2026-07-09", "2026-07-10",
               ALL, level=3, predecessors=[t9])
t11 = add_task("MILESTONE: Proposal Presentation", "2026-07-13", "2026-07-13",
               ALL, level=3, milestone=True, predecessors=[t10])

# Ceremonies close
add_summary("Sprint 0 Closure", "2026-07-13", "2026-07-13", level=2)
t_review_0 = add_task("Sprint 0 Review (demo proposal to supervisor)", "2026-07-13", "2026-07-13",
                       ALL, level=3, predecessors=[t11])
t_retro_0 = add_task("Sprint 0 Retrospective", "2026-07-13", "2026-07-13",
                      ALL, level=3, predecessors=[t_review_0],
                      notes="What went well, what to improve, action items for Sprint 1.")

# ════════════════════════════════════════════════════════════════
# SPRINT 1 (Jul 14 - Jul 27) | 2 weeks
# Goal: Deliver Ch 1-2 + working DB prototype + testable wireframes
# Vertical slice: Documentation + Database + UI + QA
# ════════════════════════════════════════════════════════════════
add_summary("Sprint 1: Foundation & Core Design (Jul 14 - Jul 27)", "2026-07-14", "2026-07-27")

add_summary("Scrum Ceremonies", "2026-07-14", "2026-07-27", level=2)
t_plan_1 = add_task("Sprint 1 Planning Meeting", "2026-07-14", "2026-07-14",
                     ALL, level=3, predecessors=[t_retro_0],
                     notes="Sprint goal: Ch 1-2 complete + working DB schema + validated wireframes. Pull stories from backlog.")
t_standup_1 = add_task("Daily Standups", "2026-07-14", "2026-07-27",
                        ALL, level=3, predecessors=[t_plan_1])

add_summary("Sprint Backlog Items", "2026-07-14", "2026-07-25", level=2)

# DOCUMENTATION slice (runs in parallel with build)
t12 = add_task("US-007: Write Chapter 1 - Introduction & Problem Statement", "2026-07-14", "2026-07-17",
               [R["Senali"]], level=3, predecessors=[t_plan_1],
               notes="Introduction, problem statement, literature review, proposed solution, functionalities.")
t13 = add_task("US-008: Write Chapter 2 - Feasibility Study & WBS", "2026-07-14", "2026-07-22",
               [R["Pasindu"]], level=3, predecessors=[t_plan_1],
               notes="Feasibility report, requirement gathering, resource identification, WBS, risk analysis.")

# BUILD slice (prototyping alongside documentation)
t14 = add_task("US-009: Design ER diagram & draft database schema", "2026-07-14", "2026-07-18",
               [R["Sachin"], R["Methmina"]], level=3, predecessors=[t_plan_1],
               notes="As a developer, I need a database design so backend development can start in Sprint 2. Sachin leads DB design; Methmina aligns it with the system architecture.")
t15 = add_task("US-010: Set up PostgreSQL + SQLAlchemy models (prototype)", "2026-07-18", "2026-07-22",
               [R["Methmina"]], level=3, predecessors=[t14],
               notes="As a developer, I can run the DB locally so we validate the schema early.")
t16 = add_task("US-011: Create interactive UI wireframes for all 7 views", "2026-07-14", "2026-07-22",
               [R["Sheree"]], level=3, predecessors=[t_plan_1],
               notes="As a user, I can click through wireframes so the team validates navigation flow.")
t17 = add_task("US-012: Set up React project + implement Auth screen prototype", "2026-07-21", "2026-07-24",
               [R["Senali"]], level=3, predecessors=[t12],
               notes="As a user, I can see a login page so we validate the tech stack works end-to-end.")

# TEST slice (validation runs alongside build)
t18 = add_task("US-013: Write test strategy & initial test plan", "2026-07-14", "2026-07-22",
               [R["Sachin"]], level=3, predecessors=[t_plan_1],
               notes="As a QA, I define test methodology and begin writing test cases for Auth & DB.")
t19 = add_task("US-014: Validate wireframes with acceptance criteria", "2026-07-22", "2026-07-24",
               [R["Sachin"], R["Sheree"]], level=3, predecessors=[t16, t18],
               notes="As a QA, I review wireframes against user stories to catch design gaps early.")

# Sprint closure
add_summary("Sprint 1 Closure", "2026-07-24", "2026-07-27", level=2)
t_review_1 = add_task("Sprint 1 Review (demo: DB prototype + wireframes + Ch 1-2)", "2026-07-24", "2026-07-24",
                       ALL, level=3, predecessors=[t13, t15, t17, t19])
t_retro_1 = add_task("Sprint 1 Retrospective", "2026-07-24", "2026-07-24",
                      ALL, level=3, predecessors=[t_review_1])
t_ms1 = add_task("MILESTONE: Milestone Meeting 1 - Ch 1 & 2 + DB Demo", "2026-07-27", "2026-07-27",
                 ALL, level=3, milestone=True, predecessors=[t_retro_1],
                 notes="Present chapters 1-2, working database, wireframes to supervisor.")

# ════════════════════════════════════════════════════════════════
# SPRINT 2 (Jul 28 - Aug 10) | 2 weeks
# Goal: Deliver Ch 3-4 + working backend APIs + frontend skeleton + test cases
# Vertical slice: Design docs + Backend + Frontend + QA
# ════════════════════════════════════════════════════════════════
add_summary("Sprint 2: Detailed Design & Backend MVP (Jul 28 - Aug 10)", "2026-07-28", "2026-08-10")

add_summary("Scrum Ceremonies", "2026-07-28", "2026-08-10", level=2)
t_plan_2 = add_task("Sprint 2 Planning Meeting", "2026-07-28", "2026-07-28",
                     ALL, level=3, predecessors=[t_ms1],
                     notes="Sprint goal: Ch 3-4 + CRUD APIs working + frontend connected to backend.")
t_standup_2 = add_task("Daily Standups", "2026-07-28", "2026-08-10",
                        ALL, level=3, predecessors=[t_plan_2])

add_summary("Sprint Backlog Items", "2026-07-28", "2026-08-07", level=2)

# DOCUMENTATION slice
t20 = add_task("US-015: Write Chapter 3 - Methodology (Agile Scrum) & Technology", "2026-07-28", "2026-07-31",
               [R["Methmina"]], level=3, predecessors=[t_plan_2],
               notes="Document Scrum framework, sprint structure, tech stack justification.")
t21 = add_task("US-016: Write Chapter 4 - System Design (ER, UML, DFD)", "2026-07-28", "2026-08-04",
               [R["Senali"]], level=3, predecessors=[t_plan_2],
               notes="Normalized relational schema, use case/class/sequence diagrams, DFDs.")

# BUILD slice (backend + frontend in parallel)
t22 = add_task("US-017: Finalize ER diagram, normalization & relational schema", "2026-07-28", "2026-08-01",
               [R["Sachin"]], level=3, predecessors=[t_plan_2],
               notes="As a developer, I need the final DB schema so all teams build against one source of truth. Database Designer finalizes 3NF normalization in Draw.io.")
t23 = add_task("US-018: Implement Auth API (login, register, JWT refresh)", "2026-08-01", "2026-08-05",
               [R["Methmina"]], level=3, predecessors=[t22],
               notes="As a user, I can register/login so I have authenticated access to the system.")
t24 = add_task("US-019: Implement Portfolio & Watchlist CRUD endpoints", "2026-08-04", "2026-08-07",
               [R["Methmina"]], level=3, predecessors=[t22],
               notes="As a user, I can add/remove holdings and watchlist stocks via API.")
t25 = add_task("US-020: Write pseudocode for AI scoring algorithm", "2026-07-28", "2026-08-04",
               [R["Pasindu"]], level=3, predecessors=[t_plan_2],
               notes="As a developer, I document the 6-factor scoring engine logic before implementation.")
t26 = add_task("US-021: Build yfinance data pipeline & technical indicator calculator", "2026-08-04", "2026-08-07",
               [R["Pasindu"]], level=3, predecessors=[t25],
               notes="As a system, I can fetch live stock data and compute RSI, MACD, moving averages.")
t27 = add_task("US-022: Build Dashboard & Advisor UI (connected to backend)", "2026-07-28", "2026-08-05",
               [R["Senali"]], level=3, predecessors=[t_plan_2],
               notes="As a user, I can view my dashboard with live data from the backend API.")
t28 = add_task("US-023: Create high-fidelity UI mockups & design system", "2026-07-28", "2026-08-05",
               [R["Sheree"]], level=3, predecessors=[t_plan_2],
               notes="As a user, I see a polished dark-themed UI. CSS variables, component library.")
t29 = add_task("US-024: Draw UML diagrams (use case, class, sequence)", "2026-08-04", "2026-08-07",
               [R["Senali"]], level=3, predecessors=[t21],
               notes="As a reader, I can see system interactions through standardized UML diagrams. System Analyst models system behaviour from Ch 4 requirements.")

# TEST slice
t30 = add_task("US-025: Write test cases for Auth & Portfolio APIs", "2026-07-28", "2026-08-05",
               [R["Sachin"]], level=3, predecessors=[t_plan_2],
               notes="As a QA, I validate API endpoints return correct data and handle edge cases.")
t31 = add_task("US-026: Execute API smoke tests on Auth & Portfolio", "2026-08-05", "2026-08-07",
               [R["Sachin"]], level=3, predecessors=[t23, t30],
               notes="As a QA, I run initial tests against working APIs to catch defects early.")

# Sprint closure
add_summary("Sprint 2 Closure", "2026-08-07", "2026-08-10", level=2)
t_review_2 = add_task("Sprint 2 Review (demo: working login + portfolio + API)", "2026-08-07", "2026-08-07",
                       ALL, level=3, predecessors=[t21, t24, t26, t27, t29, t31])
t_retro_2 = add_task("Sprint 2 Retrospective", "2026-08-07", "2026-08-07",
                      ALL, level=3, predecessors=[t_review_2])
t_ms2 = add_task("MILESTONE: Milestone Meeting 2 - Ch 3 & 4 + Working APIs", "2026-08-10", "2026-08-10",
                 ALL, level=3, milestone=True, predecessors=[t_retro_2],
                 notes="Present Ch 3-4, ER/UML diagrams, working auth + portfolio APIs, connected frontend.")

# ════════════════════════════════════════════════════════════════
# SPRINT 3 (Aug 11 - Aug 25) | 2 weeks
# Goal: System 70% complete + Ch 5-6 started + integration tested
# Vertical slice: AI/ML + remaining APIs + full frontend + testing
# ════════════════════════════════════════════════════════════════
add_summary("Sprint 3: Core Feature Build & 70% System (Aug 11 - Aug 25)", "2026-08-11", "2026-08-25")

add_summary("Scrum Ceremonies", "2026-08-11", "2026-08-25", level=2)
t_plan_3 = add_task("Sprint 3 Planning Meeting", "2026-08-11", "2026-08-11",
                     ALL, level=3, predecessors=[t_ms2],
                     notes="Sprint goal: 70% system working end-to-end. AI predictions, all major views, tested.")
t_standup_3 = add_task("Daily Standups", "2026-08-11", "2026-08-25",
                        ALL, level=3, predecessors=[t_plan_3])

add_summary("Sprint Backlog Items", "2026-08-11", "2026-08-22", level=2)

# BUILD slice - Backend
t32 = add_task("US-027: Implement Trade Journal CRUD API", "2026-08-11", "2026-08-14",
               [R["Methmina"]], level=3, predecessors=[t_plan_3],
               notes="As a user, I can log, view, and delete my past trades in the journal.")
t33 = add_task("US-028: Implement Marketplace & Strategy APIs", "2026-08-14", "2026-08-19",
               [R["Methmina"]], level=3, predecessors=[t32],
               notes="As an analyst, I can publish strategies. As a user, I can browse marketplace listings.")
t34 = add_task("US-029: Implement Notification system API", "2026-08-19", "2026-08-21",
               [R["Methmina"]], level=3, predecessors=[t33],
               notes="As a user, I receive in-app notifications for verdicts, alerts, and system events.")

# BUILD slice - AI/ML
t35 = add_task("US-030: Train XGBoost model & generate predictions", "2026-08-11", "2026-08-17",
               [R["Pasindu"]], level=3, predecessors=[t_plan_3],
               notes="As a user, I get AI-generated BUY/HOLD/SELL predictions with confidence scores.")
t36 = add_task("US-031: Integrate FinBERT sentiment analysis", "2026-08-18", "2026-08-22",
               [R["Pasindu"]], level=3, predecessors=[t35],
               notes="As a user, I see news sentiment scores powered by NLP alongside stock predictions.")
t37x = add_task("US-032: Build 6-factor composite scoring engine", "2026-08-18", "2026-08-22",
               [R["Pasindu"], R["Methmina"]], level=3, predecessors=[t35],
               notes="As a user, I see a composite score combining sentiment, momentum, valuation, volatility, volume, growth.")

# BUILD slice - Frontend
t38x = add_task("US-033: Build Portfolio, Journal & Settings views", "2026-08-11", "2026-08-19",
               [R["Senali"]], level=3, predecessors=[t_plan_3],
               notes="As a user, I can manage my portfolio, review my trade journal, and edit settings.")
t39x = add_task("US-034: Build Marketplace & Advisor integration views", "2026-08-19", "2026-08-22",
               [R["Senali"]], level=3, predecessors=[t38x],
               notes="As a user, I can browse strategies and see full AI verdicts in the Advisor.")

# BUILD slice - UI/UX
t40 = add_task("US-035: Implement design system & responsive styling", "2026-08-11", "2026-08-14",
               [R["Sheree"]], level=3, predecessors=[t_plan_3],
               notes="As a user, the app looks polished on desktop and mobile with the dark luxury theme.")
t41 = add_task("US-036: Review & refine all implemented UI screens", "2026-08-18", "2026-08-22",
               [R["Sheree"]], level=3, predecessors=[t40],
               notes="As a user, the final UI matches the design system with no visual regressions.")

# DOCUMENTATION slice (written alongside build, not after)
t42 = add_task("US-037: Begin Chapter 5 - Implementation with screenshots", "2026-08-18", "2026-08-22",
               [R["Senali"]], level=3, predecessors=[t38x],
               notes="As a reader, I see each functionality documented with evidence/screenshots.")
t43 = add_task("US-038: Begin Chapter 6 - Testing methodology & test plan", "2026-08-18", "2026-08-22",
               [R["Sachin"]], level=3, predecessors=[t_plan_3],
               notes="As a reader, I understand the testing approach and see structured test plans.")

# TEST slice (testing the build as it happens)
t44 = add_task("US-039: Write & execute test cases for Journal & Marketplace", "2026-08-14", "2026-08-21",
               [R["Sachin"]], level=3, predecessors=[t_plan_3],
               notes="As a QA, I validate new API endpoints as they become available.")
t45x = add_task("US-040: Integration test - Frontend to Backend data flow", "2026-08-21", "2026-08-22",
               [R["Sachin"], R["Senali"]], level=3, predecessors=[t34, t39x, t44],
               notes="As a QA, I verify end-to-end user journeys work across the full stack.")

# Sprint closure
add_summary("Sprint 3 Closure", "2026-08-22", "2026-08-25", level=2)
t_review_3 = add_task("Sprint 3 Review (demo: 70% system end-to-end)", "2026-08-22", "2026-08-22",
                       ALL, level=3, predecessors=[t36, t37x, t39x, t41, t42, t43, t45x])
t_retro_3 = add_task("Sprint 3 Retrospective", "2026-08-22", "2026-08-22",
                      ALL, level=3, predecessors=[t_review_3])
t_ms3 = add_task("MILESTONE: Milestone Meeting 3 - System 70% Demo", "2026-08-25", "2026-08-25",
                 ALL, level=3, milestone=True, predecessors=[t_retro_3],
                 notes="Demo 70% working system: AI predictions, portfolio, journal, marketplace, advisor.")

# ════════════════════════════════════════════════════════════════
# SPRINT 4 (Aug 26 - Sep 8) | 2 weeks
# Goal: 100% feature complete + fully tested + documentation done
# Vertical slice: Remaining features + full testing + chapters finalized
# ════════════════════════════════════════════════════════════════
add_summary("Sprint 4: Feature Completion & System Testing (Aug 26 - Sep 8)", "2026-08-26", "2026-09-08")

add_summary("Scrum Ceremonies", "2026-08-26", "2026-09-08", level=2)
t_plan_4 = add_task("Sprint 4 Planning Meeting", "2026-08-26", "2026-08-26",
                     ALL, level=3, predecessors=[t_ms3],
                     notes="Sprint goal: 100% features, all chapters done, UAT passed.")
t_standup_4 = add_task("Daily Standups", "2026-08-26", "2026-09-08",
                        ALL, level=3, predecessors=[t_plan_4])

add_summary("Sprint Backlog Items", "2026-08-26", "2026-09-05", level=2)

# BUILD slice - remaining features
t46 = add_task("US-041: Implement Admin dashboard with CRUD operations", "2026-08-26", "2026-09-01",
               [R["Methmina"], R["Senali"]], level=3, predecessors=[t_plan_4],
               notes="As an admin, I can approve/reject strategies, manage users, view revenue stats.")
t47 = add_task("US-042: Implement backtesting module & strategy validation", "2026-08-26", "2026-09-01",
               [R["Pasindu"]], level=3, predecessors=[t_plan_4],
               notes="As an analyst, I can validate strategy performance against backtest thresholds.")
t48 = add_task("US-043: Frontend-Backend full integration & API polish", "2026-09-01", "2026-09-03",
               [R["Methmina"], R["Senali"]], level=3, predecessors=[t46],
               notes="As a user, all frontend views are connected to real backend APIs with error handling.")

# DOCUMENTATION slice (finalize alongside testing)
t49 = add_task("US-044: Finalize Chapter 5 - All functionalities with evidence", "2026-08-26", "2026-09-02",
               [R["Senali"]], level=3, predecessors=[t_plan_4],
               notes="As a reader, every system feature is documented with screenshots and explanation.")
t50 = add_task("US-045: Finalize Chapter 6 - Test cases, results & conclusion", "2026-08-26", "2026-09-02",
               [R["Sachin"]], level=3, predecessors=[t_plan_4],
               notes="As a reader, test results with pass/fail are documented with conclusion.")
t51 = add_task("US-046: Write User Manual", "2026-09-01", "2026-09-03",
               [R["Sheree"]], level=3, predecessors=[t_plan_4],
               notes="As a user, I have a step-by-step guide to navigate and use the system.")

# TEST slice (comprehensive)
t52 = add_task("US-047: Execute full functional test suite", "2026-08-28", "2026-09-03",
               [R["Sachin"]], level=3, predecessors=[t_plan_4],
               notes="As a QA, I run all test cases across every module and record results.")
t53 = add_task("US-048: Bug fixing & regression testing", "2026-09-03", "2026-09-05",
               [R["Pasindu"], R["Methmina"], R["Senali"]], level=3, predecessors=[t48, t52],
               notes="As a developer, I fix all P1/P2 bugs found during testing.")
t54 = add_task("US-049: User Acceptance Testing (UAT)", "2026-09-04", "2026-09-05",
               [R["Sachin"], R["Sheree"]], level=3, predecessors=[t48, t52],
               notes="As a QA, I validate the system meets all acceptance criteria from user stories.")

# UI/UX slice
t55 = add_task("US-050: Final UI polish & responsive testing", "2026-09-01", "2026-09-04",
               [R["Sheree"]], level=3, predecessors=[t48],
               notes="As a user, the app renders correctly on all screen sizes with no visual bugs.")
t56 = add_task("US-051: Capture final screenshots & update report diagrams", "2026-09-04", "2026-09-05",
               [R["Sheree"]], level=3, predecessors=[t55],
               notes="As a reader, I see current screenshots in the report, not outdated wireframes.")

# Sprint closure
add_summary("Sprint 4 Closure", "2026-09-05", "2026-09-08", level=2)
t_review_4 = add_task("Sprint 4 Review (demo: 100% system + all chapters)", "2026-09-05", "2026-09-05",
                       ALL, level=3, predecessors=[t49, t50, t53, t54, t56])
t_retro_4 = add_task("Sprint 4 Retrospective", "2026-09-08", "2026-09-08",
                      ALL, level=3, predecessors=[t_review_4])

# ════════════════════════════════════════════════════════════════
# SPRINT 5 (Sep 9 - Sep 16) | Final Sprint (shorter - delivery focused)
# Goal: Submit final document + deliver final demonstration
# ════════════════════════════════════════════════════════════════
add_summary("Sprint 5: Final Delivery (Sep 9 - Sep 16)", "2026-09-09", "2026-09-16")

add_summary("Scrum Ceremonies", "2026-09-09", "2026-09-16", level=2)
t_plan_5 = add_task("Sprint 5 Planning Meeting", "2026-09-09", "2026-09-09",
                     ALL, level=3, predecessors=[t_retro_4],
                     notes="Sprint goal: polished final document submitted + successful demo.")
t_standup_5 = add_task("Daily Standups", "2026-09-09", "2026-09-16",
                        ALL, level=3, predecessors=[t_plan_5])

add_summary("Sprint Backlog Items", "2026-09-09", "2026-09-16", level=2)

# DOCUMENTATION + DELIVERY (all hands)
t57 = add_task("US-052: Compile final report (all chapters, appendices, references)", "2026-09-09", "2026-09-10",
               [R["Senali"], R["Pasindu"]], level=3, predecessors=[t_plan_5],
               notes="As a team, we compile all chapters into one formatted document per guidelines.")
t58 = add_task("US-053: Proofread, format & quality check report", "2026-09-09", "2026-09-10",
               [R["Sachin"], R["Sheree"]], level=3, predecessors=[t_plan_5],
               notes="As a reader, the document is error-free, properly formatted, and professional.")
t59 = add_task("US-054: Prepare Gantt chart (planned vs actual) & appendices", "2026-09-09", "2026-09-10",
               [R["Methmina"]], level=3, predecessors=[t_plan_5],
               notes="As a reader, I can see planned vs actual timeline and all supporting documents.")

t60 = add_task("MILESTONE: Final Document Submission", "2026-09-11", "2026-09-11",
               ALL, level=3, milestone=True, predecessors=[t57, t58, t59])

# DEMO PREPARATION
t61 = add_task("US-055: Prepare demo script & presentation slides", "2026-09-14", "2026-09-15",
               [R["Pasindu"], R["Sheree"]], level=3, predecessors=[t60],
               notes="As a presenter, I have a structured demo flow covering all system features.")
t62 = add_task("US-056: Full demo rehearsal & environment verification", "2026-09-14", "2026-09-15",
               ALL, level=3, predecessors=[t60],
               notes="As a team, we rehearse the full demo and verify the system runs correctly.")

t63 = add_task("MILESTONE: Final Demonstration", "2026-09-16", "2026-09-16",
               ALL, level=3, milestone=True, predecessors=[t61, t62])

# Final closure
add_summary("Sprint 5 Closure", "2026-09-16", "2026-09-16", level=2)
t_review_5 = add_task("Sprint 5 Review & Project Retrospective", "2026-09-16", "2026-09-16",
                       ALL, level=3, predecessors=[t63],
                       notes="Final retrospective: lessons learned, what to include in report.")


# ━━━━━━━━━━━━━━━━━━━━ BUILD XML ━━━━━━━━━━━━━━━━━━━━

ns = "http://schemas.microsoft.com/project"
ET.register_namespace('', ns)

project = ET.Element("Project", xmlns=ns)

ET.SubElement(project, "Name").text = "StockPilot - CSE5015 Computing Project (Agile Scrum)"
ET.SubElement(project, "Title").text = "StockPilot Gantt Chart - Agile Scrum"
ET.SubElement(project, "Subject").text = "CSE5015 Computing Project - Agile Scrum Methodology"
ET.SubElement(project, "Author").text = "Group 77"
ET.SubElement(project, "CreationDate").text = "2026-07-20T00:00:00"
ET.SubElement(project, "StartDate").text = "2026-06-30T08:00:00"
ET.SubElement(project, "FinishDate").text = "2026-09-16T17:00:00"
ET.SubElement(project, "ScheduleFromStart").text = "1"
ET.SubElement(project, "CalendarUID").text = "1"
ET.SubElement(project, "MinutesPerDay").text = "480"
ET.SubElement(project, "MinutesPerWeek").text = "2400"
ET.SubElement(project, "DaysPerMonth").text = "20"

# Calendar
calendars = ET.SubElement(project, "Calendars")
cal = ET.SubElement(calendars, "Calendar")
ET.SubElement(cal, "UID").text = "1"
ET.SubElement(cal, "Name").text = "Standard"
ET.SubElement(cal, "IsBaseCalendar").text = "1"
weekdays = ET.SubElement(cal, "WeekDays")

for day_num in range(1, 8):
    wd = ET.SubElement(weekdays, "WeekDay")
    ET.SubElement(wd, "DayType").text = str(day_num)
    if day_num in (1, 7):
        ET.SubElement(wd, "DayWorking").text = "0"
    else:
        ET.SubElement(wd, "DayWorking").text = "1"
        wt = ET.SubElement(wd, "WorkingTimes")
        wt1 = ET.SubElement(wt, "WorkingTime")
        ET.SubElement(wt1, "FromTime").text = "08:00:00"
        ET.SubElement(wt1, "ToTime").text = "12:00:00"
        wt2 = ET.SubElement(wt, "WorkingTime")
        ET.SubElement(wt2, "FromTime").text = "13:00:00"
        ET.SubElement(wt2, "ToTime").text = "17:00:00"

# Resources
resources_el = ET.SubElement(project, "Resources")
for res in RESOURCES:
    r_el = ET.SubElement(resources_el, "Resource")
    ET.SubElement(r_el, "UID").text = str(res["id"])
    ET.SubElement(r_el, "ID").text = str(res["id"])
    ET.SubElement(r_el, "Name").text = res["name"]
    ET.SubElement(r_el, "Initials").text = res["initials"]
    ET.SubElement(r_el, "Group").text = "Group 77"
    ET.SubElement(r_el, "MaxUnits").text = "1.0"
    ET.SubElement(r_el, "Type").text = "1"
    ET.SubElement(r_el, "CalendarUID").text = "1"
    ET.SubElement(r_el, "Notes").text = res["role"]

# Tasks
tasks_el = ET.SubElement(project, "Tasks")
for i, task in enumerate(TASKS):
    t_el = ET.SubElement(tasks_el, "Task")
    ET.SubElement(t_el, "UID").text = str(task["uid"])
    ET.SubElement(t_el, "ID").text = str(i + 1)
    ET.SubElement(t_el, "Name").text = task["name"]
    ET.SubElement(t_el, "Start").text = fmt(d(task["start"]))
    ET.SubElement(t_el, "Finish").text = fmt_end(d(task["finish"]))
    ET.SubElement(t_el, "OutlineLevel").text = str(task["outline_level"])
    ET.SubElement(t_el, "Priority").text = "500"
    ET.SubElement(t_el, "CalendarUID").text = "-1"
    ET.SubElement(t_el, "ConstraintType").text = "0"

    if task["summary"]:
        ET.SubElement(t_el, "Summary").text = "1"
        ET.SubElement(t_el, "Type").text = "1"
    else:
        ET.SubElement(t_el, "Summary").text = "0"

    if task["milestone"]:
        ET.SubElement(t_el, "Milestone").text = "1"
        ET.SubElement(t_el, "Duration").text = "PT0H0M0S"
    elif task["duration_days"] is not None:
        hours = task["duration_days"] * 8
        ET.SubElement(t_el, "Milestone").text = "0"
        ET.SubElement(t_el, "Duration").text = f"PT{hours}H0M0S"
    else:
        ET.SubElement(t_el, "Milestone").text = "0"

    if task["notes"]:
        ET.SubElement(t_el, "Notes").text = task["notes"]

    for pred_uid in task["predecessors"]:
        pred_link = ET.SubElement(t_el, "PredecessorLink")
        ET.SubElement(pred_link, "PredecessorUID").text = str(pred_uid)
        ET.SubElement(pred_link, "Type").text = "1"
        ET.SubElement(pred_link, "CrossProject").text = "0"
        ET.SubElement(pred_link, "LinkLag").text = "0"
        ET.SubElement(pred_link, "LagFormat").text = "7"

# Assignments
assignments_el = ET.SubElement(project, "Assignments")
assign_uid = 0
for task in TASKS:
    if not task["summary"]:
        for res_id in task["resources"]:
            assign_uid += 1
            a_el = ET.SubElement(assignments_el, "Assignment")
            ET.SubElement(a_el, "UID").text = str(assign_uid)
            ET.SubElement(a_el, "TaskUID").text = str(task["uid"])
            ET.SubElement(a_el, "ResourceUID").text = str(res_id)
            ET.SubElement(a_el, "Units").text = "1.0"
            ET.SubElement(a_el, "Start").text = fmt(d(task["start"]))
            ET.SubElement(a_el, "Finish").text = fmt_end(d(task["finish"]))

# Write
xml_str = ET.tostring(project, encoding="unicode", xml_declaration=False)
pretty = minidom.parseString(xml_str).toprettyxml(indent="  ", encoding="UTF-8")

with open(OUT, "wb") as f:
    f.write(pretty)

# Also write an .xml copy for Microsoft Project (same MS Project XML schema)
OUT_XML = OUT.replace(".pod", ".xml")
with open(OUT_XML, "wb") as f:
    f.write(pretty)

print(f"Generated: {OUT}")
print(f"Generated: {OUT_XML}")
print(f"Total tasks: {len(TASKS)}")
print(f"Total resources: {len(RESOURCES)}")
print(f"Total assignments: {assign_uid}")
print(f"\nSprint structure:")
for t in TASKS:
    if t["outline_level"] == 1:
        print(f"  {t['name']}")
    elif t["milestone"]:
        print(f"    * {t['name']}")
