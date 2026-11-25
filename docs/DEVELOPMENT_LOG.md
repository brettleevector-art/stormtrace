# STORMTRACE Development Log

## Session 001 — Foundation and configuration

### Done and verified
- Created project folder and structure in WSL2.
- Created .venv and installed dependencies (import check passed).
- Created GitHub repository and pushed the first commit.
- Created config/cities.json (6 cities OK).

### Problems and fixes
None so far.

### Next session
Phase 3: build the extraction pipeline.

## Session 002 — Phases 3 to 6

- Extraction, transformation and data quality merged.
- PostgreSQL 18 installed in WSL2 (port 5432); user stormtrace_user and database stormtrace_dw created.
- Separate Windows PostgreSQL service exists on port 6767; not used by this project.
- Login test from .env passed.



## Session 003 — Power BI integration and README

Date: 2026-11-26

### Objective
Publish the Power BI report and complete the main project README.

### Work completed

- Verified the project root:
  /home/brettunix/projects/stormtrace
- Verified the current branch:
  feature/powerbi-dashboard
- Verified the GitHub remote:
  git@github.com:brettleevector-art/stormtrace.git
- Inspected commit e1d4d24.
- Confirmed the dashboard PBIX and six screenshots were included.
- Pushed feature/powerbi-dashboard to GitHub.
- Confirmed pull request #8 was merged into main.
- Identified that README.md was initially empty.
- Added the complete project README (509 lines).
- Committed README as d8d62ec.
- Successfully pushed d8d62ec to feature/powerbi-dashboard.

### Git details

Dashboard commit:
e1d4d24

Dashboard merge commit:
916dae9

README commit:
d8d62ec

Branch:
feature/powerbi-dashboard

### Problems and fixes

Problem:
README.md was present but had zero bytes.

Fix:
Added the project overview, architecture, technology stack,
data scope, pipeline, SQL analytics, Power BI pages,
setup instructions, limitations and attribution.

Problem:
PROJECT_STATUS.md still described Phase 2 as the active phase.

Fix:
Identified the stale status information. A corrected
status document is being prepared.

### Verification

Confirmed:
- README contains 509 lines.
- README commit succeeded.
- Push to origin succeeded.
- Pull request #8 is merged.

Not verified during this session:
- Latest complete pipeline execution.
- Current database row counts.
- Current six-city data coverage.
- Latest full test suite result.
- Final SQL view results.
- Final Power BI database refresh.

### Exact next action

Update PROJECT_STATUS.md, CHANGELOG.md and this development log.
Commit and push the documentation update.
Open a documentation pull request into main.