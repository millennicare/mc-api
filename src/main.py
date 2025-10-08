from contextlib import asynccontextmanager
from fastapi import FastAPI
from scalar_fastapi import get_scalar_api_reference

from src.routes.auth_router import router as auth_router
from src.routes.user_router import router as user_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # seed
    # check the existing roles
    print("seeding roles")
    print("seeding specialties")
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/api/healthcheck")
def read_root():
    return {"Hello": "World"}


@app.get("/scalar", include_in_schema=False)
async def scalar_html():
    return get_scalar_api_reference(
        # Your OpenAPI document
        openapi_url=app.openapi_url,
        # Avoid CORS issues (optional)
        scalar_proxy_url="https://proxy.scalar.com",
        title="Millennicare API docs",
    )


app.include_router(auth_router)
app.include_router(user_router)
