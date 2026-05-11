import asyncio
import importlib
import random
import shutil
import time

from rich.live import Live
from rich.panel import Panel
from rich.text import Text
from rich.layout import Layout
from rich.table import Table
from rich.align import Align
from rich.console import Group
from rich.padding import Padding
from rich.spinner import Spinner
from rich.rule import Rule

from . import state


# =========================
# DESIGN TOKENS
# =========================

BACKGROUND_STYLE = "on #0b1f24"
SURFACE_STYLE    = "on #12313a"
SURFACE_BORDER   = "#2f7f86"

# Functional color groups — max 4 roles
ENCRYPTION_COLOR = "#e0b84f"   # everything encryption-related (warm yellow)
SYSTEM_COLOR     = "#7fb6ff"   # status, connectivity (cool blue)
HISTORY_COLOR    = "#a85bd3"   # all history panels (purple)
POSITIVE_COLOR   = "#8fd18b"   # decrypted / success (green)

ACCENT = "#f2a17a"
MUTED  = "#9ec3bf"
DIM    = "bright_black"
ERROR  = "#ef6b73"


# =========================
# BANNER CACHE
# =========================

_CACHED_BANNER = None


def _render_banner() -> Panel:
    banner_source  = "Realtime AES"
    terminal_width = shutil.get_terminal_size((120, 40)).columns

    try:
        pyfiglet  = importlib.import_module("pyfiglet")
        banner    = pyfiglet.Figlet(
            font="slant", width=max(48, terminal_width - 12)
        ).renderText(banner_source)

        banner_text    = Text()
        banner_palette = [
            f"bold {ACCENT}",
            "bold #e68c60",
            "bold #d97b51",
            "bold #c96844",
        ]
        for i, line in enumerate(banner.rstrip("\n").splitlines()):
            banner_text.append(line + "\n", style=banner_palette[i % len(banner_palette)])
    except Exception:
        banner_text = Text(banner_source, style=f"bold {ACCENT}")

    subtitle = Text("Encrypted monitoring dashboard", style=f"bold {MUTED}")
    meta     = Text(
        "Live websocket activity  •  AES-256 encryption  •  Real-time",
        style=DIM,
    )

    return Panel(
        Align.center(Group(banner_text, Padding(subtitle, (0, 0, 0, 1)), Padding(meta, (0, 0, 0, 1)))),
        border_style=SURFACE_BORDER,
        style=SURFACE_STYLE,
        padding=(0, 2),
    )


def build_banner() -> Panel:
    """Return cached banner — only renders once."""
    global _CACHED_BANNER
    if _CACHED_BANNER is None:
        _CACHED_BANNER = _render_banner()
    return _CACHED_BANNER


# =========================
# HELPERS
# =========================

def _panel(content, title: str, color: str, padding=(1, 3)) -> Panel:
    """Unified panel builder — consistent style, single color per panel."""
    return Panel(
        content,
        title=f"[bold {color}]{title}[/bold {color}]",
        border_style=color,
        style=SURFACE_STYLE,
        padding=padding,
    )


def _spinner_or_text(value: str | None, waiting_label: str, color: str) -> Text | Group:
    """Show spinner when waiting, styled text when data is present."""
    if not value:
        spinner = Spinner("dots", style=DIM)
        label   = Text(f"  {waiting_label}", style=DIM)
        return Group(Align.left(Group(spinner, label)))
    t = Text(value, style=color)
    return t


def _truncation_notice(history: list, shown: int) -> str | None:
    total = len(history)
    if total > shown:
        return f"  ↑ {total - shown} older entries hidden\n"
    return None


# =========================
# STATUS PANEL (full-width, prominent)
# =========================

def build_status_panel() -> Panel:
    is_active = state.status != "Idle"

    status_line = Text()
    status_line.append("● ", style=f"bold {POSITIVE_COLOR}" if is_active else f"bold {DIM}")
    status_line.append(state.status + "\n", style=f"bold {POSITIVE_COLOR}" if is_active else MUTED)

    # Animated wave only when active — uses Rich Spinner for smoothness
    if is_active:
        wave_chars = "".join(random.choice(state.bars) for _ in range(40))
        status_line.append(wave_chars, style=ACCENT)
    else:
        status_line.append("No active connections — start a client to begin", style=DIM)

    rule  = Rule(style=SURFACE_BORDER)
    stats = Text()
    stats.append(f"  Connected users: ", style=DIM)
    stats.append(str(len(state.clients)), style=f"bold {SYSTEM_COLOR}")
    stats.append("   •   Messages processed: ", style=DIM)
    stats.append(str(len(state.history)), style=f"bold {ENCRYPTION_COLOR}")

    content = Group(Align.center(status_line), rule, stats)
    return _panel(content, "⚡ System Status", SYSTEM_COLOR, padding=(1, 4))


