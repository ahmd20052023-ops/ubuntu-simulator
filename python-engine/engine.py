"""
Ubuntu Simulator – Command Engine

Reads a JSON request from stdin, processes the command,
and writes a JSON response to stdout.

Input:  {"command": "ls -la", "fs_state": {...}}
Output: {"output": "...", "fs_state": {...}, "error": false}
"""

import json
import sys
import shlex
import importlib
import inspect
from filesystem import VirtualFileSystem


def _load_custom_commands():
    """Load all cmd_* functions from custom_commands.py."""
    commands = {}
    try:
        mod = importlib.import_module("custom_commands")
        importlib.reload(mod)
        for name, fn in inspect.getmembers(mod, inspect.isfunction):
            if name.startswith("cmd_"):
                cmd_name = name[4:]
                commands[cmd_name] = fn
    except Exception:
        pass
    return commands


def _parse_echo(raw_args_str):
    """Parse echo arguments, handling redirection."""
    append = False
    filename = None
    text = raw_args_str

    if ">>" in raw_args_str:
        parts = raw_args_str.split(">>", 1)
        text = parts[0].strip()
        filename = parts[1].strip()
        append = True
    elif ">" in raw_args_str:
        parts = raw_args_str.split(">", 1)
        text = parts[0].strip()
        filename = parts[1].strip()

    text = text.strip("'\"")
    return text, filename, append


def execute(command_str, fs):
    """Execute a command string and return (output, is_error)."""
    command_str = command_str.strip()
    if not command_str:
        return "", False

    # Handle echo specially for redirection
    if command_str.startswith("echo "):
        raw_args = command_str[5:]
        text, filename, append = _parse_echo(raw_args)
        if filename:
            err = fs.write_file(filename, text + "\n", append=append)
            if err:
                return err, True
            return "", False
        return text, False

    # Parse command
    try:
        parts = shlex.split(command_str)
    except ValueError:
        parts = command_str.split()

    cmd = parts[0]
    args = parts[1:]

    # Built-in commands
    if cmd == "ls":
        path = None
        show_all = False
        for a in args:
            if a.startswith("-"):
                if "a" in a:
                    show_all = True
            else:
                path = a
        names, err = fs.ls(path)
        if err:
            return err, True
        if not show_all:
            names = [n for n in names if not n.startswith(".")]
        return "  ".join(names), False

    elif cmd == "cd":
        path = args[0] if args else "/home/user"
        err = fs.cd(path)
        if err:
            return err, True
        return "", False

    elif cmd == "pwd":
        return fs.pwd(), False

    elif cmd == "mkdir":
        if not args:
            return "mkdir: missing operand", True
        parents = "-p" in args
        dirs = [a for a in args if not a.startswith("-")]
        errors = []
        for d in dirs:
            if parents:
                # Create intermediate directories
                abs_path = fs._resolve(d)
                current = ""
                for part in abs_path.strip("/").split("/"):
                    current += "/" + part
                    node = fs._get_node(current)
                    if node is None:
                        err = fs.mkdir(current)
                        if err:
                            errors.append(err)
                            break
            else:
                err = fs.mkdir(d)
                if err:
                    errors.append(err)
        if errors:
            return "\n".join(errors), True
        return "", False

    elif cmd == "touch":
        if not args:
            return "touch: missing file operand", True
        errors = []
        for f in args:
            err = fs.touch(f)
            if err:
                errors.append(err)
        if errors:
            return "\n".join(errors), True
        return "", False

    elif cmd == "cat":
        if not args:
            return "cat: missing file operand", True
        outputs = []
        for f in args:
            content, err = fs.cat(f)
            if err:
                return err, True
            outputs.append(content)
        return "".join(outputs), False

    elif cmd == "rm":
        if not args:
            return "rm: missing operand", True
        recursive = False
        files = []
        for a in args:
            if a.startswith("-") and "r" in a:
                recursive = True
            else:
                files.append(a)
        errors = []
        for f in files:
            err = fs.rm(f, recursive=recursive)
            if err:
                errors.append(err)
        if errors:
            return "\n".join(errors), True
        return "", False

    elif cmd == "rmdir":
        if not args:
            return "rmdir: missing operand", True
        errors = []
        for d in args:
            err = fs.rmdir(d)
            if err:
                errors.append(err)
        if errors:
            return "\n".join(errors), True
        return "", False

    elif cmd == "cp":
        if len(args) < 2:
            return "cp: missing operand", True
        err = fs.cp(args[0], args[1])
        if err:
            return err, True
        return "", False

    elif cmd == "mv":
        if len(args) < 2:
            return "mv: missing operand", True
        err = fs.mv(args[0], args[1])
        if err:
            return err, True
        return "", False

    elif cmd == "echo":
        return " ".join(args), False

    elif cmd == "clear":
        return "__CLEAR__", False

    elif cmd == "help":
        custom = _load_custom_commands()
        lines = [
            "Available commands:",
            "  ls [path]          - List directory contents",
            "  cd [path]          - Change directory",
            "  pwd                - Print working directory",
            "  mkdir [-p] <dir>   - Create directory",
            "  touch <file>       - Create empty file",
            "  cat <file>         - Display file contents",
            "  echo <text>        - Print text (use > or >> to write to file)",
            "  rm [-r] <path>     - Remove file or directory",
            "  rmdir <dir>        - Remove empty directory",
            "  cp <src> <dst>     - Copy file or directory",
            "  mv <src> <dst>     - Move/rename file or directory",
            "  clear              - Clear terminal",
            "  help               - Show this help message",
        ]
        if custom:
            lines.append("")
            lines.append("Custom commands:")
            for name, fn in sorted(custom.items()):
                doc = fn.__doc__ or ""
                lines.append(f"  {name:18s} - {doc.strip()}")
        return "\n".join(lines), False

    else:
        # Check custom commands
        custom = _load_custom_commands()
        if cmd in custom:
            try:
                result = custom[cmd](args, fs)
                return str(result), False
            except Exception as e:
                return f"{cmd}: error: {e}", True

        return f"{cmd}: command not found", True


def main():
    raw = sys.stdin.read()
    try:
        req = json.loads(raw)
    except json.JSONDecodeError:
        resp = {"output": "Engine error: invalid JSON input", "fs_state": None, "error": True}
        print(json.dumps(resp))
        return

    command = req.get("command", "")
    fs_state = req.get("fs_state")

    fs = VirtualFileSystem(fs_state)
    output, is_error = execute(command, fs)

    resp = {
        "output": output,
        "fs_state": fs.to_dict(),
        "error": is_error,
    }
    print(json.dumps(resp))


if __name__ == "__main__":
    main()
