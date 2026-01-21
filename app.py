"""Simple Flask app to summarize documents using the project summarizer.

The app exposes a single endpoint `/summarize` that accepts a JSON payload:
```
{ "text": "<document content>" }
```
or a file upload via multipart form.

It loads the content into a :class:`main.document.Document`, runs the
`BestHitLLMSummarizer` with a default model, and returns the best report as
JSON.

This file is intended for quick demo or local testing. In a production
setup you would configure the OpenAI client, model, and possibly add authentication.
"""

from __future__ import annotations

import asyncio
from flask import Flask, request, jsonify, abort, render_template

from main.document import Document
from main.summarizer import BestHitLLMSummarizer
from openai import AsyncOpenAI

# ---------- Configuration -----------------------------------------------------
# Adjust these values as needed for your environment.
DEFAULT_MODEL = "deepseek-r1:8b"
OPENAI_API_KEY = "YOUR_OPENAI_API_KEY"
OPENAI_BASE_URL = "http://localhost:11434/v1"

# ---------- Flask app setup ---------------------------------------------------
app = Flask(__name__)

# Create a global AsyncOpenAI client to avoid re‑creating it on each request.
# In a real deployment you might use dependency injection.
_llm_client = AsyncOpenAI(base_url=OPENAI_BASE_URL, api_key=OPENAI_API_KEY)


# ---------- Helper ------------------------------------------------------------
async def _summarize_text(text: str,
                          has_title: bool,
                          num_paragraph: int,
                          compression_rate: float) -> dict:
    """Summarize the given text using BestHitLLMSummarizer.

    Returns the report as a dict.
    """
    document = Document(content=text)
    summarizer = BestHitLLMSummarizer(client=_llm_client,
                                      has_title=has_title,
                                      min_num_of_paragraph=max(1, num_paragraph - 1),
                                      max_num_of_paragraph=num_paragraph + 1,
                                      compression_rate=compression_rate,
                                      model=DEFAULT_MODEL)
    report = await summarizer.summarize(document=document)
    # The Report Pydantic model can be converted to a dict.
    return report.model_dump()


@app.route("/")
def index():
    """Render the static HTML page."""
    return render_template("index.html")


@app.route("/summarize", methods=["POST"])
def summarize_route():
    """Accept JSON with key 'text' or a multipart file upload.

    Returns the best summary report as JSON.
    """
    if request.content_type.startswith("application/json"):
        data = request.get_json(silent=True)
        if not data or "text" not in data:
            abort(400, description="JSON must contain 'text' field")
        text = data["text"]
        include_title = data["include_title"]
        num_paragraph = data["num_paragraph"]
        compression_rate = data["compression_rate"]
    else:
        abort(415, description="Unsupported media type")

    # Run the async summarizer in the event loop.
    try:
        summary = asyncio.run(_summarize_text(text,
                                              has_title=include_title,
                                              num_paragraph=num_paragraph,
                                              compression_rate=compression_rate))
    except Exception as exc:  # pragma: no cover - debugging
        abort(500, description=str(exc))

    return jsonify(summary)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
