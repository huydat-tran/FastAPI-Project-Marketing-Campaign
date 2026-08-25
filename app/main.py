from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

import app.models
from app.db.database import Base, engine
from app.routers import auth, campaign, campaign_task, users
from app.utils.exceptions import AppException

Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="Marketing Campaign Management Đẹp trai",
)


app.include_router(auth.router)
app.include_router(users.router)
app.include_router(campaign.router)
app.include_router(campaign_task.router)


@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"success": False, "message": exc.message, "detail": exc.detail},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=400,
        content={
            "success": False,
            "message": "Validation error",
            "detail": jsonable_encoder(exc.errors()),
        },
    )


@app.get("/health", tags=["System"])
def health_check():
    return {"status": "ok"}
