from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from routes import farmer, batch, consumer, auth as auth_routes, reports as reports_routes, sensor as sensor_routes
from database import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(
    title="FarmChain API",
    description="Blockchain-powered organic food traceability",
    version="1.0.0",
    lifespan=lifespan
)

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(farmer.router, prefix="/farmer", tags=["Farmer"])
app.include_router(batch.router, prefix="/batch", tags=["Batch"])
app.include_router(consumer.router, prefix="/verify", tags=["Consumer"])
app.include_router(auth_routes.router, prefix="/auth", tags=["Auth"])
app.include_router(reports_routes.router, prefix="/reports", tags=["Reports"])
app.include_router(sensor_routes.router, prefix="/sensor", tags=["Sensor"])

@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")
