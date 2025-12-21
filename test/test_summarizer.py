import asyncio
import os
import unittest

from openai import AsyncOpenAI

from main.document import Document
from main.summarizer import BestHitLLMSummarizer


class TestBestHitLLMSummarizer(unittest.TestCase):

    def setUp(self):
        input_file_path = os.path.join("data", "article.txt")
        self.document = Document.load_from_local(input_file_path=input_file_path)

    def test_open_sourced_deepseek_summarize(self):
        deepseek_client = AsyncOpenAI(
            base_url="http://localhost:11434/v1", api_key="dummy_key"
        )
        model = "deepseek-r1:8b"
        self._summarizer = BestHitLLMSummarizer(
            client=deepseek_client, model=model, llm_as_judge=False
        )

        report = asyncio.run(self._summarizer.summarize(document=self.document))
        print(report)

    def test_open_sourced_qwen_summarize(self):
        deepseek_client = AsyncOpenAI(
            base_url="http://localhost:11434/v1", api_key="dummy_key"
        )
        model = "qwen3-vl:8b"
        self._summarizer = BestHitLLMSummarizer(
            client=deepseek_client, model=model, llm_as_judge=False
        )

        report = asyncio.run(self._summarizer.summarize(document=self.document))
        print(report)
