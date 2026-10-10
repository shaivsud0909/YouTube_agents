import uvicorn
from dotenv import load_dotenv
from core.config import settings

load_dotenv()

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=settings.port, reload=True)

