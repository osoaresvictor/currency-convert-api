from dotenv import load_dotenv
load_dotenv()

from app.routers.routes import api_router
from app.core.log_requets_midleware import log_requests
from fastapi import FastAPI


db = Database()
Base.metadata.create_all(bind=db.engine)

app = FastAPI(
    title="Currency Converter API",
    version="1.0.0",
    description="A simple REST API to convert currencies"
)
app.include_router(api_router, prefix="/currencyConverter")
app.middleware("http")(log_requests)


@app.get("/healthcheck", description="Just a server Health-Check")
def healthcheck() -> dict[str, str]:
    return {"status": "Health"}
