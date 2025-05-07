from pydantic import BaseModel, Field
from datetime import datetime, timedelta, timezone
from uuid import uuid4


class OAuthState(BaseModel):
    text: str = Field(default_factory=lambda: str(uuid4()))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    expires_in: int = 60 * 10  # seconds

    @property
    def expired_at(self) -> datetime:
        return self.created_at + timedelta(seconds=self.expires_in)

    @property
    def is_expired(self) -> bool:
        return datetime.now(timezone.utc) > self.expired_at

    def match(self, state: str) -> bool:
        return self.text == state
