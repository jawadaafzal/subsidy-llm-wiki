from datetime import date
from typing import Literal

from pydantic import BaseModel, Field


class WikiPage(BaseModel):
    title: str
    page_type: Literal["source", "concept", "entity", "draft"]
    status: Literal["draft", "reviewed", "published"]

    created: date
    updated: date

    sources: list[str] = Field(default_factory=list)

    summary: str
    main_content: str
    key_facts: list[str] = Field(default_factory=list)
    evidence: list[str] = Field(default_factory=list)
    related_pages: list[str] = Field(default_factory=list)