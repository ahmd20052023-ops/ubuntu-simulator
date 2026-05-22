import React, { useState, useEffect, useRef } from "react";

const API = "/api";

const WELCOME = `Welcome to Ubuntu Simulator!
Type 'help' to see available commands.
`;

export default function Terminal({ sessionId }) {
  const [lines, setLines] = useState([{ text: WELCOME, type: "welcome" }]);
  const [input, setInput] = useState("");
  const [cwd, setCwd] = useState("/home/user");
  const [history, setHistory] = useState([]);
  const [historyIdx, setHistoryIdx] = useState(-1);
  const [busy, setBusy] = useState(false);

  const termRef = useRef(null);
  const inputRef = useRef(null);

  useEffect(() => {
    if (termRef.current) {
      termRef.current.scrollTop = termRef.current.scrollHeight;
    }
  }, [lines]);

  useEffect(() => {
    inputRef.current?.focus();
  }, [busy]);

  function focusInput() {
    inputRef.current?.focus();
  }

  function formatPrompt(dir) {
    const short = dir === "/home/user" ? "~" : dir.replace("/home/user", "~");
    return `user@ubuntu-sim:${short}$`;
  }

  async function handleSubmit(e) {
    e.preventDefault();
    const cmd = input.trim();
    setInput("");
    setHistoryIdx(-1);

    // Add the prompt + command to output
    const promptStr = formatPrompt(cwd);
    setLines((prev) => [...prev, { text: `${promptStr} ${cmd}`, type: "command" }]);

    if (!cmd) return;

    // Add to history
    setHistory((prev) => [...prev, cmd]);

    // Handle local clear
    if (cmd === "clear") {
      setLines([]);
      return;
    }

    setBusy(true);
    try {
      const res = await fetch(`${API}/sessions/${sessionId}/exec`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ command: cmd }),
      });

      const data = await res.json();

      if (data.output === "__CLEAR__") {
        setLines([]);
      } else if (data.output) {
        setLines((prev) => [
          ...prev,
          { text: data.output, type: data.error ? "error" : "output" },
        ]);
      }

      if (data.cwd) {
        setCwd(data.cwd);
      }
    } catch (err) {
      setLines((prev) => [
        ...prev,
        { text: `Error: ${err.message}`, type: "error" },
      ]);
    }
    setBusy(false);
  }

  function handleKeyDown(e) {
    if (e.key === "ArrowUp") {
      e.preventDefault();
      if (history.length === 0) return;
      const newIdx =
        historyIdx === -1 ? history.length - 1 : Math.max(0, historyIdx - 1);
      setHistoryIdx(newIdx);
      setInput(history[newIdx]);
    } else if (e.key === "ArrowDown") {
      e.preventDefault();
      if (historyIdx === -1) return;
      const newIdx = historyIdx + 1;
      if (newIdx >= history.length) {
        setHistoryIdx(-1);
        setInput("");
      } else {
        setHistoryIdx(newIdx);
        setInput(history[newIdx]);
      }
    }
  }

  return (
    <div className="terminal" ref={termRef} onClick={focusInput}>
      {lines.map((line, i) => (
        <div key={i} className={`output-line ${line.type}`}>
          {line.text}
        </div>
      ))}
      {!busy && (
        <form onSubmit={handleSubmit} className="prompt-line">
          <span className="prompt">
            <span className="user">user</span>
            <span className="at">@</span>
            <span className="host">ubuntu-sim</span>
            <span className="colon">:</span>
            <span className="path">
              {cwd === "/home/user" ? "~" : cwd.replace("/home/user", "~")}
            </span>
            <span className="dollar">$ </span>
          </span>
          <input
            ref={inputRef}
            className="input-field"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            autoFocus
            spellCheck={false}
            autoComplete="off"
          />
        </form>
      )}
    </div>
  );
}
