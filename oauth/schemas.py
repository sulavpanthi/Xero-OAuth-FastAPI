from uuid import UUID

from pydantic import BaseModel


class UserOAuthTokenBaseSchema(BaseModel):
    id: UUID
    name: str | None
    phone_number: str | None
    email: str | None
    access_token: str | None
    refresh_token: str | None
