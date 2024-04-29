from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from core.database import Base, Database
from controller.routes import api_router
from core.settings import SERVER_HOST, SERVER_PORT

db = Database()
Base.metadata.create_all(bind=db.engine)

app = FastAPI(
    title="Currency Converter API",
    version="1.0.0",
    description="A simple REST API to convert currencies"
)
app.include_router(api_router, prefix="/currencyConverter")


@app.get("/healthcheck", description="Just a server Health-Check")
def healthcheck() -> dict[str, str]:
    return {"status": "Health"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app="main:app", host=SERVER_HOST, port=SERVER_PORT, reload=True)
