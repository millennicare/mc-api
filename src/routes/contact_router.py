from http import HTTPStatus

from fastapi import APIRouter

from src.core.dependencies.contact_dependencies import T_ContactDeps
from src.schemas.contact_schemas import ContactSchema, CreateContactSchema

router = APIRouter(tags=["contacts"], prefix="/contacts")


@router.post("/", status_code=HTTPStatus.CREATED, response_model=ContactSchema)
async def create_contact(body: CreateContactSchema, deps: T_ContactDeps):
    pass
