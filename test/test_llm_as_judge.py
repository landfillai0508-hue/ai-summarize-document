import asyncio
import unittest
from unittest.mock import patch

from main.document import Document
from main.llm_as_judge import (
    Judgement,
    MainTopicExtractor,
    Reference,
    ReferenceBasedCorrectnessJudge,
    Report,
    Statement,
    Topic,
    TopicBasedCompletenessJudge,
)


class TestJudgement(unittest.TestCase):

    def setUp(self) -> None:
        self.judgement = Judgement(
            decision=True,
            reason="The referred document explicitly mentioned UCLA is a public university",
        )

    def test_decision(self) -> None:
        self.assertEqual(self.judgement.decision, True)

    def test_reason(self) -> None:
        self.assertEqual(
            self.judgement.reason,
            "The referred document explicitly mentioned UCLA is a public university",
        )


class TestReference(unittest.TestCase):
    def setUp(self) -> None:
        self.reference = Reference(
            content="UCLA (University of California, Los Angeles) is a large, prestigious public research "
            "university located in the Westwood area of Los Angeles, California, known for "
            "its strong academics, successful athletics (now in the Big Ten), and significant "
            "impact on society, consistently ranking among the top public universities nationally."
        )

    def test_document(self) -> None:
        self.assertEqual(
            self.reference.content,
            "UCLA (University of California, Los Angeles) is a large, prestigious public research "
            "university located in the Westwood area of Los Angeles, California, known for "
            "its strong academics, successful athletics (now in the Big Ten), and significant impact "
            "on society, consistently ranking among the top public universities nationally.",
        )


class TestStatement(unittest.TestCase):

    def setUp(self) -> None:
        self.statement = Statement(
            content="UCLA is a public university",
        )

    def test_statement(self) -> None:
        self.assertEqual(self.statement.content, "UCLA is a public university")


class TestReferenceBasedCorrectnessJudge(unittest.TestCase):

    def setUp(self) -> None:
        self.statement = Statement(
            content="UCLA is a public university",
        )
        self.reference = Reference(
            content="UCLA (University of California, Los Angeles) is a large, "
            "prestigious public research university located in the Westwood area of "
            "Los Angeles, California, known for its strong academics, successful "
            "athletics (now in the Big Ten), and significant impact on society, "
            "consistently ranking among the top public universities nationally."
        )
        self.judge = ReferenceBasedCorrectnessJudge()

    def test_run(self) -> None:
        judgement = asyncio.run(
            self.judge.run(statement=self.statement, reference=self.reference)
        )
        self.assertEqual(judgement.decision, True)


class TestTopic(unittest.TestCase):
    def setUp(self) -> None:
        self.topic = Topic(
            content="UCLA is a public university",
        )

    def test_topic(self) -> None:
        self.assertEqual(self.topic.content, "UCLA is a public university")


class TestMainTopicExtractor(unittest.TestCase):
    def setUp(self) -> None:
        self.document = Document(
            content="UCLA (University of California, Los Angeles) is a large, "
            "prestigious public research university located in the Westwood area of "
            "Los Angeles, California, known for its strong academics, successful "
            "athletics (now in the Big Ten), and significant impact on society, "
            "consistently ranking among the top public universities nationally."
        )
        self.main_topic_extractor = MainTopicExtractor()

    def test_run(self):
        with patch(
            "main.llm_as_judge.MainTopicExtractor.run",
            new_callable=unittest.mock.AsyncMock,
        ) as mock_run:
            mock_run.return_value = Topic(content="UCLA is a public university")
            topic = asyncio.run(self.main_topic_extractor.run(document=self.document))
            self.assertEqual(topic.content, "UCLA is a public university")


class TestTopicBasedCompletenessJudge(unittest.TestCase):
    def setUp(self) -> None:
        self.topic = Topic(
            content="UCLA is a public university",
        )
        self.report = Report(
            title="UCLA",
            content="UCLA (University of California, Los Angeles) is a large, "
            "prestigious public research university located in the Westwood area of "
            "Los Angeles, California, known for its strong academics, successful "
            "athletics (now in the Big Ten), and significant impact on society, "
            "consistently ranking among the top public universities nationally.",
        )
        self.judge = TopicBasedCompletenessJudge()

    def test_run(self) -> None:
        judgement = asyncio.run(self.judge.run(topic=self.topic, report=self.report))
        self.assertEqual(judgement.decision, True)


if __name__ == "__main__":
    unittest.main()
