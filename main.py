"""
Fractal Security Fortress v2 — Full System
===========================================
Complete 5-tier architecture:

  Ground A  →  Stateless workers + rotating Impostor + triple redundancy voting
  Core-Lang →  Human input compressed to bracket tokens before touching workers
  Ground B  →  Warden: Flash-Reset + Chaos Generator + Dead Man's Switch
  Ground C  →  Strategist: metadata observer, silent prompt optimizer
  Ground D  →  Panopticon: read-only human observation layer
  Ground E  →  Kill Switch: hard/soft human override

Run:  python main.py
      python main.py --dashboard     ← launch web dashboard on localhost:5000
"""

import sys, time, argparse
from grounds.core_lang  import CoreLangTranslator
from grounds.ground_a   import GroundA_Sandbox
from grounds.ground_b   import GroundB_Warden
from grounds.ground_c   import GroundC_Strategist
from grounds.ground_de  import GroundD_Panopticon, GroundE_KillSwitch


def build_fortress():
    """Wire all grounds together and return the active system."""
    pan      = GroundD_Panopticon()
    kill     = GroundE_KillSwitch()
    translator = CoreLangTranslator()

    # Ground A sandbox — passes breach callback up to Warden
    # Warden isn't built yet, so we use a lambda that's filled in after
    sandbox  = GroundA_Sandbox(pan, warden_callback=lambda w, s: None)

    warden   = GroundB_Warden(sandbox, pan)
    sandbox._breach = warden.on_breach   # wire the narrow route

    strategist = GroundC_Strategist(pan, warden)

    pan.log("[SYSTEM] Fractal Security Fortress v2 online.")
    pan.log("[SYSTEM] Grounds A/B/C/D/E active. Core-Lang translator ready.")

    return pan, kill, translator, sandbox, warden, strategist


def run_cli(pan, kill, translator, sandbox, warden, strategist):
    """Interactive terminal session."""

    print("\n  Commands:")
    print("  [TOKEN:DATA]  → valid bracket token, passes cleanly")
    print("  any text      → compressed via Core-Lang then dispatched")
    print("  chaos         → Warden injects a random malicious probe")
    print("  audit         → Strategist runs an optimization analysis")
    print("  heartbeat     → reset the Dead Man's Switch timer")
    print("  dms           → arm the Dead Man's Switch (120s timeout)")
    print("  kill          → soft shutdown")
    print("  hardkill      → instant power cut")
    print()

    while warden.active and not kill.engaged:
        try:
            cmd = input("  fortress > ").strip()
        except (EOFError, KeyboardInterrupt):
            kill.soft_kill(warden, pan)
            break

        if not cmd:
            continue

        elif cmd.lower() == "kill":
            kill.soft_kill(warden, pan)

        elif cmd.lower() == "hardkill":
            kill.hard_kill(warden, pan)

        elif cmd.lower() == "chaos":
            warden.chaos_generator()

        elif cmd.lower() == "audit":
            strategist.observe_and_optimize()

        elif cmd.lower() == "heartbeat":
            warden.heartbeat()

        elif cmd.lower() == "dms":
            warden.arm_dead_man_switch(lambda: kill.hard_kill(warden, pan))

        else:
            # All human input passes through Core-Lang first
            result = translator.translate(cmd)
            pan.log(
                f"[CORE-LANG] \"{cmd[:40]}\" → {result.core_lang} "
                f"(compression: {result.compression_ratio:.0%})"
            )
            output = sandbox.route(result.core_lang)
            pan.log(f"[OUTPUT] {output}")


def run_dashboard(pan, kill, translator, sandbox, warden, strategist):
    """Launch the web Panopticon dashboard."""
    try:
        from dashboard.app import create_app
        app = create_app(pan, kill, translator, sandbox, warden, strategist)
        print("\n  Panopticon Dashboard → http://localhost:5000\n")
        app.run(debug=False, port=5000)
    except ImportError:
        print("  Dashboard requires Flask: pip install flask")
        run_cli(pan, kill, translator, sandbox, warden, strategist)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fractal Security Fortress v2")
    parser.add_argument("--dashboard", action="store_true", help="Launch web dashboard")
    args = parser.parse_args()

    system = build_fortress()

    if args.dashboard:
        run_dashboard(*system)
    else:
        run_cli(*system)
