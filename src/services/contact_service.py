from src.repositories.contact_repository import ContactRepository


class ContactService:
    def __init__(self, contact_repository: ContactRepository):
        self.contact_repository = contact_repository
