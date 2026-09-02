# Bundesliga-Tipp-Agent Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Den gesamten aktiven Tipp-Kontext von einem internationalen Turnier auf die jeweils aktuelle deutsche Bundesliga-Saison umstellen.

**Architecture:** Der öffentliche `/tipp`-Skill beschafft für ein Bundesligaspiel Aufstellungs- und Quotendaten und übergibt sie an `bundesliga-tipp-agent`. Dieser führt den bestehenden deterministischen Optimizer aus; Team A ist verbindlich das Heimteam. Der Rechenkern bleibt algorithmisch unverändert, seine Nutzertexte werden bundesligatauglich.

**Tech Stack:** Claude-Code-Projekt-Skills und Custom Agent (Markdown), Python 3 Standardbibliothek, pytest.

---

## Zielstruktur

```text
.claude/
├── agents/
│   └── bundesliga-tipp-agent.md
└── skills/
    ├── aufstellung/SKILL.md
    ├── quoten/SKILL.md
    └── tipp/SKILL.md
scripts/
└── kicktipp_optimizer.py
tests/
├── test_bundesliga_context.py
└── test_kicktipp_optimizer.py
docs/superpowers/
├── 2026-07-07-probelauf.md
├── specs/
│   └── 2026-07-07-bundesliga-tipp-agent-design.md
└── plans/
    └── 2026-07-07-bundesliga-tipp-agent.md
```

`docs/superpowers/specs/2026-09-03-bundesliga-tipp-agent-design.md` bleibt
als abgenommene Migrationsspezifikation bestehen. Das Verzeichnis des lokalen
Git-Checkouts wird nicht umbenannt, da das eine Operation außerhalb des
Repositories wäre und nicht zur Agentenfunktion gehört.

### Task 1: Laufzeit-Kontext auf Bundesliga umstellen

**Files:**
- Create: `tests/test_bundesliga_context.py`
- Rename: `.claude/agents/wm-tipp-agent.md` → `.claude/agents/bundesliga-tipp-agent.md`
- Modify: `.claude/skills/aufstellung/SKILL.md`
- Modify: `.claude/skills/quoten/SKILL.md`
- Re-create: `.claude/skills/tipp/SKILL.md`

- [ ] **Step 1: Den Regressionstest für die aktiven Anweisungen schreiben**

Create `tests/test_bundesliga_context.py`:

```python
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RUNTIME_FILES = (
    ".claude/agents/bundesliga-tipp-agent.md",
    ".claude/skills/aufstellung/SKILL.md",
    ".claude/skills/quoten/SKILL.md",
    ".claude/skills/tipp/SKILL.md",
)
FORBIDDEN_TERMS = ("WM-2026", "Weltmeisterschaft", "FIFA Match Centre")


def test_runtime_context_is_bundesliga_specific():
    contents = {
        relative_path: (PROJECT_ROOT / relative_path).read_text(encoding="utf-8")
        for relative_path in RUNTIME_FILES
    }

    assert "name: bundesliga-tipp-agent" in contents[
        ".claude/agents/bundesliga-tipp-agent.md"
    ]
    assert "jeweils aktuelle Bundesliga-Saison" in contents[
        ".claude/agents/bundesliga-tipp-agent.md"
    ]
    assert "Team A ist die Heimmannschaft" in contents[
        ".claude/agents/bundesliga-tipp-agent.md"
    ]
    assert "DFL" in contents[".claude/skills/aufstellung/SKILL.md"]
    assert "Bundesliga" in contents[".claude/skills/quoten/SKILL.md"]
    assert "Bundesliga" in contents[".claude/skills/tipp/SKILL.md"]

    for content in contents.values():
        assert not any(term in content for term in FORBIDDEN_TERMS)
```

- [ ] **Step 2: Den Regressionstest rot ausführen**

Run: `python3 -m pytest tests/test_bundesliga_context.py -v`

Expected: FAIL mit `FileNotFoundError` für
`.claude/agents/bundesliga-tipp-agent.md` und/oder `.claude/skills/tipp/SKILL.md`.

- [ ] **Step 3: Den Custom Agent in die neue Rolle überführen**

Move the existing untracked file with `mv .claude/agents/wm-tipp-agent.md
.claude/agents/bundesliga-tipp-agent.md`. Replace its frontmatter and body so
that it has `name: bundesliga-tipp-agent`, retains only `Bash` as its tool,
and states all of the following explicit contracts:

