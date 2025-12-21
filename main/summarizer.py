"""summarize document."""

import inspect
from abc import ABC, abstractmethod

from jinja2 import Environment, FileSystemLoader
from ollama import AsyncClient

from main.customized_exceptions import (
    LargeLanguageAPIError,
    NoReportSatisfyAllMustRequirements,
)
from main.document import Document
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

    def __init__(self, num_tries: int = 3):
        self._num_tries = num_tries
        self._ollama_client = AsyncClient()
        self._prompt_template = BestHitLLMSummarizer._env.get_template(
            BestHitLLMSummarizer._prompt_template_file
        )

    async def summarize(self, document: Document) -> Report:
        # Define requirements which should be satisfied
        all_requirements = [
            HasTitleRequirement(must_be_satisfied=True),
            TitleLengthRequirement(
                min_num_of_char=5, max_num_of_char=80, must_be_satisfied=True
            ),
            DoubleNewlineDelimiterRequirement(),
            NumberOfParagraphRequirement(
                min_num_of_paragraph=2, max_num_of_paragraph=4, must_be_satisfied=True
            ),
            NumberOfTokenRequirement(
                min_num_of_token=100, max_num_of_token=250, must_be_satisfied=True
            ),
            CorrectnessRequirement(org_document=document, must_be_satisfied=True),
            CompletenessRequirement(org_document=document, must_be_satisfied=True),
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
                response = await self._ollama_client.chat(
                    model="deepseek-r1:8b",
                    messages=messages,
                    format=Report.model_json_schema(),
                )
            except Exception as _:
                pass
            else:
                report = Report.model_validate_json(response.message.content)
                print("report:", report)
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

        return valid_reports[0]
