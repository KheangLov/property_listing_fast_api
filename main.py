from fastapi import FastAPI
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from routes.user_route import router as user_router
from routes.property_route import router as property_router

app = FastAPI()

app.include_router(user_router)
app.include_router(property_router)

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
    uvicorn.run("main:app", host="127.0.0.1", port=9800, reload=True)
