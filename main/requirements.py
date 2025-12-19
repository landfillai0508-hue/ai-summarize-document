"""requirements module"""

from abc import ABC, abstractmethod

from main.document import Document
from main.llm_as_judge import Reference
from main.metrics import (
    CompletenessMetricExtractor,
    CorrectnessMetricExtractor,
    HasTitleMetricExtractor,
    NumberOfParagraphMetricExtractor,
    NumberOfTokenMetricExtractor,
    TitleLengthMetricExtractor,
)
from main.report import Report

__all__ = [
    "Requirement",
    "HasTitleRequirement",
    "TitleLengthRequirement",
    "NumberOfParagraphRequirement",
    "NumberOfTokenRequirement",
    "CompletenessRequirement",
    "CorrectnessRequirement",
    "DoubleNewlineDelimiterRequirement",
]


class Requirement(ABC):

    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def description(self) -> str:
        pass

    @abstractmethod
    def is_satisfied(self, report: Report) -> bool:
        pass

    @abstractmethod
    def must_be_satisfied(self) -> bool:
        pass


class HasTitleRequirement(Requirement):

    def __init__(self, must_be_satisfied: bool = False):
        super().__init__()
        self._name = "Has-Title-Requirement"
        self._description = (
            "Include a title that tells readers exactly what the document is about;"
        )
        self._must_be_satisfied = must_be_satisfied
        self._metric_extractor = HasTitleMetricExtractor()

    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> str:
        return self._description

    def is_satisfied(self, report: Report) -> bool:
        metric = self._metric_extractor.extract(report)
        value = bool(int(metric.value))
        return value

    def must_be_satisfied(self) -> bool:
        return self._must_be_satisfied


class TitleLengthRequirement(Requirement):

    def __init__(
        self,
        min_num_of_char: int,
        max_num_of_char: int,
        must_be_satisfied: bool = False,
    ):
        super().__init__()
        self._min_num_of_char = min_num_of_char
        self._max_num_of_char = max_num_of_char
        self._must_be_satisfied = must_be_satisfied
        self._name = "Title-Length-Requirement"
        self._description = (
            f"Title must be: (1) longer than {self._min_num_of_char} characters and (2) shorter than "
            f"{self._max_num_of_char} characters;"
        )
        self._metric_extractor = TitleLengthMetricExtractor()

    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> str:
        return self._description

    def is_satisfied(self, report: Report) -> bool:
        metric = self._metric_extractor.extract(report)
        num_of_char_in_title = int(metric.value)
        is_title_length_proper = (
            self._min_num_of_char <= num_of_char_in_title <= self._max_num_of_char
        )
        return is_title_length_proper

    def must_be_satisfied(self) -> bool:
        return self._must_be_satisfied


class DoubleNewlineDelimiterRequirement(Requirement):

    def __init__(self):
        super().__init__()
        self._name = "Double-Newline-As-Paragraph-Delimiter-Requirement"
        self._paragraph_delimiter = "\n\n"
        self._description = f'Use "{self._paragraph_delimiter}" as the delimiter to separate paragraphs;'

    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> str:
        return self._description

    def is_satisfied(self, report: Report) -> bool:
        return True

    def must_be_satisfied(self) -> bool:
        return False


class NumberOfParagraphRequirement(Requirement):

    def __init__(
        self,
        min_num_of_paragraph: int,
        max_num_of_paragraph: int,
        must_be_satisfied: bool = False,
    ):
        super().__init__()
        self._min_num_of_paragraph = min_num_of_paragraph
        self._max_num_of_paragraph = max_num_of_paragraph
        self._must_be_satisfied = must_be_satisfied
        self._name = "Number-Of-Paragraphs-Requirement"
        self._description = (
            f"Summarization report should have {self._min_num_of_paragraph} to {self._max_num_of_paragraph} paragraphs "
            f"in total;"
        )
        self._metric_extractor = NumberOfParagraphMetricExtractor()

    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> str:
        return self._description

    def is_satisfied(self, report: Report) -> bool:
        metric = self._metric_extractor.extract(report)
        num_of_paragraph = int(metric.value)
        has_proper_num_of_paragraph = (
            self._min_num_of_paragraph <= num_of_paragraph <= self._max_num_of_paragraph
        )
        return has_proper_num_of_paragraph

    def must_be_satisfied(self) -> bool:
        return self._must_be_satisfied


class NumberOfTokenRequirement(Requirement):

    def __init__(
        self,
        min_num_of_token: int,
        max_num_of_token: int,
        must_be_satisfied: bool = False,
    ):
        super().__init__()
        self._min_num_of_token = min_num_of_token
        self._max_num_of_token = max_num_of_token
        self._must_be_satisfied = must_be_satisfied
        self._name = "Number-Of-Tokens-Requirement"
        self._description = (
            f"Summarization report should have {self._min_num_of_token} to {self._max_num_of_token} tokens / words "
            f"in total;"
        )
        self._metric_extractor = NumberOfTokenMetricExtractor()

    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> str:
        return self._description

    def is_satisfied(self, report: Report) -> bool:
        metric = self._metric_extractor.extract(report)
        num_of_token = int(metric.value)
        has_proper_num_of_token = (
            self._min_num_of_token <= num_of_token <= self._max_num_of_token
        )
        return has_proper_num_of_token

    def must_be_satisfied(self) -> bool:
        return self._must_be_satisfied


class CorrectnessRequirement(Requirement):

    def __init__(self, org_document: Document, must_be_satisfied: bool = False):
        self._must_be_satisfied = must_be_satisfied
        self._name = "Correctness-Requirement"
        self._description = (
            "Ensure the summary faithfully reflects the original document meaning without "
            "adding personal opinions;"
        )
        self._reference = Reference(content=org_document.content)
        self._metric_extractor = CorrectnessMetricExtractor(reference=self._reference)

    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> str:
        return self._description

    async def is_satisfied(self, report: Report) -> bool:
        metric = await self._metric_extractor.extract(report)
        is_correct = bool(int(metric.value))
        return is_correct

    def must_be_satisfied(self) -> bool:
        return self._must_be_satisfied


class CompletenessRequirement(Requirement):

    def __init__(self, org_document: Document, must_be_satisfied: bool = False):
        self._must_be_satisfied = must_be_satisfied
        self._name = "Correctness-Requirement"
        self._description = "Ensure the summary cover the main idea of the document;"
        self._reference = Reference(content=org_document.content)
        self._metric_extractor = CompletenessMetricExtractor(reference=self._reference)

    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> str:
        return self._description

    async def is_satisfied(self, report: Report) -> bool:
        metric = await self._metric_extractor.extract(report)
        is_correct = bool(int(metric.value))
        return is_correct

    def must_be_satisfied(self) -> bool:
        return self._must_be_satisfied
