import unittest

from main.report import Report


class TestReport(unittest.TestCase):
    def setUp(self):
        self.report = Report(
            title="Hello World", content="This is a hello world document."
        )

    def test_title(self) -> None:
        self.assertEqual(self.report.title, "Hello World")

    def test_content(self) -> None:
        self.assertEqual(self.report.content, "This is a hello world document.")


if __name__ == "__main__":
    unittest.main()
