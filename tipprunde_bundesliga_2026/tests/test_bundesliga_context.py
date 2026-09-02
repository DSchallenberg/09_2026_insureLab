from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RUNTIME_FILES = (
    ".claude/agents/bundesliga-tipp-agent.md",
    ".claude/skills/aufstellung/SKILL.md",
    ".claude/skills/quoten/SKILL.md",
    ".claude/skills/tipp/SKILL.md",
)
FORBIDDEN_TERMS = (
    "W" + "M-2026",
    "Welt" + "meisterschaft",
    "FIFA " + "Match Centre",
)
DOCUMENTATION_FILES = (
    "docs/superpowers/specs/2026-07-07-bundesliga-tipp-agent-design.md",
    "docs/superpowers/plans/2026-07-07-bundesliga-tipp-agent.md",
    "docs/superpowers/2026-07-07-probelauf.md",
)


def test_runtime_context_is_bundesliga_specific():
    contents = {
        relative_path: (PROJECT_ROOT / relative_path).read_text(encoding="utf-8")
        for relative_path in RUNTIME_FILES
    }

    assert "name: bundesliga-tipp-agent" in contents[
        ".claude/agents/bundesliga-tipp-agent.md"
    ]
    assert "jeweils aktuellen Bundesliga-Saison" in contents[
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


def test_user_facing_documentation_describes_bundesliga():
    for relative_path in DOCUMENTATION_FILES:
        content = (PROJECT_ROOT / relative_path).read_text(encoding="utf-8")
        assert "Bundesliga" in content
        assert "FIFA " + "Match Centre" not in content
        assert "W" + "M-2026" not in content
