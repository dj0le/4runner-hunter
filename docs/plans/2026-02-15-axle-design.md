# Axle — Vehicle Mechanic Agent

**Date:** 2026-02-15
**Status:** Approved design, pending implementation
**Repo:** git@github.com:dj0le/axle.git

## Summary

Axle is a vehicle mechanic assistant that replaces the old RAG-based manual search with a modern agent architecture. Instead of embedding chunks and doing similarity search, Axle pre-processes PDF service manuals into a structured Postgres knowledge base, then uses a Sonnet 4.5 agent with tool-use to reason over that data.

The system is exposed as a CLI tool (`axle ask "..."`), an MCP server (for Claude Code), and later as a web dashboard and voice interface.

## Why Not RAG

The old approach (ChromaDB + embeddings + similarity search) had fundamental problems:

- Arbitrary chunking destroyed context — a procedure split across chunks lost coherence
- Similarity search often missed relevant content with unusual phrasing
- No reasoning across multiple manuals — couldn't synthesize FSM + Haynes information
- Every query required an LLM call, even simple spec lookups
- No structured data extraction — torque values were buried in prose

Axle fixes all of these by separating data (structured DB) from reasoning (LLM agent).

## Architecture

```
                    +-- CLI (typer)
                    |-- MCP Server (for Claude Code)
Postgres <-- Core <-+-- Web Dashboard (future)
                    +-- Gemini Live Voice (future)
```

- **Core library** (`axle`) is the only thing that touches the DB or calls the LLM
- Clients are thin wrappers — CLI parses args, MCP exposes tools, web serves HTTP
- All clients get identical behavior because they call the same core functions

### One-time ingestion pipeline (separate from query path):

```
PDFs --> Extract (pymupdf) --> Structure (Opus/Sonnet) --> Load (Postgres)
```

## Database Schema (Postgres)

### manuals

| Column | Type | Description |
|--------|------|-------------|
| id | uuid, pk | |
| title | text | "Factory Service Manual 1991 Toyota 4Runner" |
| filename | text | Original PDF filename |
| manual_type | enum | fsm, engine_repair, electrical, haynes, component, maintenance |
| year_start | int | Coverage range start |
| year_end | int | Coverage range end |
| engines | text[] | Engines this manual covers |
| authority_level | int | 1=factory/OEM, 2=engine-specific, 3=aftermarket |
| authority_notes | text | "Authoritative for all 1991 specs and procedures" |
| ingested_at | timestamp | |
| page_count | int | |

### manual_sections

| Column | Type | Description |
|--------|------|-------------|
| id | uuid, pk | |
| manual_id | fk -> manuals | |
| title | text | "Chapter 12: Cooling System" |
| section_path | text | "cooling_system/thermostat_replacement" |
| content | text | Full text of the section |
| page_start | int | |
| page_end | int | |
| section_type | enum | procedure, specification, diagram_ref, troubleshooting, overview |
| search_vector | tsvector | Postgres full-text search index |
| metadata | jsonb | {engines: [...], components: [...], tools_needed: [...]} |

### specs

| Column | Type | Description |
|--------|------|-------------|
| id | uuid, pk | |
| manual_id | fk -> manuals | |
| section_id | fk -> manual_sections, nullable | |
| category | text | "fluids", "torque", "electrical", "dimensions", "timing" |
| component | text | "engine_oil", "head_bolts", "spark_plugs" |
| property | text | "capacity", "torque_spec", "gap" |
| value | text | "4.5" |
| unit | text | "quarts", "ft-lbs", "mm" |
| condition | text, nullable | "with filter change" |
| engine | text, nullable | "3VZ-E" |
| year_range | int4range | [1989, 1995] |
| notes | text, nullable | "recheck after 50 miles" |

### procedures

