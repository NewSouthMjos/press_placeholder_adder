from dataclasses import dataclass


@dataclass
class Post:
    title: str
    edit_url: str
    date_str: str
    category: str
