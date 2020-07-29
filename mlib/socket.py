import asyncio
from dataclasses import dataclass
from typing import Awaitable, Callable, Any

import websockets

from mlib.parallel import run_in_thread, threaded

@dataclass
class SocketServer:
    host: str
    port: int

    # "Any" here should be websocket?
    fun: Callable[[Any, str], Awaitable]

    @threaded
    def start(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(
            websockets.serve(self.fun, self.host, self.port)
        )
        loop.run_forever()
