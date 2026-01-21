import pytest
import tempfile
import os

from main.document import Document


@pytest.fixture
def sample_text():
    return "Hello, world! This is a test document."


def test_load_from_local(sample_text):
    # create a temporary file with sample_text
    with tempfile.NamedTemporaryFile("w", delete=False, suffix=".txt") as tmp:
        tmp.write(sample_text)
        tmp_path = tmp.name

    try:
        doc = Document.load_from_local(tmp_path)
        assert isinstance(doc, Document)
        assert doc.content == sample_text
    finally:
        os.remove(tmp_path)


def test_pprint_captures_output(sample_text, capsys):
    # Create a Document instance
    doc = Document(content=sample_text)
    # Capture stdout when pprint is called
    doc.pprint()
    captured = capsys.readouterr()
    # pprint prints the string representation; it should contain the content
    assert sample_text in captured.out
