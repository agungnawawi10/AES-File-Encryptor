# type: ignore
import asyncio
import json
from aeslib.encrypt import encrypt
from aeslib.decrypt import decrypt
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
encrypted_history = []

clients = {}

async def handler(websocket):
    global status, encrypted_text, decrypted_text
    try:
        async for raw in websocket:
            try:
                data = json.loads(raw)
            except Exception as e:
                print("[handler] invalid json:", raw, "error:", e)
                continue

            # USER JOIN
            if data.get("type") == "join":
                username = data.get("username", "Unknown")
                clients[websocket] = username
                history.append((f"{username} joined", datetime.now().strftime("%H:%M:%S")))
                # print(f"[handler] {username} joined")
                continue

            # USER MESSAGE
            if data.get("type") == "message":
                sender = clients.get(websocket, "Unknown")
                message = data.get("message", "")

                # print(f"[handler] received message from {sender}: {message}")

                status = f"{sender} Encrypting"

                result = encrypt(message)

                encrypted_text = ""
                for char in result:
                    encrypted_text += char
                    await asyncio.sleep(0.01)

                status = f"{sender} Decrypting"

                original = decrypt(result)

                decrypted_text = ""
                for char in original:
                    decrypted_text += char
                    await asyncio.sleep(0.01)   

                # Broadcast ke semua user (copy keys to avoid runtime change)
                for client in list(clients):
                    try:
                        await client.send(json.dumps({
                            "sender": sender,
                            "plaintext": message,
                            "encrypted": result
                        }))
                    except Exception as e:
                        print(f"[handler] failed sending to client {clients.get(client)}: {e}")

                history.append((f"{sender}: {message}", datetime.now().strftime("%H:%M:%S")))
                encrypted_history.append((f"{sender}: {result}", datetime.now().strftime("%H:%M:%S")))

                if len(history) > 10:
                    history.pop(0)

                if len(encrypted_history) > 10:
                    encrypted_history.pop(0)

                status = "Idle"

    except Exception as e:
        print("[handler] connection error:", e)

    finally:
        if websocket in clients:
            username = clients[websocket]
            history.append((f"{username} left", datetime.now().strftime("%H:%M:%S")))
            # print(f"[handler] {username} left")
            del clients[websocket]

def generate_wave():
    return "".join(random.choice(bars) for _ in range(30))

async def ui_loop():
    global status

    with Live(refresh_per_second=10) as live:
        while True:
            wave = generate_wave() if status != "Idle" else ""

            content = Text()
            content.append(f"Status: {status}\n\n", style="bold green")
            content.append(wave + "\n\n", style="cyan")

            content.append("Encrypted:\n", style="bold yellow")
            content.append(encrypted_text)

            content.append("\n\nDecrypted:\n", style="bold green")
            content.append(decrypted_text)

            content.append("\n\nOnline Users:\n", style="bold blue")
            for name in clients.values():
                content.append(f"- {name}\n")

            content.append("\nHistory:\n", style="bold magenta")
            for item, t in history[-5:]:
                content.append(f"[{t}] {item}\n")

            content.append("\nEncrypted History:\n", style="bold red")
            for item, t in encrypted_history[-5:]:
                content.append(f"[{t}] {item}\n")

            live.update(Panel(content, title="Encrypt CLI"))

            await asyncio.sleep(0.1)

async def main():
    server = websockets.serve(handler, "0.0.0.0", 8765, ping_interval=None)

    async with server:
        await asyncio.gather(
            asyncio.Future(),
            ui_loop()
        )

if __name__ == "__main__":
    asyncio.run(main())
