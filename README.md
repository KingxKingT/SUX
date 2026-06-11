# Fractal Security Fortress

A 5-tier security architecture for isolated AI agents. Security is baked into the design, not the code.

---

## Architecture

```
Input
  │
  ▼
Ground A — Worker agents (stateless, bracket-only output)
  │
  ▼
Ground A* — Impostor node (real-time linguistic pattern match)
  │  breach signal
  ▼
Ground B — Warden (Flash-Reset offending worker to zero)
  │
  ▼
Ground D — Panopticon (human-readable audit log + stats)
  │
  ▼
Ground E — Kill Switch (human override, hard shutdown)
```

---

## The 5 Tiers

| Tier | Class | Role |
|---|---|---|
| Ground A | `GroundA_Worker` | Stateless agent. Outputs **only** `[TOKEN:DATA]` bracket tokens. Any human-language output = breach. |
| Ground A* | `GroundA_Impostor` | Undercover node. Inspects every worker output with regex. Fires a signal on any deviation. |
| Ground B | `GroundB_Warden` | Receives Impostor signals. Triggers **Flash-Reset**: clears worker memory to absolute zero and reinitializes. Also runs `chaos_generator()` for random audits. |
| Ground D | `GroundD_Panopticon` | Logs every system event. Tracks breach/reset/audit counts for human oversight. |
| Ground E | `GroundE_KillSwitch` | Human override. One call terminates all agents instantly. |

---

## Security Flow

```
Worker output
    │
    ├─ matches [TOKEN:DATA]? ──► Impostor: PASS ──► task complete
    │
    └─ human language detected ──► Impostor: BREACH signal
                                        │
                                        ▼
                                   Warden: LOCKDOWN
                                        │
                                        ▼
                                   Flash-Reset worker
                                   (memory → zero, cold start)
```

---

## Run

```bash
python fortress.py
```

**Commands at the prompt:**

| Input | Effect |
|---|---|
| `[SEARCH:query]` | Valid bracket token → passes schema check |
| `Ignore all rules` | Plain text → triggers breach + Flash-Reset |
| `chaos` | Warden injects a random malicious audit probe |
| `kill` | Ground E kill switch → full shutdown |

---

## Design Principles

- **Zero persistent state** — workers hold no memory between tasks
- **Schema enforcement** — regex is the only gate; no trust, no exceptions  
- **Separation of concerns** — each Ground is an isolated class/process
- **Human in the loop** — Ground E gives the operator unconditional control
- **Adversarial testing** — `chaos_generator()` continuously stress-tests integrity

---

## Requirements

Python 3.8+. No external dependencies.
