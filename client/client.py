import asyncio, websockets, json


async def send_messages(ws):
    loop = asyncio.get_event_loop()
    while True:
        msg = await loop.run_in_executor(None, input, "Pesan: ")
        await ws.send(json.dumps({"type": "message", "message": msg}))

async def receive_messages(ws):
    async for msg in ws:
        try:
            data = json.loads(msg)
            sender = data.get("sender")
            plaintext = data.get("plaintext", "")
            encrypted = data.get("encrypted", "")

            print(f"\n[{sender}] Plaintext: {plaintext}")
            print(f"[{sender}] Encrypted: {encrypted}")
            print("Kirim Pesan: ", end="", flush=True)
        except Exception as e:
            print(f"Error: {e}")

async def main():
    username = input("Username: ").strip() or "Anonymous"

    ws = await websockets.connect("ws://localhost:8765")

    await ws.send(json.dumps({"type": "join", "username": username}))

    print(f"Connected as {username}")

    await asyncio.gather(
        send_messages(ws),
        receive_messages(ws)
    )


asyncio.run(main())
