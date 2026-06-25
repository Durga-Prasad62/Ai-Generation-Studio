"""
main.py
Application entrypoint — creates the FastAPI app, wires CORS, routers,
global error handling, and creates DB tables on startup.

Run with:
    uvicorn main:app --reload
"""
import logging

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from database.db import Base, engine
from routes import auth, content

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("content_studio")

app = FastAPI(
    title="AI Content Generation Studio",
    description="Backend API for generating blog articles, product descriptions, "
                 "marketing campaigns, social posts, email templates, ad copy, and SEO content.",
    version="1.0.0",
)

# --- CORS (allow the React frontend to call this API) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Global error handling ---
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"error": "validation_error", "message": "Invalid request data", "details": exc.errors()},
    )


@app.exception_handler(SQLAlchemyError)
async def db_exception_handler(request: Request, exc: SQLAlchemyError):
    logger.exception("Database error: %s", exc)
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={"error": "database_error", "message": "A database error occurred"},
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled error: %s", exc)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": "internal_server_error", "message": "Something went wrong. Please try again."},
    )


# --- Routers ---
app.include_router(auth.router)
app.include_router(content.router)


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
    logger.info("AI Content Generation Studio backend started")


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok"}
