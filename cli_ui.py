# type: ignore
from rich.live import Live
from rich.panel import Panel
from rich.text import Text
import time
import random

bars = "▁▂▃▄▅▆▇"

def generate_wave():
    return "".join(random.choice(bars) for _ in range(40))

status = "Recording..."

with Live(refresh_per_second=10) as live:
    while True:
        wave = generate_wave()

        content = Text()
        content.append(f"Status: {status}\n\n", style="bold green")
        content.append(wave, style="cyan")

        live.update(Panel(content, title="Encrypt CLI"))

        time.sleep(0.1)
c