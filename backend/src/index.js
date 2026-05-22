const express = require("express");
const cors = require("cors");
const { v4: uuidv4 } = require("uuid");
const { spawn } = require("child_process");
const path = require("path");
const Database = require("better-sqlite3");

const app = express();
const PORT = process.env.PORT || 4000;

// ── Database setup ──────────────────────────────────────────
const dbPath = path.join(__dirname, "..", "data", "sessions.db");
const fs = require("fs");
fs.mkdirSync(path.dirname(dbPath), { recursive: true });

const db = new Database(dbPath);
db.pragma("journal_mode = WAL");

db.exec(`
  CREATE TABLE IF NOT EXISTS sessions (
    id TEXT PRIMARY KEY,
    fs_state TEXT NOT NULL,
    history TEXT NOT NULL DEFAULT '[]',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
  )
`);

// ── Middleware ───────────────────────────────────────────────
app.use(cors());
app.use(express.json({ limit: "10mb" }));

// ── Helpers ─────────────────────────────────────────────────
const PYTHON_ENGINE = path.join(__dirname, "..", "..", "python-engine", "engine.py");

function runPythonEngine(input) {
  return new Promise((resolve, reject) => {
    const proc = spawn("python3", [PYTHON_ENGINE], {
      cwd: path.join(__dirname, "..", "..", "python-engine"),
    });

    let stdout = "";
    let stderr = "";

    proc.stdout.on("data", (data) => {
      stdout += data.toString();
    });
    proc.stderr.on("data", (data) => {
      stderr += data.toString();
    });

    proc.on("close", (code) => {
      if (code !== 0) {
        reject(new Error(stderr || `Python exited with code ${code}`));
        return;
      }
      try {
        resolve(JSON.parse(stdout));
      } catch {
        reject(new Error(`Invalid JSON from engine: ${stdout}`));
      }
    });

    proc.stdin.write(JSON.stringify(input));
    proc.stdin.end();
  });
}

// ── Routes ──────────────────────────────────────────────────

// Create a new session
app.post("/api/sessions", (req, res) => {
  const id = uuidv4();
  const defaultState = JSON.stringify(null); // engine will use defaults
  db.prepare("INSERT INTO sessions (id, fs_state, history) VALUES (?, ?, ?)").run(
    id,
    defaultState,
    "[]"
  );
  res.json({ sessionId: id });
});

// Get session info
app.get("/api/sessions/:id", (req, res) => {
  const row = db.prepare("SELECT * FROM sessions WHERE id = ?").get(req.params.id);
  if (!row) {
    return res.status(404).json({ error: "Session not found" });
  }
  const fsState = JSON.parse(row.fs_state);
  const history = JSON.parse(row.history);
  res.json({
    sessionId: row.id,
    cwd: fsState ? fsState.cwd : "/home/user",
    history,
  });
});

// Execute a command
app.post("/api/sessions/:id/exec", async (req, res) => {
  const { command } = req.body;
  if (!command) {
    return res.status(400).json({ error: "Missing command" });
  }

  const row = db.prepare("SELECT * FROM sessions WHERE id = ?").get(req.params.id);
  if (!row) {
    return res.status(404).json({ error: "Session not found" });
  }

  const fsState = JSON.parse(row.fs_state);
  try {
    const result = await runPythonEngine({
      command,
      fs_state: fsState,
    });

    // Update session state
    const history = JSON.parse(row.history);
    history.push({ command, output: result.output, error: result.error });
    // Keep last 100 commands
    if (history.length > 100) history.shift();

    db.prepare(
      "UPDATE sessions SET fs_state = ?, history = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?"
    ).run(JSON.stringify(result.fs_state), JSON.stringify(history), req.params.id);

    res.json({
      output: result.output,
      error: result.error,
      cwd: result.fs_state.cwd,
    });
  } catch (err) {
    console.error("Engine error:", err.message);
    res.status(500).json({ error: "Engine error: " + err.message });
  }
});

// Reset session
app.post("/api/sessions/:id/reset", (req, res) => {
  const row = db.prepare("SELECT * FROM sessions WHERE id = ?").get(req.params.id);
  if (!row) {
    return res.status(404).json({ error: "Session not found" });
  }
  db.prepare(
    "UPDATE sessions SET fs_state = ?, history = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?"
  ).run(JSON.stringify(null), "[]", req.params.id);
  res.json({ message: "Session reset" });
});

// ── Start ───────────────────────────────────────────────────
app.listen(PORT, () => {
  console.log(`Ubuntu Simulator API running on http://localhost:${PORT}`);
});
