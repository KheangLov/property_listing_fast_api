from fastapi import FastAPI, status
from fastapi.encoders import jsonable_encoder
from fastapi.staticfiles import StaticFiles
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from routes.user_route import router as user_router
from routes.property_route import router as property_router
from routes.listing_route import router as listing_router
from routes.kh_address_route import router as kh_address_router
from os import getenv
from fastapi_pagination import add_pagination
from fastapi.exceptions import RequestValidationError, ValidationError
from fastapi.responses import JSONResponse
import json

app = FastAPI()
app.mount("/images", StaticFiles(directory="images"), name="images")
app.include_router(user_router)
app.include_router(property_router)
app.include_router(listing_router)
app.include_router(kh_address_router)


@app.exception_handler(RequestValidationError)
@app.exception_handler(ValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder({"detail": exc.errors()}),
    )

origins = ['*']

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


add_pagination(app)


# create_tables=True
# db.generate_mapping()

if __name__ == "__main__":
    uvicorn.run("main:app", host=getenv('HOST', "127.0.0.1"), port=getenv('PORT', 9800), reload=True)
