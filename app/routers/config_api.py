from fastapi import APIRouter

from core.logs import get_logs,delete_all_logs
from core.tree import folder_tree

config_router = APIRouter()

config_router.get("/health")(lambda: {"status": "ok"})
config_router.post("/get_logs")(get_logs)
config_router.delete("/delete_logs")(delete_all_logs)
config_router.get("/tree")(folder_tree)



