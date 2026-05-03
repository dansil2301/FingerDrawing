import os

from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware


load_dotenv()


def setup_middleware(app):
    ENV = os.getenv("ENV", "dev")

    if ENV == "prod":
        origins = [
            "https://eyextrace.com/",
            "https://www.eyextrace.com/",
        ]
    else:
        origins = [
            "http://localhost:3000",
            "http://127.0.0.1:3000",
        ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_methods=["*"],
        allow_headers=["*"],
        allow_credentials=True,
    )
