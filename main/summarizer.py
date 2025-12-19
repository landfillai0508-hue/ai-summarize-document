"""summarize document."""

import pprint
from abc import ABC, abstractmethod
from concurrent import futures
from string import Template
from typing import List

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
    _prompt_prefix_template = Template(
        "Summarize the following document:"
        "\n"
        "    $document"
        "\n"
        "Requirements include:"
        "\n"
        "    $requirements"
    )

    def __init__(self, num_tries: int = 10):
        self._num_tries = num_tries
        self._ollama_client = AsyncClient()

    """
    @staticmethod
    def select_the_best_candidate_report(candidate_reports: List[ReportWithMetrics],
                                         details_logger: ExplanationLogger = ExplanationLogger()) -> Report:
        # Select reports which have maximal number of alert groups
        max_num_of_alert_groups = max(report.num_of_alert_groups for report in candidate_reports)
        reports_which_have_max_alert_groups = [report for report in candidate_reports
                                               if report.num_of_alert_groups == max_num_of_alert_groups]

        # Prefer reports which do not have summary paragraphs
        has_any_report_no_summary = any(
            report.no_summary_paragraph for report in reports_which_have_max_alert_groups
        )
        reports_with_best_no_summary = [report for report in reports_which_have_max_alert_groups
                                        if report.no_summary_paragraph == has_any_report_no_summary]

        # Prefer the report which has the least tokens / words
        reports_sorted_by_num_of_tokens = sorted(reports_with_best_no_summary, key=lambda x: x.num_of_tokens)

        excluded_reports = [report for report in candidate_reports if report not in reports_sorted_by_num_of_tokens]
        details_logger.log_matching_reports(reports_sorted_by_num_of_tokens, excluded_reports)

        return reports_sorted_by_num_of_tokens[0].report
    """

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

        req_desc_as_text = "\n".join(
            f"    - {desc}" for desc in descriptions_in_all_requirements
        )

        # Build the prompt
        prompt = self._prompt_prefix_template.substitute(
            {
                "document": document.content,
                "requirements": req_desc_as_text,
            }
        )
        messages = [
            {"role": "system", "content": "You are a helpful assistant"},
            {"role": "user", "content": f"{prompt}"},
        ]

        # Query LLM API
        reports = []
        for iter in range(self._num_tries):
            print(f"Summarize at iteration {iter}")
            response = await self._ollama_client.chat(
                model="deepseek-r1:8b",
                messages=messages,
                format=Report.model_json_schema(),
            )

            report = Report.model_validate_json(response.message.content)
            reports.append(report)

        valid_reports = []
        for report in reports:
            satisfy_all_must_requirements = all(
                req.is_satisfied(report) for req in must_be_satisfied_requirements
            )
            if satisfy_all_must_requirements:
                valid_reports.append(report)

        print(f"Number of valid reports: {len(valid_reports)}")

        return reports[0]

        """
        if not has_successful_return_from_llm:
            raise LargeLanguageAPIError()

        if not reports_satisfy_must_with_metrics:
            raise NoReportSatisfyAllMustRequirements()

        best_report = BestHitChatGPTSummarizer.select_the_best_candidate_report(reports_satisfy_must_with_metrics,
                                                                                self._explanation_logger)
        return best_report
        """


if __name__ == "__main__":
    import asyncio

    input_local_path_ = "../data/article.txt"
    document_ = Document.load_from_local(input_file_path=input_local_path_)
    best_hit_llm_summarizer_ = BestHitLLMSummarizer()
    report_ = asyncio.run(best_hit_llm_summarizer_.summarize(document=document_))
    print(report_)
