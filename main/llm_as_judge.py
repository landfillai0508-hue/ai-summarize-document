"""llm_as_judge."""

from abc import ABC, abstractmethod
from string import Template

from ollama import AsyncClient
from pydantic import BaseModel, Field

from main.document import Document
from main.report import Report


class Judgement(BaseModel):
    decision: bool = Field(
        ..., description="A decision if the statement is True or False"
    )
    reason: str = Field(..., description="The reason to justify your decision")


class Reference(BaseModel):
    content: str


class Statement(BaseModel):
    content: str


class ReferenceBasedJudge(ABC):

    @abstractmethod
    async def run(self, statement: Statement, reference: Reference) -> Judgement:
        """Judge if a statement is True or False based on a given reference."""


class ReferenceBasedCorrectnessJudge(ReferenceBasedJudge):
    """Judge if a statement is True or False by a given reference."""

    def __init__(self):
        self._ollama_client = AsyncClient()
        self._prompt_template = Template(
            "Read the document as reference:"
            "\n"
            "    $document"
            "\n\n"
            "Judge if the following statement is True or False:"
            "\n"
            "    $statement"
        )

    async def run(self, statement: Statement, reference: Reference) -> Judgement:
        prompt = self._prompt_template.substitute(
            {
                "statement": statement.content,
                "document": reference.content,
            }
        )

        response = await self._ollama_client.chat(
            model="deepseek-r1:8b",
            messages=[
                {"role": "system", "content": "You are a helpful assistant"},
                {"role": "user", "content": f"{prompt}"},
            ],
            format=Judgement.model_json_schema(),
        )

        judgement = Judgement.model_validate_json(response.message.content)
        return judgement


class Topic(BaseModel):
    content: str = Field(..., description="The main idea of the document")


class MainTopicExtractor:

    def __init__(self):
        self._ollama_client = AsyncClient()
        self._prompt_template = Template(
            "Extract the main idea of the following document:" "\n" "    $document"
        )

    async def run(self, document: Document) -> Topic:
        prompt = self._prompt_template.substitute(
            {
                "document": document.content,
            }
        )

        response = await self._ollama_client.chat(
            model="deepseek-r1:8b",
            messages=[
                {"role": "system", "content": "You are a helpful assistant"},
                {"role": "user", "content": f"{prompt}"},
            ],
            format=Topic.model_json_schema(),
        )

        main_topic = Topic.model_validate_json(response.message.content)
        return main_topic


class TopicBasedJudge(ABC):

    @abstractmethod
    async def run(self, topic: Topic, report: Report) -> Judgement:
        """Judge if a report is True or False based on given topic."""


class TopicBasedCompletenessJudge(TopicBasedJudge):

    def __init__(self):
        self._ollama_client = AsyncClient()
        self._prompt_template = Template(
            "Read the following summarization report:"
            "\n"
            "    $report"
            "\n"
            "Check if the summarization report above covers the following "
            "topic:"
            "\n"
            "    $topic"
        )

    async def run(self, topic: Topic, report: Report) -> Judgement:
        prompt = self._prompt_template.substitute(
            {
                "report": report.content,
                "topic": topic.content,
            }
        )

        response = await self._ollama_client.chat(
            model="deepseek-r1:8b",
            messages=[
                {"role": "system", "content": "You are a helpful assistant"},
                {"role": "user", "content": f"{prompt}"},
            ],
            format=Judgement.model_json_schema(),
        )

        judgement = Judgement.model_validate_json(response.message.content)
        return judgement
