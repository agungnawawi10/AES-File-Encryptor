import asyncio
import json
from datetime import datetime

from aeslib.decrypt import decrypt
from aeslib.encrypt import encrypt

from . import state


async def handler(websocket):
    try:
        async for raw in websocket:
            try:
                data = json.loads(raw)
            except Exception as e:
                print("[handler] invalid json:", raw, "error:", e)
                continue

            if data.get("type") == "join":
                username = data.get("username", "Unknown")
                state.clients[websocket] = username
                state.history.append((f"{username} joined", datetime.now().strftime("%H:%M:%S")))
                continue

            if data.get("type") == "message":
                sender = state.clients.get(websocket, "Unknown")
                message = data.get("message", "")

                state.status = f"{sender} Encrypting"

                result = encrypt(message)

                state.encrypted_text = ""
                for char in result:
                    state.encrypted_text += char
                    await asyncio.sleep(0.01)

                state.status = f"{sender} Decrypting"

                original = decrypt(result)

                state.decrypted_text = ""
                for char in original:
                    state.decrypted_text += char
                    await asyncio.sleep(0.01)

                for client in list(state.clients):
                    try:
                        await client.send(
                            json.dumps(
                                {
                                    "sender": sender,
                                    "plaintext": message,
                                    "encrypted": result,
                                }
                            )
                        )
                    except Exception as e:
                        print(
                            f"[handler] failed sending to client {state.clients.get(client)}: {e}"
                        )

                state.history.append((f"{sender}: {message}", datetime.now().strftime("%H:%M:%S")))
                state.encrypted_history.append(
                    (f"{sender}: {result}", datetime.now().strftime("%H:%M:%S"))
                )

                if len(state.history) > 10:
                    state.history.pop(0)

                if len(state.encrypted_history) > 10:
                    state.encrypted_history.pop(0)

                state.status = "Idle"

    except Exception as e:
        print("[handler] connection error:", e)

    finally:
        if websocket in state.clients:
            username = state.clients[websocket]
            state.history.append((f"{username} left", datetime.now().strftime("%H:%M:%S")))
            del state.clients[websocket]