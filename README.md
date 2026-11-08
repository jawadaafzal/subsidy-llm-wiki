\# Subsidy LLM Wiki



An LLM-powered knowledge management system for Pakistani government subsidies. The project uses Retrieval-Augmented Generation (RAG) and Large Language Models (LLMs) to extract information from official government documents, retrieve relevant evidence, generate structured Wiki pages, and support fact-checking and human review.



\## Project Objectives



\- Build a structured Wiki from official Pakistani government documents.

\- Retrieve relevant information with source references.

\- Generate Wiki drafts using Google's Gemini API.

\- Detect unsupported claims and potential factual errors.

\- Ensure human review before Wiki pages are approved.



\## Key Features



\- \*\*Document Ingestion:\*\* Extracts text from official PDF documents.

\- \*\*Text Chunking:\*\* Splits documents into smaller overlapping chunks.

\- \*\*Information Retrieval:\*\* Uses BM25 to retrieve relevant source passages.

\- \*\*AI Draft Generation:\*\* Uses Gemini to create structured Wiki drafts.

\- \*\*Fact-Checking:\*\* A lint agent checks drafts against retrieved evidence.

\- \*\*Human Review:\*\* Supports approval and rejection of Wiki drafts.

\- \*\*Streamlit Interface:\*\* Provides a web interface for searching and generating drafts.

\- \*\*Evaluation:\*\* Tests source retrieval and compares Wiki-based answers with RAG-based answers.



\## Technology Stack



\- Python

\- Google Gemini API

\- BM25 (rank-bm25)

\- Pydantic

\- Streamlit

\- PyMuPDF4LLM

\- Python Frontmatter

\- PyYAML



\## Project Structure



```text

subsidy-llm-wiki/

├── raw/              # Original and extracted documents

├── wiki/             # Structured Wiki pages and drafts

├── src/              # Python source code

├── eval/             # Evaluation dataset

├── docs/             # Project documentation

├── tests/            # Tests

├── app.py            # Streamlit application

├── SCHEMA.md         # Wiki page schema

├── PROGRESS.md       # Project progress

├── requirements.txt  # Dependencies

└── README.md         # Project documentation

```



\## Installation



Clone the repository:



```bash

git clone https://github.com/jawadaafzal/subsidy-llm-wiki.git

cd subsidy-llm-wiki

```



Create and activate a virtual environment:



```bash

python -m venv .venv

source .venv/Scripts/activate

```



Install dependencies:



```bash

pip install -r requirements.txt

```



\## Configuration



Create a `.env` file in the project root:



```env

GEMINI\_API\_KEY=your\_gemini\_api\_key

```



Keep your API key private. Never commit the `.env` file to GitHub.



\## Usage



Run document ingestion:



```bash

python -m src.ingest

```



Search official sources:



```bash

python -m src.query

```



Generate a Wiki draft:



```bash

python -m src.draft

```



Run the lint agent:



```bash

python -m src.lint\_agent

```



Start the Streamlit application:



```bash

python -m streamlit run app.py

```



Run retrieval evaluation:



```bash

python -m src.evaluate

```



Compare Wiki and RAG responses:



```bash

python -m src.compare

```



\## Evaluation Results



The initial retrieval evaluation achieved:



\- Test cases: 8

\- Passed: 8

\- Source retrieval accuracy: 100%



This measures whether the expected source was retrieved. It does not establish 100% factual-answer accuracy.



\## Limitations



\- The initial scope focuses on federal-level Pakistani government subsidies.

\- Results depend on the coverage and quality of available official documents.

\- Retrieved evidence and AI-generated claims require verification.

\- Human review is required before approving Wiki content.



\## Future Improvements



\- Add more official government documents.

\- Improve retrieval accuracy and citation precision.

\- Expand automated factual evaluation.

\- Improve Wiki versioning and contradiction detection.

\- Add more advanced Wiki browsing and management features.



\## Project Status



This project is under active development.

