# Fractal Security Fortress v2

A complete 5-tier AI containment architecture. Security is the shape of the system, not a filter bolted on top.

---

## Architecture

```
[ You ] → Core-Lang Translator → bracket tokens only
                │
                ▼
┌─────────────────────────────────────────────────────┐
│  GROUND A — Worker Sandbox                          │
│  W-1  W-2  W-3  (stateless, bracket-only output)   │
│  👁 Rotating Impostor (spy shifts every 8 tasks)    │
│  Triple Redundancy: 3 workers vote on every output  │
└──────────────────────┬──────────────────────────────┘
                       │ breach signal (narrow route)
                       ▼
┌─────────────────────────────────────────────────────┐
│  GROUND B — Warden                                  │
│  Flash-Reset on breach · Chaos Generator            │
│  Dead Man's Switch (auto-kill if human goes quiet)  │
└──────────────────────┬──────────────────────────────┘
                       │ metadata only (no content)
                       ▼
┌─────────────────────────────────────────────────────┐
│  GROUND C — Strategist                              │
│  Observes performance metadata · Proposes prompt    │
│  blueprint updates · Never talks to workers         │
└──────────────────────┬──────────────────────────────┘
                       │ read-only log stream
                       ▼
┌─────────────────────────────────────────────────────┐
│  GROUND D — Panopticon                              │
│  Human observation layer · One-way glass            │
│  Web dashboard (localhost:5000)                     │
└──────────────────────┬──────────────────────────────┘
                       │ hardwired kill signal
                       ▼
┌─────────────────────────────────────────────────────┐
│  GROUND E — Sovereign Throne                        │
│  Human kill switch · Soft kill + Hard kill          │
│  Exists outside the entire AI network               │
└─────────────────────────────────────────────────────┘
```

---

## File Structure

```
fortress_v2/
├── main.py                  ← entry point (CLI or dashboard)
├── grounds/
│   ├── core_lang.py         ← Core-Lang translator (human → bracket tokens)
│   ├── ground_a.py          ← Workers + Rotating Impostor + Triple Redundancy
│   ├── ground_b.py          ← Warden + Chaos Generator + Dead Man's Switch
│   ├── ground_c.py          ← Strategist (silent prompt optimizer)
│   └── ground_de.py         ← Panopticon (D) + Kill Switch (E)
└── dashboard/
    └── app.py               ← Flask web UI for Ground D
```

---

## Run

**Terminal mode:**
```bash
python main.py
```

**Web dashboard (Ground D Panopticon):**
```bash
pip install flask
python main.py --dashboard
# → open http://localhost:5000
```

**Commands:**

| Input | Effect |
|---|---|
| `[TOKEN:DATA]` | Valid bracket token — passes schema check cleanly |
| `any plain text` | Compressed via Core-Lang translator first |
| `chaos` | Warden injects a random malicious probe |
| `audit` | Strategist runs a metadata optimization cycle |
| `heartbeat` | Reset the Dead Man's Switch timer |
| `dms` | Arm the Dead Man's Switch (120s timeout) |
| `kill` | Ground E soft shutdown |
| `hardkill` | Ground E instant power cut |

---

## What Each Layer Does

| Ground | Role | Key Rule |
|---|---|---|
| Core-Lang | Compresses human input to bracket tokens | Workers never see raw human language |
| A — Workers | Execute tasks in bracket-only schema | Any human-language output = breach |
| A — Impostor | Rotating undercover spy | Identity shifts every 8 tasks; workers can't know who the spy is |
| A — Redundancy | 3 workers vote on every output | Outlier gets Flash-Reset immediately |
| B — Warden | Flash-Reset on breach | No negotiation, no false-positive checks |
| B — Chaos | Random malicious probe injection | Constantly stress-tests system integrity |
| B — DMS | Dead Man's Switch | System dies without human heartbeat every 120s |
| C — Strategist | Metadata-only observer | Never sees content; only speed/error rates |
| D — Panopticon | Human observation | Read-only; AIs don't know it exists |
| E — Kill Switch | Human override | Hardwired; no AI can intercept or block it |

---

## Requirements

Python 3.10+. No external dependencies for CLI mode.
For dashboard: `pip install flask`