- The agent analyses exactly one match from the current Bundesliga season.
- Team A is the home team and Team B the away team.
- Its prompt must contain the match, season/round/table context, supplied
  lineup data and supplied 90-minute 1X2 odds; it must ask for missing data,
  never invent it and never research independently.
- It uses `scripts/kicktipp_optimizer.py` for every probability and expected
  points calculation, receives a clear error for unavailable odds and permits
  a model deviation only for documented lineup information.
- Its response contains recommendation, 1X2 probabilities, expected goals,
  top-five expected-points table, likely results, supplied sources/timestamps
  and a qualitative Bundesliga context (table, matchday, home/away form,
  injuries).
- It explicitly excludes extra time and penalties.

Keep the existing JSON-driven output template and the Kicktipp 4/3/2 scoring
explanation, but replace tournament wording with Bundesliga wording and remove
the hard-coded external working-directory path.

- [ ] **Step 4: Die drei Projekt-Skills vollständig auf Bundesliga-Daten umstellen**

Write the following functional requirements into the Markdown instructions:

- `aufstellung/SKILL.md`: identify home and away side; query the current
  Bundesliga season; prioritise DFL match centre and official club reports,
  then Kicker, Sportschau, ESPN or Flashscore; distinguish official from
  probable lineups; retain the existing JSON schema and add source plus
  retrieval time. Never use the retired tournament provider.
- `quoten/SKILL.md`: search `"<Heimteam>" "<Auswärtsteam>" Bundesliga
  Wettquoten 1X2 Dezimalquoten`; return only 90-minute 1X2 and Over/Under 2.5
  decimal odds, source and timestamp in the existing JSON schema; explicitly
  reject settlement markets and non-regulation-time odds.
- `tipp/SKILL.md`: recreate the public `/tipp` skill. It determines current
  season, matchday, home/away assignment and table situation, invokes
  `aufstellung` and `quoten`, then delegates with the complete collected JSON
  to `bundesliga-tipp-agent`. It must require current form, home/away form,
  injuries/suspensions and fixture congestion as sourced qualitative context.
  It analyses one match only and gives a 90-minute Kicktipp recommendation.

Each skill frontmatter must describe the current Bundesliga scope. Do not add
network access to the custom subagent.

- [ ] **Step 5: Den Laufzeit-Regressionstest grün ausführen**

Run: `python3 -m pytest tests/test_bundesliga_context.py -v`

Expected: `1 passed`.

- [ ] **Step 6: Den aktiven Kontext committen**

```bash
git add .claude/agents/bundesliga-tipp-agent.md \
  .claude/skills/aufstellung/SKILL.md \
  .claude/skills/quoten/SKILL.md \
  .claude/skills/tipp/SKILL.md \
  tests/test_bundesliga_context.py
git rm --cached .claude/agents/wm-tipp-agent.md 2>/dev/null || true
git commit -m "feat: migrate tip agent context to Bundesliga"
```

### Task 2: Optimizer-Metadaten und CLI-Regression anpassen

**Files:**
- Modify: `scripts/kicktipp_optimizer.py`
- Modify: `tests/test_kicktipp_optimizer.py`

- [ ] **Step 1: Einen fehlschlagenden CLI-Test ergänzen**

Add this test to `tests/test_kicktipp_optimizer.py`:

```python
def test_help_describes_bundesliga_context():
    proc = run_cli("--help")

    assert proc.returncode == 0
    assert "Bundesliga" in proc.stdout
    assert "WM 2026" not in proc.stdout
```

- [ ] **Step 2: Den neuen CLI-Test rot ausführen**

Run: `python3 -m pytest tests/test_kicktipp_optimizer.py::test_help_describes_bundesliga_context -v`

Expected: FAIL because the current parser description still names the retired
competition.

- [ ] **Step 3: Nur die Nutzertexte des Optimizers ändern**

In `scripts/kicktipp_optimizer.py`, change the module docstring and
`build_parser()` description from the retired competition to
`"Kicktipp-optimaler Bundesliga-Tipp aus Wettquoten."`. Leave constants,
function signatures, JSON schema and all probability calculations unchanged.

- [ ] **Step 4: Den CLI-Test und die gesamte Optimizer-Suite grün ausführen**

Run: `python3 -m pytest tests/test_kicktipp_optimizer.py -v`

Expected: all existing optimizer tests plus
`test_help_describes_bundesliga_context` pass.

- [ ] **Step 5: Die Metadatenänderung committen**

