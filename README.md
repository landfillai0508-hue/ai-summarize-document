
```markdown
# A Customized Summarizer for Summarizing Documents into Summarization Reports

An AI agent that summarizes security incidents using structured logs and LLMs to reduce investigation time.

## Overview
This project implements a production-oriented AI agent that analyzes security logs, extracts key signals, and generates concise incident summaries for SOC analysts.

The system is designed for **reliability and traceability**, with clear separation between data processing, model inference, and post-processing.

## Key Features
- Dynamic Prompting 
- LLM-based summarization with prompt templates
- Deterministic output validation
- Extensible agent workflow

## Tech Stack
- Python
- Large Language Models (configurable)

## Running
```bash
python main.py --input sample_logs.json
