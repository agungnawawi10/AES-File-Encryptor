import asyncio
import websockets

async def send_message():
    uri = "ws://localhost:8765"

    async with websockets.connect(uri) as websocket:
        print("Connected to server")

        while True:
            message = await asyncio.to_thread(input, "Ketik pesan: ")
            await websocket.send(message)

            # response = await websocket.recv()
            # print(f"[RECEIVED] {response}")

asyncio.run(send_message())
