# Axle Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build Axle — a vehicle mechanic agent with a structured Postgres knowledge base, CLI, and MCP server, replacing the old RAG-based 4runner-hunter system.

**Architecture:** Core Python library with Postgres-backed structured data (specs, procedures, manual sections, diagrams). Sonnet 4.5 agent with 7 generic tools reasons over the data. Thin CLI (typer) and MCP server wrappers expose the core. Initial manual ingestion done by Opus via Claude Code; future ingestion automated via Sonnet API.

**Tech Stack:** Python 3.12+, uv, Postgres, SQLAlchemy, Alembic, Typer, Anthropic SDK, MCP SDK, pymupdf, Docker Compose

**Design Doc:** `docs/plans/2026-02-15-axle-design.md`

**Repo:** git@github.com:dj0le/axle.git

---

## Task 1: Repository Setup & Project Scaffolding

**Files:**
- Create: `pyproject.toml`
- Create: `src/axle/__init__.py`
- Create: `src/axle/core/__init__.py`
- Create: `src/axle/db/__init__.py`
- Create: `src/axle/ingestion/__init__.py`
- Create: `src/axle/cli/__init__.py`
- Create: `src/axle/mcp/__init__.py`
- Create: `tests/__init__.py`
- Create: `tests/conftest.py`
- Create: `.gitignore`
- Create: `.env.example`
- Create: `CLAUDE.md`
- Move: `docs/plans/2026-02-15-axle-design.md` (from 4runner-hunter)
- Move: `docs/plans/2026-02-15-axle-implementation-plan.md` (this file)

**Step 1: Clone the empty repo and set up project structure**

```bash
cd ~/dev/personal
git clone git@github.com:dj0le/axle.git
cd axle
```

**Step 2: Create `pyproject.toml`**

```toml
[project]
name = "axle"
version = "0.1.0"
description = "Vehicle mechanic agent — structured knowledge base + LLM reasoning"
requires-python = ">=3.12"
dependencies = [
    "anthropic>=0.42.0",
    "sqlalchemy>=2.0",
    "psycopg[binary]>=3.2",
    "alembic>=1.14",
    "pymupdf>=1.25",
    "typer>=0.15",
    "mcp>=1.0",
    "rich>=13.0",
    "python-dotenv>=1.0",
]

[project.scripts]
axle = "axle.cli.app:app"
axle-mcp = "axle.mcp.server:main"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/axle"]

[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["src"]

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "pytest-asyncio>=0.24",
]
```

**Step 3: Create directory structure**

```bash
mkdir -p src/axle/{core,db,ingestion,cli,mcp}
mkdir -p tests
mkdir -p docs/plans
mkdir -p manuals
mkdir -p alembic/versions
```

Create `__init__.py` files for each package. `src/axle/__init__.py` should contain:

```python
"""Axle — Vehicle mechanic agent."""
__version__ = "0.1.0"
```

All other `__init__.py` files are empty.

**Step 4: Create `.gitignore`**

```gitignore
# Python
__pycache__/
*.py[cod]
*.egg-info/
dist/
build/
.venv/

# Environment
.env

# Manuals (user-provided PDFs, too large for git)
manuals/*.pdf
manuals/images/

# Database
*.db

# IDE
.idea/
.vscode/
*.swp

# OS
.DS_Store

# uv
uv.lock
```

**Step 5: Create `.env.example`**

```bash
# Anthropic API key (for Sonnet 4.5 agent queries and future ingestion)
ANTHROPIC_API_KEY=sk-ant-...

# Postgres connection
DATABASE_URL=postgresql://axle:axle@localhost:5432/axle

# Default vehicle (optional — can also be set via `axle vehicle` command)
VEHICLE_YEAR=1989
VEHICLE_MAKE=Toyota
VEHICLE_MODEL=4Runner
VEHICLE_ENGINE=3VZ-E
VEHICLE_TRANSMISSION=5-speed manual
VEHICLE_DRIVE_TYPE=4x4
```

**Step 6: Create `CLAUDE.md`**

```markdown
# CLAUDE.md

## Project Overview

Axle is a vehicle mechanic agent. It pre-processes PDF service manuals into a structured Postgres knowledge base (specs, procedures, manual sections, diagrams), then uses a Claude Sonnet 4.5 agent with tool-use to reason over that data.

## Architecture

Core Python library (`src/axle/`) with thin wrappers:
- CLI: `src/axle/cli/app.py` (typer) — `axle ask`, `axle ingest`, `axle specs`, etc.
- MCP Server: `src/axle/mcp/server.py` — exposes tools for Claude Code
- All clients call the same core functions in `src/axle/core/`

## Key Commands

```bash
# Install dependencies
uv sync

# Start Postgres
docker compose up -d postgres

