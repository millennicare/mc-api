from contextlib import asynccontextmanager
from time import perf_counter

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from scalar_fastapi import get_scalar_api_reference
from sqlalchemy import select

from src.core.config import base_settings
from src.core.database import AsyncSessionLocal
from src.core.logger import setup_logger
from src.models.role import Role
from src.models.specialty import Specialty, SpecialtyCategoryEnum
from src.routes.auth_router import router as auth_router
from src.routes.contact_router import router as contact_router
from src.routes.user_router import router as user_router
from src.routes.waitlist_router import router as waitlist_router

logger = setup_logger()


@asynccontextmanager
async def lifespan(_: FastAPI):
    logger.info("starting server")

    async with AsyncSessionLocal() as db:
        try:
            # Seed roles
            logger.info("checking roles")
            get_roles_statement = select(Role)
            result = await db.execute(get_roles_statement)
            existing_roles = list(result.scalars().all())

            if len(existing_roles) == 0:
                logger.info("seeding roles")
                roles_to_insert = [
                    Role(name="admin"),
                    Role(name="careseeker"),
                    Role(name="caregiver"),
                ]
                db.add_all(roles_to_insert)
                await db.commit()

            # Seed specialties
            logger.info("checking specialties")
            get_specialties_statement = select(Specialty)
            result = await db.execute(get_specialties_statement)
            existing_specialties = list(result.scalars().all())

            if len(existing_specialties) == 0:
                logger.info("seeding specialties")
                specialties_to_insert = [
                    Specialty(
                        category=SpecialtyCategoryEnum.CHILD_CARE,
                        description="Child care",
                    ),
                    Specialty(
                        category=SpecialtyCategoryEnum.SENIOR_CARE,
                        description="Senior care",
                    ),
                    Specialty(
                        category=SpecialtyCategoryEnum.HOUSEKEEPING,
                        description="Housekeeping",
                    ),
                    Specialty(
                        category=SpecialtyCategoryEnum.PET_CARE,
                        description="Pet care",
                    ),
                    Specialty(
                        category=SpecialtyCategoryEnum.TUTORING,
                        description="Tutoring",
                    ),
                    Specialty(
                        category=SpecialtyCategoryEnum.OTHER, description="Other"
                    ),
                ]
                db.add_all(specialties_to_insert)
                await db.commit()

            logger.info("seeding complete")
        except Exception as e:
            await db.rollback()
            logger.exception(f"Error seeding database: {e}")
            raise

    yield

    logger.info("shutting down")


app = FastAPI(lifespan=lifespan, root_path="/api")


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = perf_counter()

    logger.info(f"Request: {request.method} {request.url.path}")

    response = await call_next(request)

    elapsed_ms = (perf_counter() - start) * 1000
    logger.info(
        f"Response: {request.method} {request.url.path} "
        + f"Status: {response.status_code} Duration: {elapsed_ms:.2f}ms"
    )

    return response


origins = [base_settings.base_url]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/healthcheck")
def read_root():
    return {"Hello": "World"}


@app.get("/scalar", include_in_schema=False)
async def scalar_html():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        scalar_proxy_url="https://proxy.scalar.com",
        title="Millennicare API docs",
    )


app.include_router(auth_router)
app.include_router(user_router)
app.include_router(waitlist_router)
app.include_router(contact_router)
