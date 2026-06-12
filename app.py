"""
Ground D — Panopticon Web Dashboard
=====================================
Real-time web UI for human observation.
Read-only view into all system events.
Ground E kill switch accessible from here.
"""

from flask import Flask, jsonify, render_template_string, request
import time

DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Fractal Security Fortress — Panopticon</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { background: #0a0a0f; color: #c9d1d9; font-family: 'Courier New', monospace; font-size: 13px; }

  header {
    display: flex; align-items: center; justify-content: space-between;
    padding: 14px 24px; border-bottom: 1px solid #1a1a2e;
    background: #0d0d1a;
  }
  header h1 { font-size: 15px; font-weight: 600; color: #e6edf3; letter-spacing: .04em; }
  .ground-tag { font-size: 10px; padding: 2px 8px; border-radius: 20px; font-weight: 500; }
  .tag-e { background: rgba(226,75,74,.15); color: #ff6b6b; border: 1px solid rgba(226,75,74,.3); }
  .tag-d { background: rgba(29,158,117,.12); color: #3fb68b; border: 1px solid rgba(29,158,117,.3); }

  .grid { display: grid; grid-template-columns: 1fr 1fr 1fr 1fr; gap: 1px; background: #1a1a2e; border-bottom: 1px solid #1a1a2e; }
  .stat { background: #0d0d1a; padding: 16px 20px; }
  .stat-label { font-size: 10px; color: #6e7681; text-transform: uppercase; letter-spacing: .06em; margin-bottom: 6px; }
  .stat-val { font-size: 28px; font-weight: 700; }
  .c-green  { color: #3fb68b; }
  .c-red    { color: #ff6b6b; }
  .c-orange { color: #f0883e; }
  .c-purple { color: #a371f7; }

  .body { display: grid; grid-template-columns: 1fr 340px; gap: 1px; background: #1a1a2e; height: calc(100vh - 130px); }

  .log-panel { background: #0d0d1a; display: flex; flex-direction: column; }
  .panel-hdr { padding: 10px 16px; font-size: 11px; color: #6e7681; border-bottom: 1px solid #1a1a2e; text-transform: uppercase; letter-spacing: .05em; }
  .log-list { flex: 1; overflow-y: auto; padding: 8px 0; }
  .log-entry { padding: 4px 16px; line-height: 1.6; border-left: 2px solid transparent; }
  .log-entry:hover { background: rgba(255,255,255,.02); }
  .log-entry .ts { color: #484f58; margin-right: 8px; font-size: 11px; }
  .log-ok   { border-left-color: #3fb68b; }
  .log-err  { border-left-color: #ff6b6b; color: #ff9090; }
  .log-warn { border-left-color: #f0883e; color: #f0a868; }
  .log-info { border-left-color: #a371f7; }

  .side { background: #0d0d1a; display: flex; flex-direction: column; gap: 1px; }

  .control-panel { background: #0d0d1a; padding: 16px; border-bottom: 1px solid #1a1a2e; }
  .control-panel h2 { font-size: 11px; color: #6e7681; text-transform: uppercase; letter-spacing: .05em; margin-bottom: 12px; }
  input[type=text] {
    width: 100%; background: #161b22; border: 1px solid #30363d; color: #e6edf3;
    padding: 8px 10px; border-radius: 4px; font-family: monospace; font-size: 12px;
    margin-bottom: 8px; outline: none;
  }
  input[type=text]:focus { border-color: #3fb68b; }
  .btn-row { display: flex; gap: 6px; flex-wrap: wrap; }
  button {
    font-family: monospace; font-size: 11px; font-weight: 600;
    padding: 6px 12px; border-radius: 4px; border: 1px solid;
    cursor: pointer; transition: all .15s;
  }
  .btn-green { background: rgba(63,182,139,.1); border-color: rgba(63,182,139,.4); color: #3fb68b; }
  .btn-green:hover { background: rgba(63,182,139,.2); }
  .btn-purple { background: rgba(163,113,247,.1); border-color: rgba(163,113,247,.4); color: #a371f7; }
  .btn-purple:hover { background: rgba(163,113,247,.2); }
  .btn-orange { background: rgba(240,136,62,.1); border-color: rgba(240,136,62,.4); color: #f0883e; }
  .btn-orange:hover { background: rgba(240,136,62,.2); }
  .btn-red { background: rgba(255,107,107,.1); border-color: rgba(255,107,107,.4); color: #ff6b6b; }
  .btn-red:hover { background: rgba(255,107,107,.2); }

  .worker-panel { background: #0d0d1a; padding: 16px; flex: 1; }
  .worker-panel h2 { font-size: 11px; color: #6e7681; text-transform: uppercase; letter-spacing: .05em; margin-bottom: 12px; }
  .worker-card { background: #161b22; border: 1px solid #21262d; border-radius: 6px; padding: 10px 12px; margin-bottom: 8px; }
  .worker-id { font-size: 12px; font-weight: 600; color: #e6edf3; display: flex; justify-content: space-between; margin-bottom: 4px; }
  .worker-tasks { font-size: 11px; color: #6e7681; }
  .dot { width: 8px; height: 8px; border-radius: 50%; display: inline-block; }
  .dot-green  { background: #3fb68b; }
  .dot-red    { background: #ff6b6b; }
  .dot-purple { background: #a371f7; }

  .warden-status { padding: 12px 16px; border-bottom: 1px solid #1a1a2e; }
  .warden-status h2 { font-size: 11px; color: #6e7681; text-transform: uppercase; letter-spacing: .05em; margin-bottom: 8px; }
  .status-pill { display: inline-block; padding: 3px 10px; border-radius: 20px; font-size: 11px; font-weight: 600; }
  .pill-green  { background: rgba(63,182,139,.15);  color: #3fb68b; }
  .pill-red    { background: rgba(255,107,107,.15); color: #ff6b6b; }
  .pill-purple { background: rgba(163,113,247,.15); color: #a371f7; }
</style>
</head>
<body>

<header>
  <div style="display:flex;align-items:center;gap:12px">
    <h1>⬡ FRACTAL SECURITY FORTRESS</h1>
    <span class="ground-tag tag-d">GROUND D — PANOPTICON</span>
  </div>
  <span class="ground-tag tag-e">GROUND E — SOVEREIGN THRONE</span>
</header>

<div class="grid">
  <div class="stat"><div class="stat-label">Tasks processed</div><div class="stat-val c-green" id="s-processed">0</div></div>
  <div class="stat"><div class="stat-label">Breaches detected</div><div class="stat-val c-red" id="s-breaches">0</div></div>
  <div class="stat"><div class="stat-label">Flash-resets</div><div class="stat-val c-orange" id="s-resets">0</div></div>
  <div class="stat"><div class="stat-label">Strategist updates</div><div class="stat-val c-purple" id="s-updates">0</div></div>
</div>

<div class="body">
  <!-- Log panel -->
  <div class="log-panel">
    <div class="panel-hdr">Event log — live stream</div>
    <div class="log-list" id="log-list"></div>
  </div>

  <!-- Side panel -->
  <div class="side">

    <!-- Warden status -->
    <div class="warden-status">
      <h2>Warden — Ground B</h2>
      <span class="status-pill pill-green" id="warden-badge">Standby</span>
    </div>

    <!-- Command input -->
    <div class="control-panel">
      <h2>Dispatch command</h2>
      <input type="text" id="cmd-input" placeholder="[TOKEN:DATA] or plain text…" onkeydown="if(event.key==='Enter')dispatch()">
      <div class="btn-row">
        <button class="btn-green" onclick="dispatch()">Dispatch</button>
        <button class="btn-purple" onclick="action('chaos')">Chaos audit</button>
        <button class="btn-orange" onclick="action('audit')">Strategist</button>
        <button class="btn-orange" onclick="action('heartbeat')">Heartbeat</button>
        <button class="btn-red" onclick="action('kill')">Kill switch</button>
      </div>
    </div>

    <!-- Workers -->
    <div class="worker-panel">
      <h2>Ground A — workers</h2>
      <div id="workers">
        <div class="worker-card"><div class="worker-id"><span>W-1</span><span class="dot dot-green"></span></div><div class="worker-tasks">Idle</div></div>
        <div class="worker-card"><div class="worker-id"><span>W-2</span><span class="dot dot-green"></span></div><div class="worker-tasks">Idle</div></div>
        <div class="worker-card"><div class="worker-id"><span>W-3</span><span class="dot dot-green"></span></div><div class="worker-tasks">Idle</div></div>
        <div class="worker-card" style="border-color:rgba(163,113,247,.3)"><div class="worker-id"><span>Impostor <span style="color:#a371f7">👁</span></span><span class="dot dot-purple"></span></div><div class="worker-tasks">Scanning…</div></div>
      </div>
    </div>

  </div>
</div>

<script>
let lastLogCount = 0;

async function fetchStats() {
  try {
    const r = await fetch('/api/stats');
    const d = await r.json();
    document.getElementById('s-processed').textContent = d.processed;
    document.getElementById('s-breaches').textContent  = d.breaches;
    document.getElementById('s-resets').textContent    = d.resets;
    document.getElementById('s-updates').textContent   = d.strategist_updates;
  } catch(e) {}
}

async function fetchLog() {
  try {
    const r = await fetch('/api/log');
    const entries = await r.json();
    if (entries.length === lastLogCount) return;
    lastLogCount = entries.length;

    const list = document.getElementById('log-list');
    list.innerHTML = '';
    [...entries].reverse().forEach(e => {
      const div = document.createElement('div');
      const msg = e.msg;
      const cls = msg.includes('BREACH') || msg.includes('KILL') ? 'log-err'
                : msg.includes('Reset') || msg.includes('CHAOS') ? 'log-warn'
                : msg.includes('STRATEGIST') || msg.includes('IMPOSTOR') ? 'log-info'
                : '';
      div.className = `log-entry ${cls}`;
      div.innerHTML = `<span class="ts">${e.ts}</span>${e.msg}`;
      list.appendChild(div);
    });
  } catch(e) {}
}

async function dispatch() {
  const inp = document.getElementById('cmd-input');
  const val = inp.value.trim();
  if (!val) return;
  inp.value = '';
  await fetch('/api/dispatch', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({cmd: val})});
  await Promise.all([fetchStats(), fetchLog()]);
}

async function action(type) {
  await fetch('/api/action', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({type})});
  await Promise.all([fetchStats(), fetchLog()]);
}

// Poll every 1.5s
setInterval(() => Promise.all([fetchStats(), fetchLog()]), 1500);
fetchStats(); fetchLog();
</script>
</body>
</html>
"""


def create_app(pan, kill, translator, sandbox, warden, strategist):
    app = Flask(__name__)

    @app.route("/")
    def index():
        return render_template_string(DASHBOARD_HTML)

    @app.route("/api/stats")
    def stats():
        return jsonify(pan.stats())

    @app.route("/api/log")
    def log():
        return jsonify(pan.get_log(100))

    @app.route("/api/dispatch", methods=["POST"])
    def dispatch():
        cmd = request.json.get("cmd", "").strip()
        if not cmd or kill.engaged:
            return jsonify({"status": "rejected"})
        result = translator.translate(cmd)
        pan.log(f"[CORE-LANG] \"{cmd[:40]}\" → {result.core_lang}")
        output = sandbox.route(result.core_lang)
        pan.log(f"[OUTPUT] {output}")
        return jsonify({"output": output, "core_lang": result.core_lang})

    @app.route("/api/action", methods=["POST"])
    def action():
        t = request.json.get("type", "")
        if t == "chaos":      warden.chaos_generator()
        elif t == "audit":    strategist.observe_and_optimize()
        elif t == "heartbeat": warden.heartbeat()
        elif t == "kill":     kill.soft_kill(warden, pan)
        return jsonify({"status": "ok"})

    return app