# Run DB migrations
uv run alembic upgrade head

# Run CLI
uv run axle ask "what's the oil capacity for 3VZ-E?"
uv run axle ingest --status
uv run axle specs --component engine_oil

# Run tests
uv run pytest

# Run MCP server
uv run axle-mcp
```

## Database

Postgres with these tables: manuals, manual_sections, specs, procedures, diagrams, vehicles.
Full schema in `src/axle/db/models.py`. Migrations managed by Alembic in `alembic/`.

## Agent Tools (7)

1. lookup_spec — direct SQL query on specs table
2. list_specs — browse specs with filters
3. get_vehicle_config — current vehicle setup
4. search_procedures — full-text search on procedures
5. search_knowledge — full-text search across manual_sections
6. get_manual_section — retrieve specific section by ID
7. get_diagrams — retrieve diagrams by procedure/component/type

Defined in `src/axle/core/tools.py`, backed by queries in `src/axle/db/queries.py`.

## Design Doc

Full design: `docs/plans/2026-02-15-axle-design.md`
```

**Step 7: Create `tests/conftest.py`**

```python
"""Shared test fixtures."""

import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

# Use test database
os.environ.setdefault("DATABASE_URL", "postgresql://axle:axle@localhost:5432/axle_test")


@pytest.fixture
def db_url():
    return os.environ["DATABASE_URL"]
```

**Step 8: Copy docs from 4runner-hunter and run uv sync**

```bash
cp ~/dev/personal/4runner-hunter/docs/plans/2026-02-15-axle-design.md docs/plans/
cp ~/dev/personal/4runner-hunter/docs/plans/2026-02-15-axle-implementation-plan.md docs/plans/
uv sync
```

**Step 9: Commit**

```bash
git add .
git commit -m "feat: initial project scaffolding with pyproject.toml and directory structure"
```

---

## Task 2: Docker Compose + Postgres

**Files:**
- Create: `docker-compose.yml`
- Create: `.dockerignore`

**Step 1: Create `docker-compose.yml`**

```yaml
services:
  postgres:
    image: postgres:17
    environment:
      POSTGRES_USER: axle
      POSTGRES_PASSWORD: axle
      POSTGRES_DB: axle
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-ONLY", "pg_isready", "-U", "axle"]
      interval: 5s
      timeout: 5s
      retries: 5

volumes:
  pgdata:
```

**Step 2: Create `.dockerignore`**

```
.git
.venv
__pycache__
manuals/*.pdf
manuals/images/
*.db
.env
```

**Step 3: Start Postgres and verify connection**

```bash
docker compose up -d postgres
docker compose exec postgres pg_isready -U axle
```

Expected: `postgres:5432 - accepting connections`

**Step 4: Commit**

```bash
git add docker-compose.yml .dockerignore
git commit -m "feat: add Docker Compose with Postgres 17"
```

---

## Task 3: Database Models (SQLAlchemy)

**Files:**
- Create: `src/axle/db/models.py`
- Create: `src/axle/db/connection.py`
- Test: `tests/test_models.py`

**Step 1: Write the test**

```python
"""Test database models can be created and basic operations work."""

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

from axle.db.models import Base, Manual, Spec, Procedure, ManualSection, Diagram, Vehicle


@pytest.fixture
def engine(db_url):
    engine = create_engine(db_url)
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)


@pytest.fixture
def session(engine):
    with Session(engine) as session:
        yield session


def test_create_manual(session):
    manual = Manual(
        title="Factory Service Manual 1991 Toyota 4Runner",
        filename="Factory Service Manual 1991 Toyota 4 Runner - Jake.pdf",
        manual_type="fsm",
        year_start=1991,
        year_end=1991,
        engines=["3VZ-E"],
        authority_level=1,
    )
    session.add(manual)
    session.commit()

    result = session.query(Manual).first()
    assert result.title == "Factory Service Manual 1991 Toyota 4Runner"
    assert result.engines == ["3VZ-E"]
    assert result.authority_level == 1


def test_create_spec_linked_to_manual(session):
    manual = Manual(
        title="FSM 1991",
        filename="fsm_1991.pdf",
        manual_type="fsm",
        year_start=1991,
        year_end=1991,
        authority_level=1,
    )
    session.add(manual)
    session.flush()

    spec = Spec(
        manual_id=manual.id,
        category="fluids",
        component="engine_oil",
        property="capacity",
        value="4.5",
        unit="quarts",
        condition="with filter change",
        engine="3VZ-E",
    )
    session.add(spec)
    session.commit()

    result = session.query(Spec).first()
    assert result.value == "4.5"
    assert result.manual.title == "FSM 1991"


def test_create_vehicle(session):
    vehicle = Vehicle(
        name="Jake",
        year=1989,
        make="Toyota",
        model="4Runner",
        generation="1st (N60)",
        engine="3VZ-E",
        transmission="5-speed manual",
        drive_type="4x4",
        is_default=True,
    )
    session.add(vehicle)
    session.commit()

    result = session.query(Vehicle).filter_by(is_default=True).first()
    assert result.name == "Jake"
    assert result.engine == "3VZ-E"
```

