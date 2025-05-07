from time import time
from typing import Callable, Awaitable, Any

from pydantic import BaseModel


def _make_blocks(url_list: [str]) -> list[dict[str, str]]:
    blocks = [{"type": "image", "image_url": url, "alt_text": "image description"} for url in url_list]
    return blocks


class ReplyCallback(BaseModel):
    IN_PROGRESS_SUFFIX: str = "……"
    # Message update は Tier 3 であるため Workspace あたり 50+ per/minute となる
    # そのため各 instance あたり同時実行も考慮した rate limit を設ける
    # Ref: https://api.slack.com/docs/rate-limits
    SENDING_LIMIT_PER_MINUTE: int = 20

    text: str = ""
    interval: float = 60 / SENDING_LIMIT_PER_MINUTE
    last_sent_at: float = 0
    sent_message_ts: str = ""
    adding_blocks_callback: Callable[[list[dict[str, str]]], Awaitable]
    adding_message_callback: Callable[[str], Awaitable]
    updating_message_callback: Callable[[str, str], Awaitable]
    image_url: list[str] = []
    image_blocks: list[dict[str, str]] = []

    def set_images(self, urls: [str]) -> None:
        self.image_blocks = _make_blocks(urls)

    def has_images(self) -> bool:
        return len(self.image_blocks) > 0

    async def show_images(self) -> None:
        await self.adding_blocks_callback(self.image_blocks)

    async def add_token(self, token: str) -> None:
        self.text += token
        text_with_suffix = f"{self.text}{self.IN_PROGRESS_SUFFIX}"
        if self.sent_message_ts == "":
            response = await self.adding_message_callback(text_with_suffix)
            self.sent_message_ts = response["ts"]
        elif not self._is_over_limit():
            await self.updating_message_callback(text_with_suffix, self.sent_message_ts)
            self.last_sent_at = time()

    async def finish(self) -> None:
        await self.updating_message_callback(self.text, self.sent_message_ts)

    def _is_over_limit(self) -> bool:
        return time() - self.last_sent_at < self.interval
