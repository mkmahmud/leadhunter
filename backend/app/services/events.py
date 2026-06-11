import asyncio
import json
from collections import defaultdict
from collections.abc import AsyncIterator


class EventBroker:
    def __init__(self) -> None:
        self._queues: dict[str, set[asyncio.Queue[str]]] = defaultdict(set)

    async def publish(self, channel: str, event: dict[str, object]) -> None:
        message = json.dumps(event, default=str)
        for queue in list(self._queues[channel]):
            await queue.put(message)

    async def subscribe(self, channel: str) -> AsyncIterator[str]:
        queue: asyncio.Queue[str] = asyncio.Queue()
        self._queues[channel].add(queue)
        try:
            while True:
                yield await queue.get()
        finally:
            self._queues[channel].discard(queue)


broker = EventBroker()
