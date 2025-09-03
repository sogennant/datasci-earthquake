from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import sentry_sdk
import logging

# Lazy imports to reduce cold start time
from backend.api.config import settings
from backend.database.session import warm_up_connection_pool

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize Sentry
sentry_sdk.init(
    dsn=settings.sentry_dsn,
    # Add request headers and IP for users,
    # see https://docs.sentry.io/platforms/python/data-management/data-collected/ for more info
    send_default_pii=False,
)

# Create FastAPI instance with custom docs and openapi url
app = FastAPI(docs_url="/docs", openapi_url="/openapi.json", redirect_slashes=False)

# Lazy import routers to reduce cold start time


def include_routers():
    from backend.api.routers import (
        liquefaction_api,
        tsunami_api,
        soft_story_api,
        health_api,
    )

    app.include_router(liquefaction_api.router)
    app.include_router(tsunami_api.router)
    app.include_router(soft_story_api.router)
    app.include_router(health_api.router)


include_routers()

origins = [
    "http://localhost",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global exception handler (ensures flush before serverless exit)
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    sentry_sdk.capture_exception(exc)
    sentry_sdk.flush(timeout=2.0)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


@app.on_event("startup")
async def startup_event():
    """Warm up resources on startup to reduce cold start latency"""
    logger.info("Starting up QuakeSafe API...")
    try:
        warm_up_connection_pool()
        logger.info("Database connection pool warmed up successfully")

        # Preload GeoJSON files to reduce cold start latency
        from backend.api.routers import soft_story_api, liquefaction_api, tsunami_api
        import asyncio

        async def preload_geojson_files():
            """Preload GeoJSON files in parallel for faster startup"""
            tasks = [
                asyncio.create_task(
                    asyncio.to_thread(soft_story_api.load_soft_story_geojson)
                ),
                asyncio.create_task(
                    asyncio.to_thread(liquefaction_api.load_liquefaction_geojson)
                ),
                asyncio.create_task(
                    asyncio.to_thread(tsunami_api.load_tsunami_geojson)
                ),
            ]
            try:
                await asyncio.gather(*tasks)
                logger.info("GeoJSON files preloaded successfully from CDN/local")
            except Exception as e:
                logger.warning(f"Failed to preload some GeoJSON files: {e}")

        try:
            asyncio.run(preload_geojson_files())
        except Exception as e:
            logger.warning(f"Failed to preload GeoJSON files: {e}")

    except Exception as e:
        logger.warning(f"Failed to warm up database pool: {e}")