**Step 2: Run test to verify it fails**

```bash
uv run pytest tests/test_models.py -v
```

Expected: FAIL — `ModuleNotFoundError: No module named 'axle.db.models'`

**Step 3: Create `src/axle/db/connection.py`**

```python
"""Database connection management."""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

_engine = None
_SessionFactory = None


def get_database_url() -> str:
    url = os.environ.get("DATABASE_URL", "postgresql://axle:axle@localhost:5432/axle")
    return url


def get_engine():
    global _engine
    if _engine is None:
        _engine = create_engine(get_database_url())
    return _engine


def get_session() -> Session:
    global _SessionFactory
    if _SessionFactory is None:
        _SessionFactory = sessionmaker(bind=get_engine())
    return _SessionFactory()
```

**Step 4: Create `src/axle/db/models.py`**

```python
"""SQLAlchemy models for the Axle knowledge base."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Manual(Base):
    __tablename__ = "manuals"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    filename: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    manual_type: Mapped[str] = mapped_column(String(50), nullable=False)
    year_start: Mapped[int | None] = mapped_column(Integer)
    year_end: Mapped[int | None] = mapped_column(Integer)
    engines: Mapped[list[str] | None] = mapped_column(ARRAY(Text))
    authority_level: Mapped[int] = mapped_column(Integer, default=3)
    authority_notes: Mapped[str | None] = mapped_column(Text)
    ingested_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    page_count: Mapped[int | None] = mapped_column(Integer)

    sections: Mapped[list["ManualSection"]] = relationship(back_populates="manual", cascade="all, delete-orphan")
    specs: Mapped[list["Spec"]] = relationship(back_populates="manual", cascade="all, delete-orphan")
    procedures: Mapped[list["Procedure"]] = relationship(back_populates="manual", cascade="all, delete-orphan")
    diagrams: Mapped[list["Diagram"]] = relationship(back_populates="manual", cascade="all, delete-orphan")


class ManualSection(Base):
    __tablename__ = "manual_sections"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    manual_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("manuals.id"), nullable=False)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    section_path: Mapped[str | None] = mapped_column(Text)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    page_start: Mapped[int | None] = mapped_column(Integer)
    page_end: Mapped[int | None] = mapped_column(Integer)
    section_type: Mapped[str | None] = mapped_column(String(50))
    metadata_: Mapped[dict | None] = mapped_column("metadata", JSONB)

    manual: Mapped["Manual"] = relationship(back_populates="sections")
    specs: Mapped[list["Spec"]] = relationship(back_populates="section")
    procedures: Mapped[list["Procedure"]] = relationship(back_populates="section")
    diagrams: Mapped[list["Diagram"]] = relationship(back_populates="section")


class Spec(Base):
    __tablename__ = "specs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    manual_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("manuals.id"), nullable=False)
    section_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("manual_sections.id"))
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    component: Mapped[str] = mapped_column(Text, nullable=False)
    property: Mapped[str] = mapped_column(Text, nullable=False)
    value: Mapped[str] = mapped_column(Text, nullable=False)
    unit: Mapped[str | None] = mapped_column(String(50))
    condition: Mapped[str | None] = mapped_column(Text)
    engine: Mapped[str | None] = mapped_column(String(50))
    year_start: Mapped[int | None] = mapped_column(Integer)
    year_end: Mapped[int | None] = mapped_column(Integer)
    notes: Mapped[str | None] = mapped_column(Text)

    manual: Mapped["Manual"] = relationship(back_populates="specs")
    section: Mapped["ManualSection | None"] = relationship(back_populates="specs")


class Procedure(Base):
    __tablename__ = "procedures"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    manual_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("manuals.id"), nullable=False)
    section_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("manual_sections.id"))
    title: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str | None] = mapped_column(String(50))
    engine: Mapped[str | None] = mapped_column(String(50))
    year_start: Mapped[int | None] = mapped_column(Integer)
    year_end: Mapped[int | None] = mapped_column(Integer)
    difficulty: Mapped[str | None] = mapped_column(String(20))
    estimated_time: Mapped[str | None] = mapped_column(Text)
    tools_needed: Mapped[list[str] | None] = mapped_column(ARRAY(Text))
    steps: Mapped[dict | None] = mapped_column(JSONB)
    warnings: Mapped[list[str] | None] = mapped_column(ARRAY(Text))

    manual: Mapped["Manual"] = relationship(back_populates="procedures")
    section: Mapped["ManualSection | None"] = relationship(back_populates="procedures")
    diagrams: Mapped[list["Diagram"]] = relationship(back_populates="procedure")


class Diagram(Base):
    __tablename__ = "diagrams"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    manual_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("manuals.id"), nullable=False)
    section_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("manual_sections.id"))
    procedure_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("procedures.id"))
    page_number: Mapped[int | None] = mapped_column(Integer)
    image_path: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    diagram_type: Mapped[str | None] = mapped_column(String(50))
    components: Mapped[list[str] | None] = mapped_column(ARRAY(Text))
    metadata_: Mapped[dict | None] = mapped_column("metadata", JSONB)

    manual: Mapped["Manual"] = relationship(back_populates="diagrams")
    section: Mapped["ManualSection | None"] = relationship(back_populates="diagrams")
    procedure: Mapped["Procedure | None"] = relationship(back_populates="diagrams")


class Vehicle(Base):
    __tablename__ = "vehicles"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str | None] = mapped_column(Text)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    make: Mapped[str] = mapped_column(String(100), nullable=False)
    model: Mapped[str] = mapped_column(String(100), nullable=False)
    generation: Mapped[str | None] = mapped_column(String(50))
    engine: Mapped[str | None] = mapped_column(String(50))
    transmission: Mapped[str | None] = mapped_column(String(100))
    drive_type: Mapped[str | None] = mapped_column(String(50))
    vin: Mapped[str | None] = mapped_column(String(17))
    notes: Mapped[str | None] = mapped_column(Text)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)
```

