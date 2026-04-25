# type: ignore
import asyncio
from crypto.encrypt import encrypt
from crypto.decrypt import decrypt
import websockets
from rich.live import Live
from rich.panel import Panel
from rich.text import Text
from datetime import datetime
import random

bars = "▁▂▃▄▅▆▇"
status = "Idle"
encrypted_text = ""
decrypted_text = ""
history = []


async def handler(websocket):
    global status, encrypted_text, decrypted_text

    status = "Connected"

    try:
        async for message in websocket:
            status = "Encrypting"

            result = encrypt(message)
            encrypted_text = "\n"

            # streaming per karakter
            for char in result:
                encrypted_text += char
                await asyncio.sleep(0.02)

            status = "Decrypting"

            # streaming decrypt
            original = decrypt(result)
            decrypted_text += "\n"

            for char in original:
                decrypted_text += char 
                await asyncio.sleep(0.02)

            await websocket.send(result)
            history.append((result, datetime.now().strftime("%H:%M:%S")))
            if len(history) > 10:
                history.pop(0)

            status = "Idle"

    except Exception as e:
        status = "Error"
        print("Connection error:", e)


def generate_wave():
    return "".join(random.choice(bars) for _ in range(30))


async def ui_loop():
    global status, encrypted_text, decrypted_text

    with Live(refresh_per_second=10) as live:
        while True:
            wave = generate_wave() if status != "Idle" else ""

            content = Text()
            content.append(f"Status: {status}\n\n", style="bold green")
            content.append(wave + "\n\n", style="cyan")
            content.append("Encrypted:\n", style="bold yellow")
            content.append(encrypted_text, style="yellow")
            content.append("\n\nDecrypted:\n", style="bold green")
            content.append(decrypted_text, style="green")

            # history di sini
            content.append("\nHistory:\n", style="bold magenta")
            for item, t in history[-5:]:
                content.append(f"[{t}] {item}\n", style="magenta")

            live.update(Panel(content, title="Encrypt CLI"))

            await asyncio.sleep(0.1)


async def main():
    server = websockets.serve(handler, "0.0.0.0", 8765, ping_interval=None)

    async with server:
        await asyncio.gather(asyncio.Future(), ui_loop())


if __name__ == "__main__":
    asyncio.run(main())