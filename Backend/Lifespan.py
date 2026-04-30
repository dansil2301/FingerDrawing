import asyncio
from contextlib import asynccontextmanager

def create_lifespan(orchestrator):
    @asynccontextmanager
    async def lifespan(app):
        task = asyncio.create_task(orchestrator.watch_ttl())
        yield
        task.cancel()
    return lifespan