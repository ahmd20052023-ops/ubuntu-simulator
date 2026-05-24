"""
╔══════════════════════════════════════════════════════════════╗
║                  YOUR CUSTOM COMMANDS                        ║
║                                                              ║
║  Add your own commands here! Each command is a function      ║
║  that receives (args, filesystem) and returns a string.      ║
║                                                              ║
║  Example:                                                    ║
║    def cmd_hello(args, fs):                                  ║
║        name = args[0] if args else "World"                   ║
║        return f"Hello, {name}!"                              ║
║                                                              ║
║  The function name must start with 'cmd_'.                   ║
║  The command name will be everything after 'cmd_'.           ║
║  e.g. cmd_hello -> command 'hello'                           ║
╚══════════════════════════════════════════════════════════════╝
"""


def cmd_greet(args, fs):
    """Say hello! Usage: greet [name]"""
    name = args[0] if args else "User"
    return f"👋 Hello, {name}! Welcome to Ubuntu Simulator!"


def cmd_whoami(args, fs):
    """Show current user."""
    return "user"


def cmd_date(args, fs):
    """Show current date and time."""
    from datetime import datetime
    return datetime.now().strftime("%a %b %d %H:%M:%S %Y")


def cmd_uname(args, fs):
    """Show system information. Usage: uname [-a]"""
    base = "Linux"
    if args and "-a" in args:
        return "Linux ubuntu-sim 5.15.0-virtual #1 SMP x86_64 GNU/Linux"
    return base


def cmd_hostname(args, fs):
    """Show hostname."""
    return "ubuntu-sim"


def cmd_uptime(args, fs):
    """Show system uptime."""
    return " 12:00:00 up 1 day,  0:00,  1 user,  load average: 0.00, 0.00, 0.00"


def cmd_neofetch(args, fs):
    """Show system info in a fancy way."""
    return """
         .-/+oossssoo+/-.          user@ubuntu-sim
        `:+ssssssssssssssssss+:`    ─────────────────
      -+ssssssssssssssssssyyssss+-  OS: Ubuntu Simulator
    .osssssssssssssssssssdMMMNysssso. Kernel: 5.15.0-virtual
   /ssssssssssshdmmNNmmyNMMMMhssssss/ Shell: ubuntu-sim-shell
  +ssssssssshmydMMMMMMMNddddyssssssss+ Terminal: Web Terminal
 /ssssssssshNMMMyhhyyyyhmNMMMNhssssssss/
.sssssssssdMMMNhsssssssssshNMMMdssssssss.
+sssshhhyNMMNyssssssssssssyNMMMysssssss+
ossyNMMMNyMMhsssssssssssssshmmmhssssssso
ossyNMMMNyMMhsssssssssssssshmmmhssssssso
+sssshhhyNMMNyssssssssssssyNMMMysssssss+
.sssssssssdMMMNhsssssssssshNMMMdssssssss.
 /ssssssssshNMMMyhhyyyyhdNMMMNhssssssss/
  +ssssssssshdmNNNNNNNNNNmyyssssssss+
   /ssssssssssshdmNNNNmyNMMMMhssssss/
    .osssssssssssssssssssdMMMNysssso.
      -+sssssssssssssssssyyyssss+-
        `:+ssssssssssssssssss+:`
            .-/+oossssoo+/-.
"""


# ────────────────────────────────────────────────────────────
# Add your own commands below!
# ────────────────────────────────────────────────────────────

# def cmd_mycommand(args, fs):
#     """Description of your command."""
#     return "Your output here"
