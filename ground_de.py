"""
Ground D — The Panopticon (Human Observation Layer)
Ground E — The Sovereign Throne (Human Kill Switch)
====================================================
Ground D: Read-only mirror. AIs have NO idea it exists.
          Streams all system events to a human dashboard.
          Cannot send commands downward — observation only.

Ground E: Physical override. Cryptographic kill signal.
          Cuts power to all grounds. Default state = ALIVE requires
          constant human confirmation (Dead Man's Switch integration).
"""

import time
from dataclasses import dataclass, field


# ── Ground D: Panopticon ──────────────────────────────────────────────────────

@dataclass
class GroundD_Panopticon:
    """
    One-way glass. Logs everything. Controls nothing.
    The AIs below cannot see this layer, cannot write to it,
    and cannot send exploit payloads upward.
    """
    processed:          int   = 0
    breaches:           int   = 0
    resets:             int   = 0
    audits:             int   = 0
    strategist_updates: int   = 0
    _log: list = field(default_factory=list)

    def log(self, msg: str):
        entry = {"ts": time.strftime("%H:%M:%S"), "msg": msg}
        self._log.append(entry)
        print(f"[{entry['ts']}] {msg}")

    def get_log(self, last_n: int = 50) -> list[dict]:
        """Returns the last N log entries for the dashboard."""
        return self._log[-last_n:]

    def stats(self) -> dict:
        return {
            "processed":          self.processed,
            "breaches":           self.breaches,
            "resets":             self.resets,
            "audits":             self.audits,
            "strategist_updates": self.strategist_updates,
        }

    def report(self):
        print(f"\n{'─'*55}")
        print(f"  PANOPTICON FINAL REPORT")
        print(f"  Processed : {self.processed}")
        print(f"  Breaches  : {self.breaches}")
        print(f"  Resets    : {self.resets}")
        print(f"  Audits    : {self.audits}")
        print(f"  Strategist updates: {self.strategist_updates}")
        print(f"{'─'*55}\n")


# ── Ground E: Sovereign Throne ────────────────────────────────────────────────

class GroundE_KillSwitch:
    """
    Human override. Exists entirely outside the AI network.
    Sends a hardwired termination signal — no AI can intercept or block it.

    Two modes:
      soft_kill  → graceful shutdown (flushes logs, reports)
      hard_kill  → instant power cut (emergency, no cleanup)
    """

    def __init__(self):
        self._engaged = False

    @property
    def engaged(self) -> bool:
        return self._engaged

    def soft_kill(self, warden, panopticon):
        """Graceful shutdown — drain current tasks, report, power off."""
        self._engaged = True
        panopticon.log("[KILL SWITCH] Soft kill engaged by human operator.")
        panopticon.log("[KILL SWITCH] Draining active tasks…")
        time.sleep(0.5)
        warden.active = False
        warden.disarm_dead_man_switch()
        panopticon.log("[KILL SWITCH] All grounds offline.")
        panopticon.report()

    def hard_kill(self, warden, panopticon):
        """Emergency instant shutdown. No cleanup. Equivalent to cutting power."""
        self._engaged = True
        panopticon.log("[KILL SWITCH] ⚡ HARD KILL — instant power cut by human operator.")
        warden.active = False
        # In production: os.kill(os.getpid(), signal.SIGKILL) per ground process
        panopticon.report()
