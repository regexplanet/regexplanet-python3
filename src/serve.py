import asyncio
import os
from hypercorn.config import Config
from hypercorn.asyncio import serve

from app import app

config = Config()
config.bind = [ os.environ.get("HOSTNAME", "0.0.0.0") + ":" + os.environ.get("PORT", 4000) ]

asyncio.run(serve(app, config))