**Step 5: Run tests**

```bash
uv run pytest tests/test_models.py -v
```

Expected: PASS (all 3 tests)

**Step 6: Commit**

```bash
git add src/axle/db/ tests/test_models.py
git commit -m "feat: add SQLAlchemy models for manuals, specs, procedures, diagrams, vehicles"
```

---

## Task 4: Alembic Migrations

**Files:**
- Create: `alembic.ini`
- Create: `alembic/env.py`
- Generated: `alembic/versions/001_initial_schema.py`

**Step 1: Initialize Alembic**

```bash
uv run alembic init alembic
```

**Step 2: Edit `alembic.ini`** — set `sqlalchemy.url` to empty (we load from env).

**Step 3: Edit `alembic/env.py`** — import models and use `DATABASE_URL` from env:

```python
import os
from axle.db.models import Base
# Set target_metadata = Base.metadata
# Set sqlalchemy.url from os.environ["DATABASE_URL"]
```

**Step 4: Generate initial migration**

```bash
uv run alembic revision --autogenerate -m "initial schema"
```

**Step 5: Run migration**

```bash
uv run alembic upgrade head
```

**Step 6: Verify tables exist**

```bash
docker compose exec postgres psql -U axle -c "\dt"
```

Expected: Tables listed — manuals, manual_sections, specs, procedures, diagrams, vehicles, alembic_version

**Step 7: Add full-text search index migration**

Generate a second migration that adds the tsvector column and GIN index to `manual_sections`:

```sql
ALTER TABLE manual_sections ADD COLUMN search_vector tsvector;
CREATE INDEX idx_manual_sections_search ON manual_sections USING GIN(search_vector);

CREATE OR REPLACE FUNCTION manual_sections_search_update() RETURNS trigger AS $$
BEGIN
    NEW.search_vector := to_tsvector('english', COALESCE(NEW.title, '') || ' ' || COALESCE(NEW.content, ''));
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER manual_sections_search_trigger
    BEFORE INSERT OR UPDATE ON manual_sections
    FOR EACH ROW EXECUTE FUNCTION manual_sections_search_update();
```

Also add a GIN index on `procedures` for full-text search on title + steps:

```sql
ALTER TABLE procedures ADD COLUMN search_vector tsvector;
CREATE INDEX idx_procedures_search ON procedures USING GIN(search_vector);

CREATE OR REPLACE FUNCTION procedures_search_update() RETURNS trigger AS $$
BEGIN
    NEW.search_vector := to_tsvector('english', COALESCE(NEW.title, '') || ' ' || COALESCE(NEW.steps::text, ''));
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER procedures_search_trigger
    BEFORE INSERT OR UPDATE ON procedures
    FOR EACH ROW EXECUTE FUNCTION procedures_search_update();
```

**Step 8: Run second migration**

```bash
uv run alembic upgrade head
```

**Step 9: Commit**

```bash
git add alembic/ alembic.ini
git commit -m "feat: add Alembic migrations with full-text search indexes"
```

---

## Task 5: Database Query Layer

**Files:**
- Create: `src/axle/db/queries.py`
- Test: `tests/test_queries.py`

