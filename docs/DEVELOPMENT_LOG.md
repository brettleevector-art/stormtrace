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

