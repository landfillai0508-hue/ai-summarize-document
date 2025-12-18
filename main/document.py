"""document module."""

from pprint import pprint

from pydantic import BaseModel

__all__ = [
    "Document",
]


class Document(BaseModel):
    content: str

    def pprint(self) -> None:
        pprint(self.content)

    @classmethod
    def load_from_local(cls, input_file_path: str) -> "Document":
        with open(input_file_path, "r") as in_file_obj:
            content = in_file_obj.read()
            return cls(content=content)
