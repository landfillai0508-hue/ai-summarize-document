import unittest

from main.llm_as_judge import Reference
from main.metrics import (
    CompletenessMetricExtractor,
    CorrectnessMetricExtractor,
    HasTitleMetricExtractor,
    Metric,
    NumberOfParagraphMetricExtractor,
    NumberOfTokenMetricExtractor,
    TitleLengthMetricExtractor,
)
from main.report import Report


class TestMetric(unittest.TestCase):

    def setUp(self) -> None:
        self.metric = Metric(name="Has-Title-Metric", value="1")

        self.metric_alternate = Metric(name="Has-Title-Metric", value="1")

    def test_name(self) -> None:
        self.assertEqual(self.metric.name, "Has-Title-Metric")

    def test_value(self) -> None:
        self.assertEqual(self.metric.value, "1")

    def test_equal(self) -> None:
        self.assertEqual(self.metric, self.metric_alternate)


class TestHasTitleMetricExtractor(unittest.TestCase):

    def setUp(self) -> None:
        self.no_title_report = Report(
            title="", content="UCLA is a public university at Los Angeles"
        )

        self.with_title_report = Report(
            title="UCLA", content="UCLA is a public university at Los Angeles"
        )

        self.metric_extractor = HasTitleMetricExtractor()

    def test_extract(self) -> None:
        on_no_title_report_metric = self.metric_extractor.extract(
            report=self.no_title_report
        )
        self.assertEqual(on_no_title_report_metric.name, "Has-Title-Metric")
        self.assertFalse(bool(int(on_no_title_report_metric.value)))

        on_with_title_report_metric = self.metric_extractor.extract(
            report=self.with_title_report
        )
        self.assertTrue(bool(int(on_with_title_report_metric.value)))


class TestTitleLengthMetricExtractor(unittest.TestCase):

    def setUp(self) -> None:
        self.report = Report(
            title="UCLA", content="UCLA is a public university at Los Angeles"
        )

        self.metric_extractor = TitleLengthMetricExtractor()

    def test_extract(self) -> None:
        title_length_metric = self.metric_extractor.extract(report=self.report)
        self.assertEqual(title_length_metric.name, "Number-Of-Chars-In-Title-Metric")
        self.assertEqual(title_length_metric.value, "4")


class TestNumberOfParagraphMetricExtractor(unittest.TestCase):

    def setUp(self) -> None:
        self.report = Report(
            title="UCLA",
            content="UCLA is a public university at Los Angeles.\n\n"
            "UCLA is a large research university located, known for its strong academics, "
            "successful athletics (now in the Big Ten), and significant impact on society.",
        )

        self.metric_extractor = NumberOfParagraphMetricExtractor()

    def test_extract(self) -> None:
        num_of_paragraph_metric = self.metric_extractor.extract(report=self.report)
        self.assertEqual(num_of_paragraph_metric.name, "Number-Of-Paragraphs-Metric")
        self.assertEqual(num_of_paragraph_metric.value, "2")


class TestNumberOfTokenMetricExtractor(unittest.TestCase):

    def setUp(self) -> None:
        self.report = Report(
            title="UCLA", content="UCLA is a public university at Los Angeles."
        )

        self.metric_extractor = NumberOfTokenMetricExtractor()

    def test_extract(self) -> None:
        num_of_token_metric = self.metric_extractor.extract(report=self.report)
        self.assertEqual(num_of_token_metric.name, "Number-Of-Tokens-Metric")
        self.assertEqual(num_of_token_metric.value, "8")


class TestCorrectnessMetricExtractor(unittest.TestCase):

    def setUp(self) -> None:
        self.report = Report(
            title="UCLA",
            content="UCLA is a public university",
        )
        self.reference = Reference(
            content="UCLA (University of California, Los Angeles) is a large, "
            "prestigious public research university located in the Westwood area of "
            "Los Angeles, California, known for its strong academics, successful "
            "athletics (now in the Big Ten), and significant impact on society, "
            "consistently ranking among the top public universities nationally."
        )

        self.metric_extractor = CorrectnessMetricExtractor(reference=self.reference)

    def test_extract(self) -> None:
        correctness_metric = self.metric_extractor.extract(report=self.report)
        self.assertEqual(correctness_metric.name, "Correctness-Metric")
        self.assertTrue(bool(int(correctness_metric.value)))


class TestCompletenessMetricExtractor(unittest.TestCase):

    def setUp(self) -> None:
        self.report = Report(
            title="UCLA",
            content="UCLA (University of California, Los Angeles) is a large, "
            "prestigious public research university located in the Westwood area of "
            "Los Angeles, California, known for its strong academics, successful "
            "athletics (now in the Big Ten), and significant impact on society, "
            "consistently ranking among the top public universities nationally.",
        )
        self.reference = Reference(
            content="UCLA (University of California, Los Angeles) is a large, "
            "prestigious public research university located in the Westwood area of "
            "Los Angeles, California, known for its strong academics, successful "
            "athletics (now in the Big Ten), and significant impact on society, "
            "consistently ranking among the top public universities nationally."
        )

        self.metric_extractor = CompletenessMetricExtractor(reference=self.reference)

    def test_extract(self) -> None:
        completeness_metric = self.metric_extractor.extract(report=self.report)
        self.assertEqual(completeness_metric.name, "Completeness-Metric")
        self.assertTrue(bool(int(completeness_metric.value)))
