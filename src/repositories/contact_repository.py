from src.core.deps import T_Database


class ContactRepository:
    def __init__(self, db: T_Database):
        self.db = db
