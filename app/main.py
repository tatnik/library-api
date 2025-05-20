from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError

from app.routers.auth import router as auth_router 
from app.routers.books import router as books_router
from app.routers.readers import router as readers_router
from app.routers.loan import router as loan_router



app = FastAPI(
    title="Library API",
    description="RESTful API for managing a library catalog",
    version="1.0.0"
)


@app.exception_handler(IntegrityError)
async def integrity_error_handler(request: Request, exc: IntegrityError):
    # Parse the error type and generate a human-readable description
    orig = str(exc.orig).lower()
    if "unique constraint" in orig and "isbn" in orig:
        detail = "A book with this ISBN already exists"
    elif "unique constraint" in orig and "email" in orig:
        detail = "A user with this email already exists"
    else:
        detail = "A unique or other database constraint was violated"
    return JSONResponse(
        status_code=400,
        content={"detail": detail}
    )

app.include_router(auth_router)
app.include_router(books_router)
app.include_router(readers_router)
app.include_router(loan_router)  
