from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from service_gateway.routes import tests, webhooks


@asynccontextmanager
async def lifespan(app: FastAPI):
    Path("results").mkdir(exist_ok=True)
    yield


app = FastAPI(
    title="Foxhound Test Framework",
    description="API-first test automation framework",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(tests.router)
app.include_router(webhooks.router)


@app.get("/api/v1/health")
async def health_check():
    return {"status": "healthy", "service": "foxhound"}
