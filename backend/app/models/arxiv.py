from pydantic import BaseModel
from enum import Enum
from arxiv import Search, Result
from typing import Optional


class VectorizationStatus(Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class ArxivPaper(BaseModel):
    id: str

    @property
    def id_safe_for_path(self) -> str:
        return self.id.replace("/", "-").replace(".", "-")

    @property
    def url(self) -> str:
        return f"https://arxiv.org/abs/{self.id}"

    @property
    def pdf_url(self) -> Optional[str]:
        paper = self._find_paper()
        if paper is None:
            return None
        return paper.pdf_url

    def _find_paper(self) -> Optional[Result]:
        result = Search(id=self.id).results()
        paper = next(result, None)
        if paper is None:
            return None
        return paper
