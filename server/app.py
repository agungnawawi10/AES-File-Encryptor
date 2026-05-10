import asyncio

import websockets

from .ui import ui_loop
from .ws_handler import handler


async def main():
    server = websockets.serve(handler, "0.0.0.0", 8765, ping_interval=None)

    async with server:
        await asyncio.gather(asyncio.Future(), ui_loop())