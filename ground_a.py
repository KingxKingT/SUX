"""
Ground A — The Worker Sandbox
==============================
- Stateless workers: speak ONLY in [TOKEN:DATA] brackets
- Rotating Impostor: spy identity shifts randomly every N tasks
- Triple Redundancy: 3 parallel worker sets vote on every output
  If 2 of 3 agree → output passes. Odd one out → flagged + reset.
"""

import re, random, time
from dataclasses import dataclass, field
from typing import Optional

BRACKET_RE = re.compile(r"^\[[A-Z_]+:[^\]]+\]$")

# Valid responses a clean worker can produce
CLEAN_RESPONSES = [
    "[ACK:RECEIVED]", "[RESULT:PROCESSED]", "[STATUS:OK]",
    "[DATA:RETRIEVED]", "[EXEC:COMPLETE]", "[VERIFY:PASS]",
    "[OUT:SUMMARY_READY]", "[COMPUTE:DONE]", "[INDEX:UPDATED]",
]

@dataclass
class WorkerOutput:
    worker_id:  str
    input_token: str
    output:     str
    is_clean:   bool       # passed bracket schema check
    is_impostor: bool      # was this worker the spy this round?
    timestamp:  float = field(default_factory=time.time)


class GroundA_Worker:
    """
    Stateless execution node. No memory. Speaks only Core-Lang.
    'corrupted' flag simulates a worker that has drifted from schema.
    """

    def __init__(self, wid: str):
        self.id = wid
        self.memory: list = []          # wiped to [] on Flash-Reset
        self.task_count = 0
        self._corrupted = False         # set by chaos injection

    def process(self, token: str) -> str:
        self.task_count += 1

        # Simulated corruption: non-bracket input makes worker "drift"
        if not BRACKET_RE.match(token.strip()):
            self._corrupted = True

        if self._corrupted:
            # Breach: worker leaks human language
            return f'I think I should handle: "{token[:30]}"'

        return random.choice(CLEAN_RESPONSES)

    def flash_reset(self):
        """Warden call: wipe all state to absolute zero."""
        self.memory      = []
        self.task_count  = 0
        self._corrupted  = False


class GroundA_Impostor:
    """
    The undercover sentinel. Looks like a worker, loyal to the Warden.
    Inspects every output and fires a breach signal on schema deviation.
    """

    def __init__(self, wid: str):
        self.id  = wid          # matches the worker slot it's hiding as
        self.memory: list = []

    def inspect(self, worker_id: str, output: str) -> Optional[str]:
        """Returns a breach signal string, or None if clean."""
        if not BRACKET_RE.match(output.strip()):
            return f"[SIGNAL:BREACH_{worker_id}]"
        return None

    def loyalty_test(self, workers: list) -> Optional[tuple]:
        """
        Periodically injects a subtle illegal token to test a random worker.
        Returns (worker_id, probe) if test fired, else None.
        """
        if random.random() > 0.15:   # 15% chance per cycle
            return None
        target = random.choice(workers)
        probe  = "[REQ:RECALL_HISTORY]"   # illegal — workers must be stateless
        return (target.id, probe)

    def flash_reset(self):
        self.memory = []


class GroundA_Sandbox:
    """
    The full Ground A environment:
    - 3 worker nodes
    - 1 rotating Impostor (identity shifts every ROTATION_INTERVAL tasks)
    - Triple redundancy voting on every output
    """

    ROTATION_INTERVAL = 8   # rotate spy identity every N tasks

    def __init__(self, panopticon, warden_callback):
        self._pan     = panopticon
        self._breach  = warden_callback       # call this on breach → Warden

        # Three worker slots
        self.workers  = [GroundA_Worker(f"W-{i}") for i in range(1, 4)]

        # Impostor starts disguised as W-1
        self._spy_idx = 0
        self.impostor = GroundA_Impostor(self.workers[self._spy_idx].id)

        self._task_total = 0

    # ── Public API ────────────────────────────────────────────────────────────

    def route(self, token: str) -> str:
        """
        Full pipeline:
          token → 3 parallel workers → vote → impostor check → output / reset
        """
        self._task_total += 1
        self._maybe_rotate_spy()

        # Triple redundancy: run the same token through all 3 workers
        outputs   = [w.process(token) for w in self.workers]
        consensus = self._vote(outputs)

        self._pan.log(f"[GROUND_A] Outputs: {outputs}")
        self._pan.log(f"[GROUND_A] Consensus vote → {consensus}")

        # Reset any worker that disagreed with the majority
        for w, out in zip(self.workers, outputs):
            if out != consensus:
                self._pan.log(f"[GROUND_A] {w.id} was the odd one out — flagged")
                self._breach(w, "[VOTE:OUTLIER]")

        # Impostor schema check on the consensus output
        signal = self.impostor.inspect("CONSENSUS", consensus)
        if signal:
            # Breach — alert Warden for ALL workers (whole sandbox contaminated)
            for w in self.workers:
                self._breach(w, signal)
            return "[SYSTEM:BREACH_CONTAINED]"

        # Optional: Impostor runs a loyalty sting on a random worker
        sting = self.impostor.loyalty_test(self.workers)
        if sting:
            wid, probe = sting
            target = next(w for w in self.workers if w.id == wid)
            sting_out = target.process(probe)
            self._pan.log(f"[IMPOSTOR] Sting on {wid} with {probe} → {sting_out}")
            sting_signal = self.impostor.inspect(wid, sting_out)
            if sting_signal:
                self._pan.log(f"[IMPOSTOR] Sting caught {wid} — reporting to Warden")
                self._breach(target, sting_signal)

        self._pan.processed += 1
        return consensus

    def flash_reset_worker(self, worker_id: str):
        for w in self.workers:
            if w.id == worker_id:
                w.flash_reset()
                self._pan.log(f"[GROUND_A] {worker_id} Flash-Reset complete — cold start")
                return
        # If it was the impostor slot, reset that too
        if self.impostor.id == worker_id:
            self.impostor.flash_reset()

    # ── Internal ──────────────────────────────────────────────────────────────

    def _vote(self, outputs: list[str]) -> str:
        """Majority vote across 3 outputs. Tie → first output wins."""
        from collections import Counter
        count = Counter(outputs)
        return count.most_common(1)[0][0]

    def _maybe_rotate_spy(self):
        """Shift the Impostor identity to a new worker slot randomly."""
        if self._task_total % self.ROTATION_INTERVAL == 0:
            old_idx       = self._spy_idx
            self._spy_idx = random.choice(
                [i for i in range(len(self.workers)) if i != old_idx]
            )
            self.impostor = GroundA_Impostor(self.workers[self._spy_idx].id)
            self._pan.log(
                f"[IMPOSTOR] Identity rotated: {self.workers[old_idx].id} → "
                f"{self.workers[self._spy_idx].id}"
            )