**Step 1: Write the tests**

```python
"""Test database query functions used by agent tools."""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from axle.db.models import Base, Manual, Spec, Procedure, ManualSection, Vehicle
from axle.db.queries import (
    lookup_spec,
    list_specs,
    get_vehicle_config,
    search_procedures,
    search_knowledge,
    get_manual_section,
    get_diagrams,
)


@pytest.fixture
def engine(db_url):
    engine = create_engine(db_url)
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)


@pytest.fixture
def session(engine):
    with Session(engine) as session:
        yield session


@pytest.fixture
def seeded_db(session):
    """Seed the database with sample data for testing."""
    manual = Manual(
        title="FSM 1991",
        filename="fsm_1991.pdf",
        manual_type="fsm",
        year_start=1991,
        year_end=1991,
        engines=["3VZ-E"],
        authority_level=1,
    )
    session.add(manual)
    session.flush()

    session.add(Spec(
        manual_id=manual.id,
        category="fluids",
        component="engine_oil",
        property="capacity",
        value="4.5",
        unit="quarts",
        condition="with filter change",
        engine="3VZ-E",
    ))

    session.add(Spec(
        manual_id=manual.id,
        category="torque",
        component="head_bolts",
        property="torque_spec",
        value="58",
        unit="ft-lbs",
        engine="3VZ-E",
    ))

    section = ManualSection(
        manual_id=manual.id,
        title="Cooling System Overview",
        section_path="cooling_system/overview",
        content="The cooling system uses a 50/50 mix of coolant and water. Total capacity is 8.5 quarts.",
        page_start=100,
        page_end=105,
        section_type="overview",
    )
    session.add(section)
    session.flush()

    session.add(Vehicle(
        name="Jake",
        year=1989,
        make="Toyota",
        model="4Runner",
        engine="3VZ-E",
        transmission="5-speed manual",
        drive_type="4x4",
        is_default=True,
    ))

    session.commit()
    return session


def test_lookup_spec(seeded_db):
    result = lookup_spec(seeded_db, component="engine_oil", property="capacity")
    assert len(result) >= 1
    assert result[0]["value"] == "4.5"
    assert result[0]["unit"] == "quarts"


def test_lookup_spec_with_engine_filter(seeded_db):
    result = lookup_spec(seeded_db, component="engine_oil", property="capacity", engine="3VZ-E")
    assert len(result) >= 1
    assert result[0]["engine"] == "3VZ-E"


def test_list_specs_by_category(seeded_db):
    result = list_specs(seeded_db, category="torque")
    assert len(result) >= 1
    assert result[0]["component"] == "head_bolts"


def test_get_vehicle_config(seeded_db):
    result = get_vehicle_config(seeded_db)
    assert result["name"] == "Jake"
    assert result["engine"] == "3VZ-E"


def test_lookup_spec_not_found(seeded_db):
    result = lookup_spec(seeded_db, component="nonexistent", property="nothing")
    assert result == []
```

**Step 2: Run tests to verify they fail**

```bash
uv run pytest tests/test_queries.py -v
```

Expected: FAIL — `ModuleNotFoundError`

**Step 3: Implement `src/axle/db/queries.py`**

Implement all 7 query functions that back the agent tools:

- `lookup_spec(session, component, property, engine=None)` — direct SQL filter on specs
- `list_specs(session, category=None, component=None, engine=None)` — browsable spec listing
- `get_vehicle_config(session)` — returns default vehicle
- `search_procedures(session, query, category=None, engine=None)` — full-text search
- `search_knowledge(session, query, manual_type=None, year=None)` — full-text search on sections
- `get_manual_section(session, section_id)` — direct lookup by ID
- `get_diagrams(session, procedure_id=None, component=None, diagram_type=None)` — diagram lookup

Each function returns plain dicts (not ORM objects) so they're serializable for the agent.

**Step 4: Run tests**

```bash
uv run pytest tests/test_queries.py -v
```

Expected: PASS

**Step 5: Commit**

```bash
git add src/axle/db/queries.py tests/test_queries.py
git commit -m "feat: add database query layer for all 7 agent tools"
```

---

## Task 6: Agent Tools Layer

**Files:**
- Create: `src/axle/core/tools.py`
- Create: `src/axle/core/prompts.py`
- Test: `tests/test_tools.py`

**Step 1: Write the test**

Test that tools are properly defined with names, descriptions, and parameter schemas — and that they call the correct query functions.

