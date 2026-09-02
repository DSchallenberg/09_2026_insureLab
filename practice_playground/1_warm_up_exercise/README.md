# practice_playground

Teil von **[InsureLab](https://www.adesso.de/)** — Spielwiese und Referenzprojekt für die Konfiguration von Claude Code mit dem Adesso AI Hub.

## Claude Code mit AI Hub verbinden

Folge diesen Schritten, um Claude Code für die Verwendung des lokalen Adesso AI Hubs zu konfigurieren.

### 1. Lokale Konfiguration anlegen

Kopiere die Vorlage aus `.claude/settings.local-example.json` in die aktive lokale Konfigurationsdatei:

```bash
# Mac/Linux
cp .claude/settings.local-example.json .claude/settings.local.json

# Windows
copy .claude\settings.local-example.json .claude\settings.local.json
```

Trage deinen API-Key aus dem AI Hub in `.claude/settings.local.json` ein:

```json
{
  "env": {
    "ANTHROPIC_API_KEY": "dein-ai-hub-api-key"
  }
}
```

> **Wichtig:** `.claude/settings.local.json` steht in `.gitignore` und wird nicht commited — der API-Key bleibt lokal.

### 2. Globale Konfiguration (bereits vorbereitet)

Die Datei `.claude/settings.json` enthält die Konfiguration für den AI Hub und muss normalerweise nicht angepasst werden:

```json
{
  "model": "qwen-3.6-35b-sovereign",
  "env": {
    "ANTHROPIC_BASE_URL": "https://adesso-ai-hub.3asabc.de",
    "ANTHROPIC_MODEL": "qwen-3.6-35b-sovereign",
    "ANTHROPIC_DEFAULT_HAIKU_MODEL": "claude-haiku-4-5",
    "ANTHROPIC_DEFAULT_SONNET_MODEL": "claude-sonnet-5",
    "ANTHROPIC_DEFAULT_OPUS_MODEL": "claude-opus-5"
  },
  "enabledPlugins": {
    "skill-creator@claude-plugins-official": true
  }
}
```

- **`ANTHROPIC_BASE_URL`** – Endpoint des AI Hubs
- **`ANTHROPIC_MODEL`** – Standard-Modell für Claude Code
- **`ANTHROPIC_DEFAULT_*_MODEL`** – Mapping für Haiku/Sonnet/Opus über den AI Hub

### 3. Verbindung testen

Starte Claude Code im Projektverzeichnis:

```bash
claude
```

In der Konsole sollte angezeigt werden, welches Modell verwendet wird und die Verbindung zum AI Hub steht.
