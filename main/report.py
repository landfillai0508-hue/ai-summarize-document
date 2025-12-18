"""report module."""

from pydantic import BaseModel, Field


class Report(BaseModel):
    """summarization report"""

    title: str = Field(..., description="The title of the summarization report")

    content: str = Field(..., description="The content of the summarization report")