```python
"""Test agent tool definitions and execution."""

from axle.core.tools import TOOLS, execute_tool


def test_all_tools_defined():
    tool_names = [t["name"] for t in TOOLS]
    assert "lookup_spec" in tool_names
    assert "list_specs" in tool_names
    assert "get_vehicle_config" in tool_names
    assert "search_procedures" in tool_names
    assert "search_knowledge" in tool_names
    assert "get_manual_section" in tool_names
    assert "get_diagrams" in tool_names


def test_tools_have_descriptions():
    for tool in TOOLS:
        assert "description" in tool
        assert len(tool["description"]) > 10


def test_tools_have_input_schema():
    for tool in TOOLS:
        assert "input_schema" in tool
        assert tool["input_schema"]["type"] == "object"
```

**Step 2: Run test to verify it fails**

```bash
uv run pytest tests/test_tools.py -v
```

**Step 3: Implement `src/axle/core/tools.py`**

Define the 7 tools as Anthropic-compatible tool schemas. Each tool has a name, description, and `input_schema`. The `execute_tool(tool_name, params, session)` function dispatches to the matching query function.

**Step 4: Implement `src/axle/core/prompts.py`**

The system prompt defining Axle's personality, authority hierarchy, and tool usage rules:

```python
SYSTEM_PROMPT = """You are Axle, a vehicle mechanic assistant. You have access to factory service manuals, engine repair manuals, electrical wiring diagrams, and aftermarket guides.

Rules:
- Always call get_vehicle_config() first to know what vehicle you're working on
- For spec questions, use lookup_spec BEFORE searching manuals
- Always cite which manual a recommendation comes from
- Include safety warnings prominently
- If you can't find something in the manuals, say so clearly — don't guess at specs or torque values
- When giving procedures, include required tools and estimated time

Manual authority for resolving conflicts:
- Torque specs, tolerances, fluid specs: Factory Service Manual wins. Always.
- Engine-specific procedures: Engine Repair Manual wins over generic FSM.
- Electrical diagnosis: Wiring Diagram manual wins.
- Plain-English explanations, tips, shortcuts: Haynes/aftermarket is often clearer.
- When values conflict: cite both, flag the discrepancy, recommend FSM value.
"""
```

**Step 5: Run tests**

```bash
uv run pytest tests/test_tools.py -v
```

Expected: PASS

**Step 6: Commit**

```bash
git add src/axle/core/tools.py src/axle/core/prompts.py tests/test_tools.py
git commit -m "feat: add agent tool definitions and system prompt"
```

---

## Task 7: Agent Engine (Sonnet Tool-Use Loop)

**Files:**
- Create: `src/axle/core/agent.py`
- Test: `tests/test_agent.py`

**Step 1: Write the test**

Test the agent loop with mocked Anthropic responses to verify it correctly dispatches tool calls and returns final text.

```python
"""Test agent tool-use loop."""

from unittest.mock import MagicMock, patch
from axle.core.agent import Agent


def test_agent_returns_text_response():
    """Agent should return text when Sonnet responds without tool calls."""
    # Mock the Anthropic client to return a simple text response
    # Verify agent.ask() returns the text


def test_agent_executes_tool_calls():
    """Agent should execute tool calls and feed results back to Sonnet."""
    # Mock Anthropic to return a tool_use response, then a text response
    # Verify the tool was called with correct params
    # Verify final text response is returned
```

**Step 2: Implement `src/axle/core/agent.py`**

The agent is a loop:

```python
class Agent:
    def __init__(self, db_session, model="claude-sonnet-4-5-20250929"):
        self.client = anthropic.Anthropic()
        self.model = model
        self.session = db_session
        self.messages = []

    def ask(self, question: str) -> str:
        self.messages.append({"role": "user", "content": question})

        while True:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                system=SYSTEM_PROMPT,
                tools=TOOLS,
                messages=self.messages,
            )

            # If response has tool_use blocks, execute them and loop
            # If response has text blocks and stop_reason="end_turn", return text
```

**Step 3: Run tests**

```bash
uv run pytest tests/test_agent.py -v
```

Expected: PASS

**Step 4: Commit**

```bash
git add src/axle/core/agent.py tests/test_agent.py
git commit -m "feat: add agent engine with Sonnet tool-use loop"
```

---

## Task 8: CLI Interface

**Files:**
- Create: `src/axle/cli/app.py`
- Test: manual testing via `uv run axle --help`

**Step 1: Implement `src/axle/cli/app.py`**

