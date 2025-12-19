
```markdown
# A Customized Document Summarizer

A customized summarizer implemented on top of LLMs.

## Overview
This project implements a production-oriented AI agent that analyzes security logs, extracts key signals, and generates concise incident summaries for SOC analysts.

The system is designed for **reliability and traceability**, with clear separation between data processing, model inference, and post-processing.

## Key Features
- Structured Prompt which includes (1) Instructions; (2) Context; (3) Requirements 
- Requirements are coupled with metrics and metric extractors for quantifing the validity and the quality of a summarization report
- LLM_as_judge for extracting both accuracy metric and completeness metric
- Extensible agent workflow

## Tech Stack
- Python
- Large Language Models (configurable)

## Running
