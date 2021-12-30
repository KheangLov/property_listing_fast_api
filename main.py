from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from routes.user_route import router as user_router
from routes.property_route import router as property_router
from routes.listing_route import router as listing_router
from routes.kh_address_route import router as kh_address_router
from os import getenv

app = FastAPI()
app.mount("/images", StaticFiles(directory="images"), name="images")
app.include_router(user_router)
app.include_router(property_router)
app.include_router(listing_router)
app.include_router(kh_address_router)


origins = ['*']

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# create_tables=True
# db.generate_mapping()

if __name__ == "__main__":
    uvicorn.run("main:app", host=getenv('HOST', "127.0.0.1"), port=getenv('PORT', 9800), reload=True)
