from src.repositories.waitlist_repository import WaitlistRepository
from src.schemas.waitlist_schemas import CreateWaitlistSchema, WaitlistSchema


class WaitlistService:
    def __init__(self, waitlist_repository: WaitlistRepository):
        self.waitlist_repository = waitlist_repository

    async def create_waitlist(self, body: CreateWaitlistSchema) -> WaitlistSchema:
        existing_waitlist = await self.waitlist_repository.get_waitlist_by_email(
            body.email
        )
        if existing_waitlist:
            return WaitlistSchema.model_validate(existing_waitlist)

        waitlist = await self.waitlist_repository.create_waitlist(body)
        return WaitlistSchema.model_validate(waitlist)
