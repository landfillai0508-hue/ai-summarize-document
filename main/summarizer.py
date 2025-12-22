"""summarize document."""

import inspect
from abc import ABC, abstractmethod

from jinja2 import Environment, FileSystemLoader
from openai import AsyncOpenAI

from main.customized_exceptions import (
    LargeLanguageAPIError,
    NoReportSatisfyAllMustRequirements,
)
from main.document import Document
from main.llm_as_judge import Reference
from main.metrics import BertScoreMetricExtractor, RougeScoreMetricExtractor
from main.report import Report
from main.requirements import (
    CompletenessRequirement,
    CorrectnessRequirement,
    DoubleNewlineDelimiterRequirement,
    HasTitleRequirement,
    NumberOfParagraphRequirement,
    NumberOfTokenRequirement,
    TitleLengthRequirement,
)


class AbstractSummarizer(ABC):

    @abstractmethod
    async def summarize(self, document: Document) -> Report:
        pass


class BestHitLLMSummarizer(AbstractSummarizer):
    _env = Environment(loader=FileSystemLoader("prompts/templates"))
    _prompt_template_file = "summarize_document_template.j2"

    def __init__(
        self,
        client: AsyncOpenAI,
        model: str,
        has_title: bool = True,
        min_num_of_char_in_title: int = 5,
        max_num_of_char_in_title: int = 50,
        min_num_of_paragraph: int = 2,
        max_num_of_paragraph: int = 4,
        compression_rate: float = 0.2,
        num_tries: int = 5,
        llm_as_judge: bool = False,
    ):
        self._llm_api_client = client
        self._model = model
        self._has_title = has_title
        self._min_num_of_char_in_title = min_num_of_char_in_title
        self._max_num_of_char_in_title = max_num_of_char_in_title
        self._min_num_of_paragraph = min_num_of_paragraph
        self._max_num_of_paragraph = max_num_of_paragraph
        self._compression_rate = compression_rate
        self._num_tries = num_tries
        self._llm_as_judge = llm_as_judge
        self._prompt_template = BestHitLLMSummarizer._env.get_template(
            BestHitLLMSummarizer._prompt_template_file
        )

    async def summarize(self, document: Document) -> Report:
        num_of_token = len([_ for _ in document.content.split() if _.strip()])
        # Define requirements which should be satisfied
        all_requirements = []
        if self._has_title:
            all_requirements.append(HasTitleRequirement(must_be_satisfied=True))

        all_requirements.extend(
            [
                TitleLengthRequirement(
                    min_num_of_char=self._min_num_of_char_in_title,
                    max_num_of_char=self._max_num_of_char_in_title,
                    must_be_satisfied=True,
                ),
                DoubleNewlineDelimiterRequirement(),
                NumberOfParagraphRequirement(
                    min_num_of_paragraph=self._min_num_of_paragraph,
                    max_num_of_paragraph=self._max_num_of_paragraph,
                    must_be_satisfied=True,
                ),
                NumberOfTokenRequirement(
                    min_num_of_token=int(
                        max(self._compression_rate - 0.05, 0.1) * num_of_token
                    ),
                    max_num_of_token=int(
                        min(self._compression_rate + 0.05, 0.9) * num_of_token
                    ),
                    must_be_satisfied=True,
                ),
            ]
        )

        if self._llm_as_judge:
            all_requirements.extend(
                [
                    CorrectnessRequirement(
                        client=self._llm_api_client,
                        model=self._model,
                        org_document=document,
                        must_be_satisfied=True,
                    ),
                    CompletenessRequirement(
                        client=self._llm_api_client,
                        model=self._model,
                        org_document=document,
                        must_be_satisfied=True,
                    ),
                ]
            )

        scorers = [
            BertScoreMetricExtractor(reference=Reference(content=document.content)),
            RougeScoreMetricExtractor(reference=Reference(content=document.content)),
        ]

        must_be_satisfied_requirements = [
            req for req in all_requirements if req.must_be_satisfied()
        ]

        descriptions_in_all_requirements = []
        for requirement in all_requirements:
            descriptions_in_all_requirements.append(requirement.description)

        # Build the prompt
        prompt = self._prompt_template.render(
            {
                "document": document.content,
                "requirements": descriptions_in_all_requirements,
            }
        )

        messages = [
            {"role": "system", "content": "You are a helpful assistant"},
            {"role": "user", "content": f"{prompt}"},
        ]

        # Query LLM API
        reports = []
        for iteration in range(self._num_tries):
            print(f"Summarize at iteration {iteration}")
            try:
                response = await self._llm_api_client.beta.chat.completions.parse(
                    model=self._model,
                    messages=messages,
                    response_format=Report,
                )
            except Exception as e:
                print(e)
            else:
                report = Report.model_validate_json(response.choices[0].message.content)
                reports.append(report)

        valid_reports = []
        for report in reports:
            satisfy_all_must_requirements = []
            for req in must_be_satisfied_requirements:
                if inspect.iscoroutinefunction(req.is_satisfied):
                    satisfy_all_must_requirements.append(await req.is_satisfied(report))
                else:
                    satisfy_all_must_requirements.append(req.is_satisfied(report))

            if satisfy_all_must_requirements:
                valid_reports.append(report)

        if not reports:
            raise LargeLanguageAPIError()

        if not valid_reports:
            raise NoReportSatisfyAllMustRequirements()

        best_report_id = -1
        best_report_score = 0
        for idx, report in enumerate(valid_reports):
            scores = []
            for scorer in scorers:
                score = scorer.extract(report=report)
                scores.append(float(score.value))

            cur_report_score = sum(scores)  # sum scores of all scorers
            if cur_report_score > best_report_score:
                best_report_id = idx

        return valid_reports[best_report_id]
