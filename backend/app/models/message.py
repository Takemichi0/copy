import re
from datetime import datetime
from pydantic import BaseModel
from pytz import UTC, timezone
from typing import Optional

from ..utils.arxiv_extraction import arxiv_id_of
from ..utils.firebase import sanitize_for_firestore

class SlackThreadTimestamp(BaseModel):
    raw: str

    @property
    def as_firestore_path(self) -> str:
        return sanitize_for_firestore(self.raw)

    @property
    def as_float(self) -> float:
        return float(self.raw)

    @property
    def as_datetime(self) -> datetime:
        timestamp_float = float(self.raw)
        dt_utc = datetime.fromtimestamp(timestamp_float, tz=UTC)
        return dt_utc.astimezone(timezone('Asia/Tokyo'))


class SlackMessage(BaseModel):
    workspace_id: str
    slack_id: str
    channel_id: str
    thread_ts: SlackThreadTimestamp
    text: str

    @property
    def has_arxiv_id(self) -> bool:
        return self.arxiv_id is not None

    @property
    def arxiv_id(self) -> Optional[str]:
        return self._extract_arxiv_id()

    def _extract_arxiv_id(self) -> Optional[str]:
        url = self._extract_first_url_from_message(self.text)
        if url is None:
            return None
        return arxiv_id_of(url)

    def _extract_first_url_from_message(self, message: str) -> str:
        # Ref: https://api.slack.com/reference/surfaces/formatting#links-in-retrieved-messages
        regex = re.compile(
            r'<(http[s]?://[^>|]+)(?:|[^>]+)?>'
        )
        match = regex.search(message)
        if match:
            return match.group(1)
        return None


class SlackThread(BaseModel):
    messages: list[SlackMessage]

    @property
    def workspace_id(self) -> str:
        self._ensure_messages()
        return self.messages[0].workspace_id

    @property
    def channel_id(self) -> str:
        self._ensure_messages()
        return self.messages[0].channel_id

    @property
    def thread_ts(self) -> SlackThreadTimestamp:
        self._ensure_messages()
        return self.messages[0].thread_ts

    @property
    def arxiv_id(self) -> str:
        self._ensure_messages()
        if self.messages[0].arxiv_id is None:
            raise Exception("No arxiv_id")
        return self.messages[0].arxiv_id

    def messages_to_dict(self) -> list[dict]:
        return [message.model_dump() for message in self.messages]

    def requires_summary(self) -> bool:
        # 最初のメッセージに対しては必ず summary を返す
        return len(self.messages) == 1

    def _ensure_messages(self) -> None:
        if len(self.messages) == 0:
            raise Exception("No messages")
