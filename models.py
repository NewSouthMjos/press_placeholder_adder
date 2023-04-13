from dataclasses import dataclass,  field
from urllib import parse


@dataclass
class Post:
    id: int = field(init=False)
    title: str
    edit_url: str
    date_str: str
    category: str

    def __post_init__(self) -> None:
        self.id = int(
            parse.parse_qs(parse.urlparse(self.edit_url).query)['post'][0]
        )


@dataclass
class Placeholder:
    text: str
    symbols_count: int