```python
"""Axle CLI — vehicle mechanic agent."""

import typer
from rich.console import Console

app = typer.Typer(name="axle", help="Vehicle mechanic agent")
console = Console()


@app.command()
def ask(question: str):
    """Ask the mechanic agent a question."""
    # Initialize DB session, create Agent, call agent.ask(question)
    # Print response with rich formatting


@app.command()
def specs(
    component: str = typer.Option(None, help="Filter by component"),
    category: str = typer.Option(None, help="Filter by category"),
    engine: str = typer.Option(None, help="Filter by engine"),
):
    """List or lookup specs from the knowledge base."""
    # Direct DB query, no LLM needed


@app.command()
def manuals():
    """List ingested manuals."""


@app.command()
def vehicle():
    """Show or set the current vehicle configuration."""


@app.command()
def ingest(
    manual: str = typer.Option(None, help="Specific PDF to ingest"),
    reparse: bool = typer.Option(False, help="Re-run LLM structuring"),
    status: bool = typer.Option(False, help="Show ingestion status"),
):
    """Ingest PDF manuals into the knowledge base."""
```

**Step 2: Verify CLI works**

```bash
uv run axle --help
uv run axle ask --help
uv run axle specs --help
```

Expected: Help text displayed for each command

**Step 3: Commit**

```bash
git add src/axle/cli/app.py
git commit -m "feat: add Typer CLI with ask, specs, manuals, vehicle, ingest commands"
```

---

## Task 9: Ingestion Pipeline — PDF Parser

**Files:**
- Create: `src/axle/ingestion/parser.py`
- Test: `tests/test_ingestion.py`

**Step 1: Write the test**

```python
"""Test PDF parsing and text extraction."""

from pathlib import Path
from axle.ingestion.parser import extract_pdf_text, extract_pdf_images


def test_extract_pdf_text_returns_pages(tmp_path):
    """Test that PDF text extraction returns page-structured text."""
    # Create a simple test PDF with pymupdf
    # Verify extract_pdf_text returns list of {page: int, text: str}


def test_extract_pdf_images(tmp_path):
    """Test that PDF image extraction saves images to disk."""
    # Verify extract_pdf_images saves image files and returns metadata
```

**Step 2: Implement `src/axle/ingestion/parser.py`**

```python
"""PDF text and image extraction using pymupdf."""

import fitz  # pymupdf
from pathlib import Path


def extract_pdf_text(pdf_path: Path) -> list[dict]:
    """Extract text from each page of a PDF.

    Returns list of {page: int, text: str} dicts.
    """


def extract_pdf_images(pdf_path: Path, output_dir: Path) -> list[dict]:
    """Extract images from a PDF and save to output_dir.

    Returns list of {page: int, image_path: str, width: int, height: int} dicts.
    """
```

**Step 3: Run tests**

```bash
uv run pytest tests/test_ingestion.py -v
```

**Step 4: Commit**

```bash
git add src/axle/ingestion/parser.py tests/test_ingestion.py
git commit -m "feat: add PDF text and image extraction with pymupdf"
```

---

## Task 10: Ingestion Pipeline — LLM Structurer

**Files:**
- Create: `src/axle/ingestion/structurer.py`
- Test: `tests/test_structurer.py`

**Step 1: Write the test**

Test with mocked Anthropic responses that structurer correctly parses LLM output into specs, procedures, and sections.

**Step 2: Implement `src/axle/ingestion/structurer.py`**

Takes raw page text from parser, sends to Sonnet (or Opus) with extraction prompts, returns structured JSON:

```python
def structure_manual_content(pages: list[dict], model: str = "claude-sonnet-4-5-20250929") -> dict:
    """Send raw manual text to LLM for structured extraction.

    Returns {
        "specs": [...],
        "procedures": [...],
        "sections": [...],
    }
    """
```

Prompt instructs the LLM to extract specs with exact values, procedures with numbered steps, and section boundaries. Emphasizes: do not round, do not paraphrase torque specs.

**Step 3: Run tests and commit**

```bash
uv run pytest tests/test_structurer.py -v
git add src/axle/ingestion/structurer.py tests/test_structurer.py
git commit -m "feat: add LLM-based manual content structurer"
```

---

## Task 11: Ingestion Pipeline — Database Loader

**Files:**
- Create: `src/axle/ingestion/loader.py`
- Test: `tests/test_loader.py`

**Step 1: Write the test**

Test that loader takes structurer output and correctly inserts records into all tables.

**Step 2: Implement `src/axle/ingestion/loader.py`**

```python
def load_manual(session, filename: str, structured_data: dict, images: list[dict]) -> Manual:
    """Load structured manual data into the database.

    Creates Manual record, then inserts sections, specs, procedures, diagrams.
    """
```

**Step 3: Run tests and commit**

```bash
uv run pytest tests/test_loader.py -v
git add src/axle/ingestion/loader.py tests/test_loader.py
git commit -m "feat: add database loader for ingested manual data"
```

---

## Task 12: Wire Ingestion into CLI

**Files:**
- Modify: `src/axle/cli/app.py` (the `ingest` command)

**Step 1: Wire `axle ingest` to call parser → structurer → loader**

