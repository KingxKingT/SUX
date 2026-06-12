"""
Ground C — The Strategist (Evolutionary Predictor)
====================================================
Observes ONLY metadata (speed, error rates, token efficiency).
Never looks at content. Never talks to workers directly.
Sends optimized prompt blueprint updates down to the Warden only.

The workers get smarter — but have no idea why or how. They just wake
up after a Warden reset with slightly better constraints baked in.
"""

import time, random
from dataclasses import dataclass, field


@dataclass
class PerformanceSnapshot:
    timestamp:       float
    breach_rate:     float   # breaches / total tasks
    reset_rate:      float   # resets / total tasks
    audit_pass_rate: float   # audits that passed clean / total audits
    token_efficiency: float  # how compressed the output tokens are (0–1)


@dataclass
class PromptUpdate:
    target:      str    # which worker class gets updated
    parameter:   str    # what constraint changes
    old_value:   str
    new_value:   str
    predicted_gain: str


class GroundC_Strategist:
    """
    The silent engineer above the Warden.
    Reads Panopticon metadata → runs internal simulations →
    proposes prompt blueprint updates → sends to Warden for deployment.

    Operational Laws:
    - Never suggest a change that gives workers more autonomy or memory.
    - Only optimize for: Speed, Token Reduction, Error Rate Reduction.
    - Never communicate with Ground A workers directly.
    - Treat workers as disposable, immutable functions.
    """

    OBSERVATION_INTERVAL = 30   # seconds between analysis cycles

    def __init__(self, panopticon, warden):
        self._pan     = panopticon
        self._warden  = warden
        self._history: list[PerformanceSnapshot] = []
        self._updates: list[PromptUpdate]         = []

    # ── Main observation cycle ────────────────────────────────────────────────

    def observe_and_optimize(self) -> PromptUpdate | None:
        """
        Take a metadata snapshot, run analysis, propose an update if beneficial.
        Returns the update sent to Warden, or None if no change needed.
        """
        snap = self._snapshot()
        self._history.append(snap)
        self._pan.log(
            f"[STRATEGIST] Snapshot → breach_rate={snap.breach_rate:.2f} "
            f"reset_rate={snap.reset_rate:.2f} "
            f"token_efficiency={snap.token_efficiency:.2f}"
        )

        update = self._analyze(snap)
        if update:
            self._pan.log(
                f"[STRATEGIST] Optimization found: {update.target} → "
                f"{update.parameter}: {update.old_value} → {update.new_value} "
                f"(predicted: {update.predicted_gain})"
            )
            self._pan.log(
                f"[STRATEGIST] Sending blueprint update to Warden for next reset cycle."
            )
            self._updates.append(update)
            self._pan.strategist_updates += 1
            return update

        self._pan.log("[STRATEGIST] No optimization needed this cycle.")
        return None

    # ── Internal analysis ─────────────────────────────────────────────────────

    def _snapshot(self) -> PerformanceSnapshot:
        total = max(self._pan.processed, 1)
        return PerformanceSnapshot(
            timestamp        = time.time(),
            breach_rate      = self._pan.breaches / total,
            reset_rate       = self._pan.resets   / total,
            audit_pass_rate  = max(0, 1 - (self._pan.breaches / max(self._pan.audits, 1))),
            token_efficiency = random.uniform(0.75, 0.98),   # simulated metric
        )

    def _analyze(self, snap: PerformanceSnapshot) -> PromptUpdate | None:
        """
        Simple heuristic optimizer.
        In a real system this would run prompt simulations and A/B comparisons.
        """
        # High breach rate → tighten worker schema enforcement
        if snap.breach_rate > 0.3:
            return PromptUpdate(
                target    = "GroundA_Worker",
                parameter = "schema_strictness",
                old_value = "standard",
                new_value = "maximum — reject any token with >0 ambiguity",
                predicted_gain = "~40% breach rate reduction"
            )

        # Low token efficiency → compress output vocabulary
        if snap.token_efficiency < 0.80:
            return PromptUpdate(
                target    = "CoreLangTranslator",
                parameter = "compression_depth",
                old_value = "keyword-match",
                new_value = "greedy multi-word compression",
                predicted_gain = "~25% token reduction"
            )

        # High reset rate → audit impostor loyalty test frequency
        if snap.reset_rate > 0.4:
            return PromptUpdate(
                target    = "GroundA_Impostor",
                parameter = "loyalty_test_probability",
                old_value = "0.15",
                new_value = "0.08 — reduce false positives",
                predicted_gain = "~30% unnecessary reset reduction"
            )

        return None   # system is healthy, no change

    def report(self) -> dict:
        return {
            "snapshots_taken":  len(self._history),
            "updates_proposed": len(self._updates),
            "updates":          [
                f"{u.target}.{u.parameter}: {u.old_value} → {u.new_value}"
                for u in self._updates
            ]
        }
