from __future__ import annotations
from dataclasses import dataclass


@dataclass
class Post:
    id: int
    title: str
    date: str
    status: str
    categories: list[int]
    initial_content_raw: str
    result_content_raw: str | None = None

    @classmethod
    def parse_json_post(cls, post_json: dict) -> Post:
        return cls(
            post_json.get("id"),
            post_json.get("title").get("rendered"),
            post_json.get("date"),
            post_json.get("status"),
            post_json.get("categories"),
            post_json.get("content").get("raw"),
        )


@dataclass
class Placeholder:
    text: str
    symbols_count: int