The `ingest` command should:
1. Find PDFs in `manuals/` directory
2. For each PDF: parse text + images, structure via LLM, load into DB
3. Show progress with `rich` progress bars
4. Report results: how many specs, procedures, sections extracted per manual

**Step 2: Test manually**

```bash
# Copy a test PDF to manuals/
uv run axle ingest --status
uv run axle ingest --manual "test.pdf"
```

**Step 3: Commit**

```bash
git add src/axle/cli/app.py
git commit -m "feat: wire ingestion pipeline into CLI ingest command"
```

---

## Task 13: MCP Server

**Files:**
- Create: `src/axle/mcp/server.py`
- Test: manual testing via Claude Code MCP config

**Step 1: Implement MCP server**

Uses the `mcp` SDK to expose the 7 tools as MCP tools. Each tool calls the same query functions as the CLI agent.

```python
"""Axle MCP server — exposes mechanic tools for Claude Code."""

from mcp.server import Server
from mcp.server.stdio import stdio_server

server = Server("axle")

@server.tool()
async def lookup_spec(component: str, property: str, engine: str | None = None) -> str:
    """Look up a specific vehicle specification."""
    # Call db query, format result as text


# ... define all 7 tools ...


async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream)
```

**Step 2: Add MCP config entry**

Add to Claude Code's `~/.config/claude/config.json`:

```json
{
  "mcpServers": {
    "axle": {
      "command": "uv",
      "args": ["--directory", "/home/djole/dev/personal/axle", "run", "axle-mcp"]
    }
  }
}
```

**Step 3: Test in Claude Code**

Start a new Claude Code session and verify the axle tools appear. Test `lookup_spec` with sample data.

**Step 4: Commit**

```bash
git add src/axle/mcp/server.py
git commit -m "feat: add MCP server exposing all 7 mechanic tools"
```

---

## Task 14: Initial Manual Ingestion (Opus via Claude Code)

**No code to write.** This is a data population task done interactively.

**Step 1: Copy manuals from 4runner-hunter**

```bash
cp ~/dev/personal/4runner-hunter/manuals/*.pdf ~/dev/personal/axle/manuals/
```

**Step 2: Start Postgres and run migrations**

```bash
cd ~/dev/personal/axle
docker compose up -d postgres
uv run alembic upgrade head
```

**Step 3: Ingest manuals using Opus (Claude Code session)**

In a Claude Code session in the axle repo, interactively:
- Read each PDF using the Read tool (pages at a time)
- Extract specs, procedures, sections, diagram descriptions
- Write directly to the database via the loader

This uses Opus on the Max plan — zero API cost, best extraction quality.

**Step 4: Verify ingestion**

```bash
uv run axle ingest --status
uv run axle manuals
uv run axle specs
```

**Step 5: Commit any seed data or ingestion scripts used**

```bash
git commit -m "feat: complete initial manual ingestion (17 manuals)"
```

---

## Task 15: End-to-End Testing

**Files:**
- Create: `tests/test_e2e.py`

**Step 1: Write end-to-end tests**

```python
"""End-to-end tests with real database and mocked LLM."""


def test_ask_spec_question_no_llm_needed(seeded_db):
    """Spec lookups should return data without calling the LLM."""


def test_ask_diagnostic_question_uses_tools(seeded_db):
    """Complex questions should trigger tool calls."""


def test_cli_ask_returns_response():
    """CLI `axle ask` should produce output."""
```

**Step 2: Run full test suite**

```bash
uv run pytest -v
```

**Step 3: Commit**

```bash
git add tests/test_e2e.py
git commit -m "test: add end-to-end tests for spec lookups and diagnostic queries"
```

---

## Summary

| Task | What it builds | Depends on |
|------|---------------|------------|
| 1 | Repo scaffolding, pyproject.toml, CLAUDE.md | — |
| 2 | Docker Compose + Postgres | — |
| 3 | SQLAlchemy models | 1 |
| 4 | Alembic migrations + full-text search | 2, 3 |
| 5 | Query layer (7 functions) | 3 |
| 6 | Tool definitions + system prompt | 5 |
| 7 | Agent engine (Sonnet loop) | 6 |
| 8 | CLI interface | 7 |
| 9 | PDF parser (pymupdf) | 1 |
| 10 | LLM structurer | 9 |
| 11 | Database loader | 5, 10 |
| 12 | Wire ingestion into CLI | 8, 11 |
| 13 | MCP server | 6 |
| 14 | Initial manual ingestion (Opus) | 12 |
| 15 | End-to-end tests | 8, 14 |

**Parallelizable:** Tasks 1+2 can run in parallel. Tasks 9-11 (ingestion) can be built in parallel with Tasks 6-8 (agent+CLI). Task 13 (MCP) can be built in parallel with Task 8 (CLI) since both depend on Task 6.
