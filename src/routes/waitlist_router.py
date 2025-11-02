from http import HTTPStatus

from fastapi import APIRouter

from src.core.dependencies.waitlist_dependencies import T_WaitlistDeps
from src.schemas.waitlist_schemas import CreateWaitlistSchema, WaitlistSchema

router = APIRouter(tags=["waitlist"], prefix="/waitlists")


@router.post("/", status_code=HTTPStatus.CREATED, response_model=WaitlistSchema)
async def create_waitlist(body: CreateWaitlistSchema, deps: T_WaitlistDeps):
    return await deps.service.create_waitlist(body)
