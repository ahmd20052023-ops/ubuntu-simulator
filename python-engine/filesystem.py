"""Virtual filesystem for the Ubuntu simulator."""

import json
import copy


def _default_fs():
    """Return the default filesystem tree."""
    return {
        "type": "dir",
        "children": {
            "home": {
                "type": "dir",
                "children": {
                    "user": {
                        "type": "dir",
                        "children": {
                            "Documents": {"type": "dir", "children": {}},
                            "Downloads": {"type": "dir", "children": {}},
                            "Desktop": {"type": "dir", "children": {}},
                            "welcome.txt": {
                                "type": "file",
                                "content": "Welcome to Ubuntu Simulator!\nType 'help' to see available commands.\n",
                            },
                        },
                    }
                },
            },
            "etc": {"type": "dir", "children": {}},
            "var": {"type": "dir", "children": {}},
            "tmp": {"type": "dir", "children": {}},
            "usr": {"type": "dir", "children": {}},
        },
    }


class VirtualFileSystem:
    """A tree-based virtual filesystem."""

    def __init__(self, state=None):
        if state is None:
            self.root = _default_fs()
            self.cwd = "/home/user"
        else:
            self.root = state.get("root", _default_fs())
            self.cwd = state.get("cwd", "/home/user")

    def to_dict(self):
        return {"root": self.root, "cwd": self.cwd}

    # ── helpers ──────────────────────────────────────────────

    def _resolve(self, path):
        """Resolve a path string to an absolute path."""
        if not path.startswith("/"):
            path = self.cwd.rstrip("/") + "/" + path
        parts = []
        for p in path.split("/"):
            if p == "" or p == ".":
                continue
            elif p == "..":
                if parts:
                    parts.pop()
            else:
                parts.append(p)
        return "/" + "/".join(parts)

    def _get_node(self, path):
        """Return the node at *path*, or None."""
        path = self._resolve(path)
        if path == "/":
            return self.root
        node = self.root
        for part in path.strip("/").split("/"):
            if node.get("type") != "dir":
                return None
            node = node.get("children", {}).get(part)
            if node is None:
                return None
        return node

    def _get_parent_and_name(self, path):
        """Return (parent_node, child_name) for *path*."""
        path = self._resolve(path)
        parts = path.strip("/").split("/")
        name = parts[-1]
        parent_path = "/" + "/".join(parts[:-1])
        parent = self._get_node(parent_path)
        return parent, name

    # ── public API ───────────────────────────────────────────

    def ls(self, path=None):
        target = self._get_node(path or self.cwd)
        if target is None:
            return None, f"ls: cannot access '{path}': No such file or directory"
        if target["type"] == "file":
            return [path], None
        names = sorted(target.get("children", {}).keys())
        return names, None

    def cd(self, path):
        abs_path = self._resolve(path)
        node = self._get_node(abs_path)
        if node is None:
            return f"cd: {path}: No such file or directory"
        if node["type"] != "dir":
            return f"cd: {path}: Not a directory"
        self.cwd = abs_path
        return None

    def pwd(self):
        return self.cwd

    def mkdir(self, path):
        parent, name = self._get_parent_and_name(path)
        if parent is None:
            return f"mkdir: cannot create directory '{path}': No such file or directory"
        if parent["type"] != "dir":
            return f"mkdir: cannot create directory '{path}': Not a directory"
        if name in parent["children"]:
            return f"mkdir: cannot create directory '{path}': File exists"
        parent["children"][name] = {"type": "dir", "children": {}}
        return None

    def touch(self, path):
        parent, name = self._get_parent_and_name(path)
        if parent is None:
            return f"touch: cannot touch '{path}': No such file or directory"
        if name not in parent["children"]:
            parent["children"][name] = {"type": "file", "content": ""}
        return None

    def cat(self, path):
        node = self._get_node(path)
        if node is None:
            return None, f"cat: {path}: No such file or directory"
        if node["type"] == "dir":
            return None, f"cat: {path}: Is a directory"
        return node.get("content", ""), None

    def write_file(self, path, content, append=False):
        parent, name = self._get_parent_and_name(path)
        if parent is None:
            return f"write: cannot write to '{path}': No such file or directory"
        if name in parent["children"] and parent["children"][name]["type"] == "dir":
            return f"write: '{path}': Is a directory"
        if append and name in parent["children"]:
            parent["children"][name]["content"] += content
        else:
            parent["children"][name] = {"type": "file", "content": content}
        return None

    def rm(self, path, recursive=False):
        parent, name = self._get_parent_and_name(path)
        if parent is None or name not in parent.get("children", {}):
            return f"rm: cannot remove '{path}': No such file or directory"
        node = parent["children"][name]
        if node["type"] == "dir" and not recursive:
            return f"rm: cannot remove '{path}': Is a directory (use rm -r)"
        del parent["children"][name]
        return None

    def rmdir(self, path):
        parent, name = self._get_parent_and_name(path)
        if parent is None or name not in parent.get("children", {}):
            return f"rmdir: failed to remove '{path}': No such file or directory"
        node = parent["children"][name]
        if node["type"] != "dir":
            return f"rmdir: failed to remove '{path}': Not a directory"
        if node.get("children"):
            return f"rmdir: failed to remove '{path}': Directory not empty"
        del parent["children"][name]
        return None

    def cp(self, src, dst):
        src_node = self._get_node(src)
        if src_node is None:
            return f"cp: cannot stat '{src}': No such file or directory"
        dst_parent, dst_name = self._get_parent_and_name(dst)
        if dst_parent is None:
            return f"cp: cannot create '{dst}': No such file or directory"
        dst_parent["children"][dst_name] = copy.deepcopy(src_node)
        return None

    def mv(self, src, dst):
        src_parent, src_name = self._get_parent_and_name(src)
        if src_parent is None or src_name not in src_parent.get("children", {}):
            return f"mv: cannot stat '{src}': No such file or directory"
        dst_parent, dst_name = self._get_parent_and_name(dst)
        if dst_parent is None:
            return f"mv: cannot move to '{dst}': No such file or directory"
        dst_parent["children"][dst_name] = src_parent["children"].pop(src_name)
        return None
