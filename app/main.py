from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.config import settings

from app.routers.config_api import config_router
from app.routers.research_api import research_router


app = FastAPI()

app = FastAPI(title=settings.title, description=settings.description, version=settings.version,swagger_ui_parameters={"docExpansion": "none"})


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup_event():
    from core.logs import logger
    logger.info("Starting up the application...")

from app.routers.script_api import script_router

app.include_router(config_router, tags=["config"], prefix="/config")
app.include_router(script_router, tags=["script"], prefix="/script")
app.include_router(research_router, tags=["research"], prefix="/research")
