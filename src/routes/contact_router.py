from http import HTTPStatus
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Path, Query

from src.core.dependencies.contact_dependencies import T_ContactDeps
from src.schemas.contact_schemas import ContactSchema, CreateContactSchema

router = APIRouter(tags=["contact"], prefix="/contacts")


@router.post("/", status_code=HTTPStatus.CREATED, response_model=ContactSchema)
async def create_contact(body: CreateContactSchema, deps: T_ContactDeps):
    return await deps.service.create_contact(body)

@router.get("/{id}", status_code=HTTPStatus.OK, response_model=ContactSchema)
async def get_contact(id: Annotated[UUID, Path(description="The id of the contact")], deps: T_ContactDeps):
    return await deps.service.get_contact_by_id(contact_id=id)

@router.get("", status_code=HTTPStatus.OK, response_model=list[ContactSchema])
async def get_contacts(deps: T_ContactDeps, skip: int = Query(0, ge=0), limit: int = Query(100, le=100)):
    return await deps.service.get_contacts(skip=skip, limit=limit)
