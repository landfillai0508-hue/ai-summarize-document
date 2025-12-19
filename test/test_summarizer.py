import asyncio
import os
import unittest

from main.document import Document
from main.summarizer import BestHitLLMSummarizer


class TestBestHitLLMSummarizer(unittest.TestCase):

    def setUp(self):
        self._summarizer = BestHitLLMSummarizer()

    def test_summarize(self):
        input_file_path = os.path.join("data", "article.txt")
        document = Document.load_from_local(input_file_path=input_file_path)
        report = asyncio.run(self._summarizer.summarize(document=document))
        print(report)
