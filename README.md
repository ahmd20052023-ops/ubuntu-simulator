# Ubuntu Simulator 🐧

A web-based Ubuntu terminal simulator built with **React**, **Express.js**, and **Python**.

## Features

- **Virtual Filesystem** – Create, delete, edit, copy, and move files and folders
- **Ubuntu-style Terminal** – Looks and feels like a real Ubuntu terminal
- **Command History** – Navigate previous commands with arrow keys
- **Session Persistence** – Your filesystem state is saved in SQLite
- **Custom Commands** – Add your own commands in `python-engine/custom_commands.py`

## Architecture

```
┌──────────────┐     ┌──────────────────┐     ┌────────────────┐
│   React UI   │────▶│  Express.js API  │────▶│  Python Engine │
│  (Terminal)  │◀────│  (Data Storage)  │◀────│  (Commands)    │
└──────────────┘     └──────────────────┘     └────────────────┘
                            │
                      ┌─────┴─────┐
                      │  SQLite   │
                      │ (Sessions)│
                      └───────────┘
```

## Prerequisites

- **Node.js** >= 18
- **Python** >= 3.8
- **npm**

## Quick Start

```bash
# 1. Install dependencies
npm run install:all

# 2. Start backend (Terminal 1)
npm run dev:backend

# 3. Start frontend (Terminal 2)
npm run dev:frontend

# 4. Open http://localhost:3000
```

## Supported Commands

| Command | Description |
|---------|-------------|
| `ls [path]` | List directory contents |
| `cd [path]` | Change directory |
| `pwd` | Print working directory |
| `mkdir [-p] <dir>` | Create directory |
| `touch <file>` | Create empty file |
| `cat <file>` | Display file contents |
| `echo <text>` | Print text (`>` write, `>>` append to file) |
| `rm [-r] <path>` | Remove file or directory |
| `rmdir <dir>` | Remove empty directory |
| `cp <src> <dst>` | Copy file or directory |
| `mv <src> <dst>` | Move/rename file or directory |
| `clear` | Clear terminal |
| `help` | Show all available commands |

## Custom Commands

Edit `python-engine/custom_commands.py` to add your own commands:

```python
def cmd_mycommand(args, fs):
    """Description of your command."""
    return "Your output here"
```

The function name must start with `cmd_`. The command name will be everything after `cmd_`.

### Built-in Custom Commands

| Command | Description |
|---------|-------------|
| `greet [name]` | Say hello |
| `whoami` | Show current user |
| `date` | Show current date/time |
| `uname [-a]` | Show system information |
| `hostname` | Show hostname |
| `uptime` | Show system uptime |
| `neofetch` | Show system info (fancy) |

## Project Structure

```
ubuntu-simulator/
├── frontend/              # React app (Vite)
│   ├── src/
│   │   ├── components/
│   │   │   └── Terminal.jsx
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   └── index.css
│   └── package.json
├── backend/               # Express.js API
│   ├── src/
│   │   └── index.js
│   └── package.json
├── python-engine/         # Python command engine
│   ├── engine.py          # Main entry point
│   ├── filesystem.py      # Virtual filesystem
│   └── custom_commands.py # YOUR custom commands
├── package.json           # Root scripts
└── README.md
```
