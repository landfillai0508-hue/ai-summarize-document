import asyncio
import unittest

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


class TestHasTitleRequirement(unittest.TestCase):

    def setUp(self) -> None:
        self.requirement = HasTitleRequirement(must_be_satisfied=True)
        self.report = Report(title="UCLA", content="UCLA is a public university at LA.")

    def test_name(self) -> None:
        self.assertEqual(self.requirement.name, "Has-Title-Requirement")

    def test_description(self) -> None:
        self.assertEqual(
            self.requirement.description,
            "Include a title that tells readers exactly what the document is about;",
        )

    def test_must_be_satisfied(self) -> None:
        self.assertTrue(self.requirement.must_be_satisfied())

    def test_is_satisfied(self) -> None:
        self.assertTrue(self.requirement.is_satisfied(report=self.report))


class TestTitleLengthRequirement(unittest.TestCase):

    def setUp(self) -> None:
        self.requirement = TitleLengthRequirement(
            min_num_of_char=4, max_num_of_char=64, must_be_satisfied=True
        )
        self.report = Report(title="UCLA", content="UCLA is a public university at LA.")

    def test_name(self) -> None:
        self.assertEqual(self.requirement.name, "Title-Length-Requirement")

    def test_description(self) -> None:
        self.assertEqual(
            self.requirement.description,
            (
                f"Title must be: (1) longer than 4 characters and (2) shorter than "
                f"64 characters;"
            ),
        )

    def test_must_be_satisfied(self) -> None:
        self.assertTrue(self.requirement.must_be_satisfied())

    def test_is_satisfied(self) -> None:
        self.assertTrue(self.requirement.is_satisfied(report=self.report))


class TestDoubleNewlineDelimiterRequirement(unittest.TestCase):

    def setUp(self) -> None:
        self.requirement = DoubleNewlineDelimiterRequirement()
        self.report = Report(
            title="UCLA",
            content="UCLA is a public university at LA.\n\n"
            "UCLA is a public university at LA.",
        )

    def test_name(self) -> None:
        self.assertEqual(
            self.requirement.name, "Double-Newline-As-Paragraph-Delimiter-Requirement"
        )

    def test_description(self) -> None:
        self.assertEqual(
            self.requirement.description,
            ('Use "\n\n" as the delimiter to separate paragraphs;'),
        )

    def test_must_be_satisfied(self) -> None:
        self.assertFalse(self.requirement.must_be_satisfied())

    def test_is_satisfied(self) -> None:
        self.assertTrue(self.requirement.is_satisfied(report=self.report))


class TestNumberOfParagraphRequirement(unittest.TestCase):

    def setUp(self) -> None:
        self.requirement = NumberOfParagraphRequirement(
            min_num_of_paragraph=2, max_num_of_paragraph=5, must_be_satisfied=True
        )
        self.report = Report(
            title="UCLA",
            content="UCLA is a public university at LA.\n\n"
            "UCLA is a public university at LA.",
        )

    def test_name(self) -> None:
        self.assertEqual(self.requirement.name, "Number-Of-Paragraphs-Requirement")

    def test_description(self) -> None:
        self.assertEqual(
            self.requirement.description,
            ("Summarization report should have 2 to 5 paragraphs in total;"),
        )

    def test_must_be_satisfied(self) -> None:
        self.assertTrue(self.requirement.must_be_satisfied())

    def test_is_satisfied(self) -> None:
        self.assertTrue(self.requirement.is_satisfied(report=self.report))


class TestNumberOfTokenRequirement(unittest.TestCase):

    def setUp(self) -> None:
        self.requirement = NumberOfTokenRequirement(
            min_num_of_token=5, max_num_of_token=30, must_be_satisfied=True
        )
        self.report = Report(
            title="UCLA",
            content="UCLA is a public university at LA.\n\n"
            "UCLA is a public university at LA.",
        )

    def test_name(self) -> None:
        self.assertEqual(self.requirement.name, "Number-Of-Tokens-Requirement")

    def test_description(self) -> None:
        self.assertEqual(
            self.requirement.description,
            (f"Summarization report should have 5 to 30 tokens / words in total;"),
        )

    def test_must_be_satisfied(self) -> None:
        self.assertTrue(self.requirement.must_be_satisfied())

    def test_is_satisfied(self) -> None:
        self.assertTrue(self.requirement.is_satisfied(report=self.report))


class TestCorrectnessRequirement(unittest.TestCase):

    def setUp(self) -> None:
        self.report = Report(
            title="UCLA",
            content="UCLA is a public university",
        )
        self.document = Document(
            content="UCLA (University of California, Los Angeles) is a large, "
            "prestigious public research university located in the Westwood area of "
            "Los Angeles, California, known for its strong academics, successful "
            "athletics (now in the Big Ten), and significant impact on society, "
            "consistently ranking among the top public universities nationally."
        )

        self.requirement = CorrectnessRequirement(
            org_document=self.document, must_be_satisfied=True
        )

    def test_name(self) -> None:
        self.assertEqual(self.requirement.name, "Correctness-Requirement")

    def test_description(self) -> None:
        self.assertEqual(
            self.requirement.description,
            (
                "Ensure the summary faithfully reflects the original document meaning without "
                "adding personal opinions;"
            ),
        )

    def test_must_be_satisfied(self) -> None:
        self.assertTrue(self.requirement.must_be_satisfied())

    def test_is_satisfied(self) -> None:
        self.assertTrue(asyncio.run(self.requirement.is_satisfied(report=self.report)))


class TestCompletenessRequirement(unittest.TestCase):
    def setUp(self) -> None:
        self.report = Report(
            title="UCLA",
            content="UCLA (University of California, Los Angeles) is a large, "
            "prestigious public research university located in the Westwood area of "
            "Los Angeles, California, known for its strong academics, successful "
            "athletics (now in the Big Ten), and significant impact on society, "
            "consistently ranking among the top public universities nationally.",
        )
        self.document = Document(
            content="UCLA (University of California, Los Angeles) is a large, "
            "prestigious public research university located in the Westwood area of "
            "Los Angeles, California, known for its strong academics, successful "
            "athletics (now in the Big Ten), and significant impact on society, "
            "consistently ranking among the top public universities nationally."
        )

        self.requirement = CompletenessRequirement(
            org_document=self.document, must_be_satisfied=True
        )

    def test_name(self) -> None:
        self.assertEqual(self.requirement.name, "Correctness-Requirement")

    def test_description(self) -> None:
        self.assertEqual(
            self.requirement.description,
            ("Ensure the summary cover the main idea of the document;"),
        )

    def test_must_be_satisfied(self) -> None:
        self.assertTrue(self.requirement.must_be_satisfied())

    def test_is_satisfied(self) -> None:
        self.assertTrue(asyncio.run(self.requirement.is_satisfied(report=self.report)))


if __name__ == "__main__":
    unittest.main()
