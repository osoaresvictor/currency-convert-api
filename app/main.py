from dotenv import load_dotenv, dotenv_values
load_dotenv()

from app.routers.routes import api_router
from app.core.log_requets_midleware import log_requests
from app.core.database import Database
from fastapi import FastAPI


db = Database().init_db()

app = FastAPI(
    title="Currency Converter API",
    version="1.0.0",
    summary="A simple REST API to perform convertion between two currencies",
    description="This API is a PoC (Proof of Concept) designed to explore \
                       concepts such as caching, resilience, scalability and \
                       best development practices. It was developed in Python \
                                                 using the FastAPI framework.",
    contact={
        "name": "Victor Soares",
        "email": "victor_soares@live.com",
        "url": "https://www.linkedin.com/in/soares-victor-it/"
    },
    root_path="/api"
)
app.include_router(api_router, prefix="/currencyConverter")
app.middlewsdare("http")(log_requests)


@app.get(
    "/healthcheck",
    description="Just a server Health-Check",
    tags=["Server"]
)
def healthcheck() -> dict["str", str]:
    return {"status": "Health"}