| Column | Type | Description |
|--------|------|-------------|
| id | uuid, pk | |
| manual_id | fk -> manuals | |
| section_id | fk -> manual_sections | |
| title | text | "Timing Belt Replacement" |
| category | text | "engine", "drivetrain", "electrical", "body", "suspension" |
| engine | text, nullable | "3VZ-E" |
| year_range | int4range | |
| difficulty | enum | beginner, intermediate, advanced |
| estimated_time | text | "2-3 hours" |
| tools_needed | text[] | |
| steps | jsonb | [{step: 1, text: "...", warning: "...", torque: "..."}] |
| warnings | text[] | Critical safety notes |
| related_specs | uuid[] | Spec IDs referenced by this procedure |

### diagrams

| Column | Type | Description |
|--------|------|-------------|
| id | uuid, pk | |
| manual_id | fk -> manuals | |
| section_id | fk -> manual_sections, nullable | |
| procedure_id | fk -> procedures, nullable | |
| page_number | int | |
| image_path | text | "manuals/images/{manual_id}/p145_01.png" |
| description | text | AI-generated description of the diagram |
| diagram_type | enum | wiring, exploded_view, torque_sequence, routing, flowchart, location, table |
| components | text[] | What components are shown |
| metadata | jsonb | {orientation, references_steps: [3,4,5]} |

### vehicles

| Column | Type | Description |
|--------|------|-------------|
| id | uuid, pk | |
| name | text | "Jake" (nickname) |
| year | int | 1989 |
| make | text | "Toyota" |
| model | text | "4Runner" |
| generation | text | "1st (N60)" |
| engine | text | "3VZ-E" |
| transmission | text | "5-speed manual" |
| drive_type | text | "4x4" |
| vin | text, nullable | |
| notes | text | Freeform notes |
| is_default | boolean | Which vehicle to use when not specified |

## Agent Tools (6 + 1)

### Structured lookups (no LLM reasoning needed)

1. **lookup_spec(component, property, engine?)** — Direct SQL query on specs table. Returns value, unit, condition, source.
2. **list_specs(category?, component?, engine?)** — Browse available specs with optional filters.
3. **get_vehicle_config()** — Returns current vehicle specs. Agent calls this first.

### Text retrieval (feeds context to LLM reasoning)

4. **search_procedures(query, category?, engine?)** — Full-text search on procedures. Returns title, steps, tools, warnings.
5. **search_knowledge(query, manual_type?, year?)** — Full-text search across manual_sections. The catch-all.
6. **get_manual_section(manual_id, section_path)** — Retrieve a specific known section.

### Diagram retrieval

7. **get_diagrams(procedure_id?, component?, diagram_type?)** — Returns matching diagrams with descriptions and file paths.

## Multi-Source Synthesis

When multiple manuals cover the same topic, the agent receives ALL matching results tagged with source and authority level. The agent (not a scoring algorithm) decides how to combine them.

### Authority hierarchy (encoded in system prompt)

- Torque specs, tolerances, fluid specs: Factory Service Manual wins. Always.
- Engine-specific procedures: Engine Repair Manual wins over generic FSM.
- Electrical diagnosis: Wiring Diagram manual wins.
- Plain-English explanations, tips, shortcuts: Haynes is often clearer.
- When values conflict: cite both, flag the discrepancy, recommend FSM value.

## Ingestion Pipeline

### Initial ingestion: Opus 4.6 via Claude Code (Max plan)

- Read each PDF using Claude Code's Read tool (pages at a time, including images)
- Opus extracts structured data with highest accuracy
- Zero API cost — runs on Max plan
- One-time effort for the foundational knowledge base

### Future ingestion: `axle ingest` command via Sonnet 4.5 API

- Automated pipeline for adding new manuals later
- pymupdf extracts raw text + images
- Sonnet structures the extracted content into JSON
- Loader inserts into Postgres
- Estimated cost: $1-3 per manual

### Image extraction during ingestion

