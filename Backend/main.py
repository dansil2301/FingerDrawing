from fastapi import FastAPI

from Config import setup_middleware
from Lifespan import create_lifespan
from Server.QueueOrchestration import QueueOrchestration
from Server.Handlers.WebRTCHandler import WebRTCHandler
from Server.Routes.Routes import get_router


orchestrator = QueueOrchestration()
web_rtc_handler = WebRTCHandler()

app = FastAPI(lifespan=create_lifespan(orchestrator))

setup_middleware(app)

app.include_router(get_router(orchestrator, web_rtc_handler))
