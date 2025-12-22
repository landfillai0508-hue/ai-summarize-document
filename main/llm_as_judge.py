"""llm_as_judge."""

import os
from abc import ABC, abstractmethod

from jinja2 import Environment, FileSystemLoader
from openai import AsyncOpenAI
from pydantic import BaseModel, Field

from main.document import Document
from main.report import Report

__all__ = [
    "Judgement",
    "Reference",
    "Statement",
    "ReferenceBasedJudge",
    "ReferenceBasedCorrectnessJudge",
    "Topic",
    "MainTopicExtractor",
    "TopicBasedCompletenessJudge",
]

ABSOLUTE_PATH = os.path.dirname(__file__)
ROOT_SOURCE_PATH = "/".join(ABSOLUTE_PATH.split("/")[:-1])


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

    _env = Environment(loader=FileSystemLoader(f"{ROOT_SOURCE_PATH}/prompts/templates"))
    _prompt_template_file = "judge_statement_correctness_template.j2"

    def __init__(self, client: AsyncOpenAI, model: str):
        self._llm_api_client = client
        self._model = model
        self._prompt_template = ReferenceBasedCorrectnessJudge._env.get_template(
            ReferenceBasedCorrectnessJudge._prompt_template_file
        )

    async def run(self, statement: Statement, reference: Reference) -> Judgement:
        prompt = self._prompt_template.render(
            {
                "statement": statement.content,
                "document": reference.content,
            }
        )

        response = await self._llm_api_client.beta.chat.completions.parse(
            model=self._model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant"},
                {"role": "user", "content": f"{prompt}"},
            ],
            response_format=Judgement,
        )

        judgement = Judgement.model_validate_json(response.choices[0].message.content)
        return judgement


class Topic(BaseModel):
    content: str = Field(..., description="The main idea of the document")


class MainTopicExtractor:
    _env = Environment(loader=FileSystemLoader(f"{ROOT_SOURCE_PATH}/prompts/templates"))
    _prompt_template_file = "extract_main_topic_template.j2"

    def __init__(self, client: AsyncOpenAI, model: str):
        self._llm_api_client = client
        self._model = model
        self._prompt_template = MainTopicExtractor._env.get_template(
            MainTopicExtractor._prompt_template_file
        )

    async def run(self, document: Document) -> Topic:
        prompt = self._prompt_template.render(
            {
                "document": document.content,
            }
        )

        response = await self._llm_api_client.beta.chat.completions.parse(
            model=self._model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant"},
                {"role": "user", "content": f"{prompt}"},
            ],
            response_format=Topic,
        )

        main_topic = Topic.model_validate_json(response.choices[0].message.content)
        return main_topic


class TopicBasedJudge(ABC):

    @abstractmethod
    async def run(self, topic: Topic, report: Report) -> Judgement:
        """Judge if a report is True or False based on given topic."""


class TopicBasedCompletenessJudge(TopicBasedJudge):
    _env = Environment(loader=FileSystemLoader(f"{ROOT_SOURCE_PATH}/prompts/templates"))
    _prompt_template_file = "judge_report_completeness_template.j2"

    def __init__(self, client: AsyncOpenAI, model: str):
        self._llm_api_client = client
        self._model = model
        self._prompt_template = TopicBasedCompletenessJudge._env.get_template(
            TopicBasedCompletenessJudge._prompt_template_file
        )

    async def run(self, topic: Topic, report: Report) -> Judgement:
        prompt = self._prompt_template.render(
            {
                "report": report.content,
                "topic": topic.content,
            }
        )

        response = await self._llm_api_client.beta.chat.completions.parse(
            model=self._model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant"},
                {"role": "user", "content": f"{prompt}"},
            ],
            response_format=Judgement,
        )

        judgement = Judgement.model_validate_json(response.choices[0].message.content)
        return judgement