```bash
git add scripts/kicktipp_optimizer.py tests/test_kicktipp_optimizer.py
git commit -m "chore: label optimizer for Bundesliga tips"
```

### Task 3: Projektdokumentation migrieren und absichern

**Files:**
- Rename: `docs/superpowers/specs/2026-07-07-wm-tipp-agent-design.md` → `docs/superpowers/specs/2026-07-07-bundesliga-tipp-agent-design.md`
- Rename: `docs/superpowers/plans/2026-07-07-wm-tipp-agent.md` → `docs/superpowers/plans/2026-07-07-bundesliga-tipp-agent.md`
- Modify: `docs/superpowers/2026-07-07-probelauf.md`
- Modify: `docs/superpowers/specs/2026-09-03-bundesliga-tipp-agent-design.md`
- Modify: `tests/test_bundesliga_context.py`

- [ ] **Step 1: Einen fehlschlagenden Test für die fachliche Dokumentation schreiben**

Extend `tests/test_bundesliga_context.py` with:

```python
DOCUMENTATION_FILES = (
    "docs/superpowers/specs/2026-07-07-bundesliga-tipp-agent-design.md",
    "docs/superpowers/plans/2026-07-07-bundesliga-tipp-agent.md",
    "docs/superpowers/2026-07-07-probelauf.md",
)


def test_user_facing_documentation_describes_bundesliga():
    for relative_path in DOCUMENTATION_FILES:
        content = (PROJECT_ROOT / relative_path).read_text(encoding="utf-8")
        assert "Bundesliga" in content
        assert "FIFA Match Centre" not in content
        assert "WM-2026" not in content
```

- [ ] **Step 2: Den Dokumentationstest rot ausführen**

Run: `python3 -m pytest tests/test_bundesliga_context.py::test_user_facing_documentation_describes_bundesliga -v`

Expected: FAIL with `FileNotFoundError` until the documents are renamed.

- [ ] **Step 3: Spezifikation, Plan und Probelauf fachlich migrieren**

Use `git mv` for the two dated documents. Rewrite their examples, diagrams,
source strategy, agent name, command descriptions and acceptance criteria to
match Tasks 1 and 2:

- Model every fixture as home team versus away team in the current Bundesliga
  season.
- Replace neutral-venue and tournament/group/knockout assumptions with
  matchday, table position, home/away performance, fixture congestion and
  relegation/title/European-qualification context.
- Replace retired official lineup sources with DFL and official club sources.
- Keep the established 90-minute Kicktipp 4/3/2 scoring and deterministic
  optimizer explanation.
- Make the acceptance run a clearly marked Bundesliga-format example. Do not
  retain unsourced claims presented as current odds, lineups or standings.

Then revise the 2026-09-03 migration spec so it describes the Bundesliga
architecture directly rather than naming the retired competition. Retain its
approved decisions unchanged.

- [ ] **Step 4: Den Dokumentationstest grün ausführen**

Run: `python3 -m pytest tests/test_bundesliga_context.py -v`

Expected: `2 passed`.

- [ ] **Step 5: Die Dokumentationsmigration committen**

```bash
git add docs/superpowers tests/test_bundesliga_context.py
git commit -m "docs: migrate tip agent documentation to Bundesliga"
```

### Task 4: Vollständige Verifikation und Restbestände prüfen

**Files:**
- Verify only: project runtime, documentation, tests and CLI.

- [ ] **Step 1: Auf veraltete Fachbegriffe im aktiven Projektinhalt prüfen**

Run:

```bash
rg -n -i 'wm-2026|weltmeisterschaft|fifa match centre' \
  .claude scripts tests docs/superpowers \
  -g '*.md' -g '*.py' \
  -g '!docs/superpowers/plans/2026-09-03-bundesliga-tipp-agent.md'
```

Expected: no matches. Historical Git-Objekte und der Checkout-Verzeichnisname
sind nicht Teil dieser Suche.

- [ ] **Step 2: Gesamte Testsuite ausführen**

Run: `python3 -m pytest tests/ -v`

Expected: all tests pass with no errors or warnings.

- [ ] **Step 3: Den dokumentierten CLI-Aufruf prüfen**

Run: `python3 scripts/kicktipp_optimizer.py --odds 2.10 3.40 3.60 --over25 1.85`

Expected: exit code 0, valid JSON on stdout and a `recommendation` object.

- [ ] **Step 4: Den endgültigen Git-Status prüfen**

Run: `git status --short`

Expected: no unintended generated files; only deliberate uncommitted user work
outside this plan, if any, is reported.