# =========================
# USERS PANEL
# =========================

def build_users_panel() -> Panel:
    t = Table.grid(padding=(0, 1))

    if not state.clients:
        t.add_row(Text("No connections", style=DIM))
        t.add_row(Text("Waiting for clients…", style=f"italic {MUTED}"))
    else:
        for name in state.clients.values():
            t.add_row(
                Text("●", style=f"bold {POSITIVE_COLOR}"),
                Text(name, style=MUTED),
            )

    return _panel(t, "👥 Online Users", SYSTEM_COLOR)


# =========================
# ENCRYPT PANEL
# =========================

def build_encrypt_panel() -> Panel:
    content = _spinner_or_text(
        state.encrypted_text,
        "Awaiting message to encrypt…",
        ENCRYPTION_COLOR,
    )
    return _panel(content, "🔐 AES Encrypted", ENCRYPTION_COLOR)
    # return _panel(content, "🔐 AES Encrypted", ENCRYPTION_COLOR)


# =========================
# DECRYPT PANEL
# =========================

def build_decrypt_panel() -> Panel:
    content = _spinner_or_text(
        state.decrypted_text,
        "Awaiting encrypted input…",
        POSITIVE_COLOR,
    )
    # return _panel(content, "🔓 AES Decrypted",SURFACE_BORDER)
    return _panel(content, "🔓 AES Decrypted", POSITIVE_COLOR)


# =========================
# HISTORY PANEL
# =========================

HISTORY_SHOWN = 6


def build_history_panel() -> Panel:
    history_text = Text()

    if not state.history:
        history_text.append("No activity yet\n", style=DIM)
        history_text.append("Events will appear here once messages flow in.", style=f"italic {MUTED}")
    else:
        notice = _truncation_notice(state.history, HISTORY_SHOWN)
        if notice:
            history_text.append(notice, style=DIM)

        for item, t in state.history[-HISTORY_SHOWN:]:
            history_text.append(f"[{t}] ", style=DIM)
            history_text.append(f"{item}\n", style=MUTED)

    # return _panel(history_text, "📜 Activity History", SURFACE_BORDER)
    return _panel(history_text, "📜 Activity History", HISTORY_COLOR)


# =========================
# ENCRYPTED HISTORY PANEL
# =========================

ENC_HISTORY_SHOWN = 5


def build_encrypted_history_panel() -> Panel:
    enc_text = Text()

    if not state.encrypted_history:
        enc_text.append("No encrypted messages yet\n", style=DIM)
        enc_text.append("Encrypted payloads will be logged here.", style=f"italic {MUTED}")
    else:
        notice = _truncation_notice(state.encrypted_history, ENC_HISTORY_SHOWN)
        if notice:
            enc_text.append(notice, style=DIM)

        for item, t in state.encrypted_history[-ENC_HISTORY_SHOWN:]:
            enc_text.append(f"[{t}] ", style=DIM)
            enc_text.append(f"{item}\n", style=ENCRYPTION_COLOR)

    # return _panel(enc_text, "🛡 Encrypted History", SURFACE_BORDER)
    return _panel(enc_text, "🛡 Encrypted History", HISTORY_COLOR)


# =========================
# MAIN UI LOOP
# =========================

async def ui_loop():
    layout = Layout()

    # Priority hierarchy: Status+Users → Encrypt/Decrypt → History
    layout.split_column(
        Layout(name="banner", size=7),   # compact header
        Layout(name="top",    size=10),  # status (wide) + users (narrow), cukup tinggi
        Layout(name="middle", ratio=2),  # primary: encrypt / decrypt
        Layout(name="bottom", ratio=2),  # secondary: history panels
    )

    # Status dapat 75% lebar, Users 25% — proporsional
    layout["top"].split_row(
        Layout(name="status", ratio=3),
        Layout(name="users",  ratio=1),
    )

    layout["middle"].split_row(
        Layout(name="encrypted"),
        Layout(name="decrypted"),
    )

    layout["bottom"].split_row(
        Layout(name="history"),
        Layout(name="encrypted_history"),
    )

    with Live(layout, refresh_per_second=10, screen=True) as live:
        while True:
            layout["banner"].update(build_banner())
            layout["status"].update(build_status_panel())
            layout["users"].update(build_users_panel())
            layout["encrypted"].update(build_encrypt_panel())
            layout["decrypted"].update(build_decrypt_panel())
            layout["history"].update(build_history_panel())
            layout["encrypted_history"].update(build_encrypted_history_panel())

            await asyncio.sleep(0.1)