- pymupdf extracts images from each page
- Stored as files: `manuals/images/{manual_id}/{page}_{index}.png`
- Opus/Sonnet generates description, diagram type, component tags
- Linked to procedures and sections via the diagrams table
- Poor quality extractions flagged during ingestion

## LLM Configuration

- **Default model:** Claude Sonnet 4.5 via Anthropic API (on Vertex AI / Google Cloud)
- **Ingestion model:** Opus 4.6 for initial parse (via Claude Code), Sonnet for future updates
- **Cost per query:** ~$0.05-0.10 for diagnostic reasoning, $0 for structured lookups
- **No model routing complexity** — Sonnet handles everything at query time

## Project Structure

```
axle/
├── pyproject.toml              # Package config, CLI entrypoint, dependencies
├── docker-compose.yml          # Postgres + app containers
├── Dockerfile
│
├── src/
│   └── axle/                   # Core Python package
│       ├── __init__.py
│       │
│       ├── core/
│       │   ├── agent.py        # Agent engine — Sonnet tool-use loop
│       │   ├── tools.py        # Tool definitions (7 tools)
│       │   └── prompts.py      # System prompt, authority rules
│       │
│       ├── db/
│       │   ├── models.py       # SQLAlchemy models
│       │   ├── connection.py   # Postgres connection / session management
│       │   └── queries.py      # Query functions the tools call
│       │
│       ├── ingestion/
│       │   ├── parser.py       # PDF text + image extraction (pymupdf)
│       │   ├── structurer.py   # Extracts specs/procedures from raw text
│       │   └── loader.py       # Loads parsed data into Postgres
│       │
│       ├── cli/
│       │   └── app.py          # Typer CLI
│       │
│       └── mcp/
│           └── server.py       # MCP server for Claude Code
│
├── manuals/                    # PDF source files (gitignored)
├── docs/plans/
├── tests/
│   ├── test_tools.py
│   ├── test_queries.py
│   ├── test_ingestion.py
│   └── conftest.py
│
└── alembic/                    # DB migrations
    ├── alembic.ini
    └── versions/
```

## CLI Commands

```bash
axle ask "question"              # Ask the mechanic agent
axle ingest                      # Ingest all PDFs in manuals/
axle ingest --manual "X.pdf"     # Ingest one specific manual
axle ingest --reparse            # Re-run LLM structuring
axle ingest --status             # Show what's ingested
axle specs                       # List all extracted specs
axle specs --component X         # Lookup specific spec
axle manuals                     # List ingested manuals
axle vehicle                     # Show/set current vehicle config
```

## Dependencies

```
anthropic          # Claude API (Sonnet 4.5)
sqlalchemy         # ORM + query builder
psycopg[binary]    # Postgres driver (async)
alembic            # DB migrations
pymupdf            # PDF + image extraction
typer              # CLI framework
mcp                # MCP SDK
```

## Installation

```bash
# Local dev
uv sync

# Install CLI globally
uv tool install .

# Run MCP server
uv run axle-mcp

# Docker (Postgres + app)
docker compose up
```

## Diagram Presentation by Interface

| Interface | How diagrams are presented |
|-----------|--------------------------|
| CLI | Prints description + file path, optionally opens with xdg-open |
| MCP / Claude Code | Returns image path — Claude can read it directly |
| Web Dashboard (future) | Rendered inline with procedure steps |
| Gemini Voice (future) | Agent describes the diagram verbally |

## Future Interfaces (not in scope for v1, but compatible)

- **Web Dashboard** — FastAPI serving the same core library, procedure checklists with inline diagrams
- **Gemini Live Voice** — voice-based interaction for hands-free garage use
- **Multi-vehicle support** — vehicles table already supports this

## Migration from 4runner-hunter

- New repo: git@github.com:dj0le/axle.git
- Old repo (4runner-hunter) stays as-is — learning artifact
- Manuals (PDFs) are copied to the new repo's manuals/ directory
- No code is carried over — clean start
