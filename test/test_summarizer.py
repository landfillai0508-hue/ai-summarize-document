import asyncio
import os
import unittest

from openai import AsyncOpenAI

from main.document import Document
from main.summarizer import BestHitLLMSummarizer


class TestBestHitLLMSummarizer(unittest.TestCase):

    def setUp(self):
        # Point the client to your local Ollama instance
        client = AsyncOpenAI(base_url="http://localhost:11434/v1", api_key="dummy_key")
        self._summarizer = BestHitLLMSummarizer(
            client=client, model="deepseek-r1:8b", llm_as_judge=True
        )

    def test_summarize(self):
        input_file_path = os.path.join("data", "article.txt")
        document = Document.load_from_local(input_file_path=input_file_path)
        report = asyncio.run(self._summarizer.summarize(document=document))
        print(report)
