import os
import unittest

from main.document import Document


class TestDocument(unittest.TestCase):

    def test_content(self) -> None:
        document = Document(content="Hello World")
        self.assertEqual(document.content, "Hello World")

    def test_load_from_local(self) -> None:
        input_file_path = os.path.join("data", "hello_world.txt")
        document = Document.load_from_local(input_file_path)
        self.assertEqual(document.content, "Hello World")


if __name__ == "__main__":
    unittest.main()
