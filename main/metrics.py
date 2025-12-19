"""metrics module"""

import asyncio
from abc import ABC, abstractmethod
from functools import partial

from main.document import Document
from main.llm_as_judge import (
    Judgement,
    MainTopicExtractor,
    Reference,
    ReferenceBasedCorrectnessJudge,
    Statement,
    TopicBasedCompletenessJudge,
)
from main.report import Report

__all__ = [
    "Metric",
    "MetricExtractor",
    "HasTitleMetricExtractor",
    "TitleLengthMetricExtractor",
    "NumberOfParagraphMetricExtractor",
    "NumberOfTokenMetricExtractor",
    "CorrectnessMetricExtractor",
    "CompletenessMetricExtractor",
]


class Metric:

    def __init__(self, name: str, value: str):
        self._name = name
        self._value = value

    @property
    def name(self) -> str:
        return self._name

    @property
    def value(self) -> str:
        return self._value

    def __eq__(self, other) -> bool:
        return all(
            (
                isinstance(other, Metric),
                self.name == other.name,
                self.value == other.value,
            )
        )

    def __hash__(self) -> int:
        return hash(self.value)


class MetricExtractor(ABC):

    @abstractmethod
    def extract(self, report: Report) -> Metric:
        pass


class HasTitleMetricExtractor(MetricExtractor):

    def extract(self, report: Report) -> Metric:
        has_title = bool(report.title)
        value = str(int(has_title))
        return Metric(name="Has-Title-Metric", value=value)


class TitleLengthMetricExtractor(MetricExtractor):

    def extract(self, report: Report) -> Metric:
        num_of_char = len(report.title.strip())
        value = str(num_of_char)
        return Metric(name="Number-Of-Chars-In-Title-Metric", value=value)


class NumberOfParagraphMetricExtractor(MetricExtractor):

    def extract(self, report: Report) -> Metric:
        paragraphs = report.content.strip().split("\n\n")
        value = str(len(paragraphs))
        return Metric(name="Number-Of-Paragraphs-Metric", value=value)


class NumberOfTokenMetricExtractor(MetricExtractor):

    def extract(self, report: Report) -> Metric:
        tokens = report.content.strip().split()
        value = str(len(tokens))
        return Metric(name="Number-Of-Tokens-Metric", value=value)


class CorrectnessMetricExtractor(MetricExtractor):
    def __init__(self, reference: Reference):
        self._judge = partial(ReferenceBasedCorrectnessJudge().run, reference=reference)

    async def extract(self, report: Report) -> Metric:
        statements = [
            Statement(content=statement.strip())
            for statement in report.content.split("\n\n")  # NOTE: each paragraph is treated as a statement
            if statement.strip()
        ]
        judgements = await asyncio.gather(
            *[self._judge(statement=statement) for statement in statements]
        )
        is_all_statement_true: bool = all(
            judgement.decision for judgement in judgements
        )
        value = str(int(is_all_statement_true))
        return Metric(name="Correctness-Metric", value=value)


class CompletenessMetricExtractor(MetricExtractor):

    def __init__(self, reference: Reference):
        self._reference = reference
        self._main_idea_extractor = MainTopicExtractor()
        self._judge = TopicBasedCompletenessJudge()

    async def extract(self, report: Report) -> Metric:
        main_topic = await self._main_idea_extractor.run(
            document=Document(content=self._reference.content)
        )
        judgement = await self._judge.run(topic=main_topic, report=report)
        value = str(int(judgement.decision))
        return Metric(name="Completeness-Metric", value=value)
