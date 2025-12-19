
```markdown
# A Customized Reliable Document Summarizer
An agentic workflow was designed and implemented for summarizing documents to reports accurately.

## Overview
This project implements a production-oriented AI agent that summarizes documents into reports.

The system is designed for **reliability and traceability**. A comprehensive evaluation framework is implemented for guarantteeing its reliability.

## Key Features
- Structured Prompt which includes (1) Instructions; (2) Context; (3) Requirements 
- Requirements are coupled with metrics and metric extractors for quantifing the validity and the quality of a summarization report
- LLM_as_judge for extracting both accuracy metric and completeness metric
- Extensible agent workflow

## Tech Stack
- Python
- Large Language Models (configurable)
- Ollama
- LLM-as-judge

## Running
