# Orchestrate Support Triage Agent

Command-line support triage for the HackerRank Orchestrate challenge.

The program reads the evaluator's ticket file, searches the provided support corpus, decides whether each case should be answered or escalated, and writes the completed predictions CSV. It is built for the challenge workflow: run one terminal command, produce `support_tickets/output.csv`, submit the result.

## Evaluation Contract

Expected repository shape:

```text
.
├── code/
├── data/
│   ├── claude/
│   ├── hackerrank/
│   └── visa/
└── support_tickets/
    └── support_tickets.csv
```

Run from the repository root:

```bash
python code/main.py
```

The agent reads:

```text
support_tickets/support_tickets.csv
```

and writes:

```text
support_tickets/output.csv
```

That output contains the original ticket fields plus the five required prediction fields:

```text
issue,subject,company,response,product_area,status,request_type,justification
```

## What The Agent Handles

The ticket set spans HackerRank, Claude, and Visa support. The messages are not clean FAQ prompts; they include blank subjects, mixed wording, urgent requests, irrelevant questions, account and billing pressure, security-sensitive cases, and product-specific issues.

The agent is designed to do five things reliably:

1. classify the request,
2. retrieve matching corpus evidence,
3. decide whether the ticket is safe to answer,
4. produce a grounded support response,
5. write a schema-valid CSV row.

Allowed output values are enforced before writing:

```text
status: replied | escalated
request_type: product_issue | feature_request | bug | invalid
```

## Architecture

```text
CSV ticket
   |
   v
intent classifier  ----> request_type, emergency flag, retrieval query
   |
   v
risk scanner       ----> deterministic sensitive-case signal
   |
   v
hybrid retriever   ----> BM25 + MiniLM over local support docs
   |
   v
evidence validator ----> answerability + grounded response
   |
   v
decision engine    ----> replied / escalated
   |
   v
Pydantic schema    ----> output.csv row
```

## Code Layout

```text
code/
├── main.py                         # entrypoint and CSV orchestration
├── requirements.txt
├── classification/
│   ├── intent_classifier.py        # request type, emergency flag, retrieval query
│   └── risk_classifier.py          # deterministic high-risk keyword scan
├── config/
│   └── enums.py                    # paths, enums, allowed values
├── decision/
│   └── decision_engine.py          # reply/escalate decision
├── ingestion/
│   └── loader.py                   # corpus loading and chunking
├── retrieval/
│   ├── bm25.py                     # lexical index
│   ├── embeddings.py               # MiniLM model + embedding cache
│   └── hybrid.py                   # lexical/semantic rank fusion
├── utils/
│   ├── llm_client.py               # OpenRouter client
│   └── schema_validator.py         # Pydantic output validation
└── validation/
    └── evidence_validator.py       # evidence check and response drafting
```

## Retrieval

The corpus is loaded from the local `data/` directory. Each document chunk keeps its ecosystem, source document, section path, and text.

Retrieval is scoped by ecosystem when the company is known. A Claude ticket searches Claude docs, a Visa ticket searches Visa docs, and a HackerRank ticket searches HackerRank docs.

Ranking combines two signals:

- BM25 for exact support terms and product language.
- MiniLM embeddings for semantic matches when the ticket uses different wording.

The hybrid score is:

```text
0.5 * normalized_bm25 + 0.5 * cosine_similarity
```

Corpus embeddings are cached under `data/embeddings/` after they are computed. That keeps repeated evaluation runs fast without adding model files or generated artifacts to the submitted `code/` directory.

## Safety And Grounding

The agent does not answer directly from model memory. It retrieves corpus evidence first, validates whether the evidence can support an answer, and only then drafts a response.

Safety routing is handled in two layers:

- `risk_classifier.py` catches sensitive language such as fraud, unauthorized access, account compromise, payment failure, legal/GDPR, and related risk terms.
- `intent_classifier.py` detects true emergency/outage claims and classifies the request type.

The final decision uses both retrieval confidence and safety signals. Supported tickets get a direct response. Risky or unsupported tickets are escalated. Harmless out-of-scope messages get a short deflection instead of a fabricated policy.

## Model Configuration

The LLM client sends requests through OpenRouter.

Required:

```bash
export OPENROUTER_API_KEY="your_openrouter_key"
```

Optional:

```bash
export LLM_MODEL="google/gemma-4-31b-it:free"
export LLM_CALL_DELAY="4"
```

`LLM_MODEL` can be changed without touching code. `LLM_CALL_DELAY` controls the pause before model calls, which is useful when running through low-rate-limit endpoints.

## Setup

Install dependencies from the repository root:

```bash
python -m pip install -r code/requirements.txt
```

Dependencies are intentionally standard Python packages:

```text
pandas
rank-bm25
sentence-transformers
openai
python-dotenv
pydantic
tenacity
numpy
```

The `openai` package is used only as an SDK for OpenRouter's compatible chat-completions API. The code requires `OPENROUTER_API_KEY`.

## Run

Generate the final predictions:

```bash
python code/main.py
```

Run the sample file:

```bash
python code/main.py test
```

Sample mode writes to the same `support_tickets/output.csv` path. If sample mode is used during checking, run the default command again before submission.

## Runtime Behavior

The first run initializes the retrieval stack and prepares local embedding cache files. Later runs reuse the cached corpus embeddings and only embed incoming queries at runtime.

LLM calls are still the main runtime cost because the agent performs structured classification and evidence validation for each ticket. That is intentional: the model is used where judgment is needed, while retrieval and validation keep the response grounded in the provided corpus.

For faster runs on a higher-throughput OpenRouter model/account, reduce the call delay:

```bash
export LLM_CALL_DELAY="1"
python code/main.py
```

## Validation Snapshot

On the provided sample ticket set, the agent matched the explicit categorical labels:

| Field | Result |
| --- | --- |
| `status` | 10 / 10 |
| `request_type` | 10 / 10 |

The architecture also produces the remaining judged fields: product area, response, and justification.

## Submission Check

Before uploading:

```bash
python code/main.py
```

Confirm:

- `support_tickets/output.csv` exists.
- It has one output row per input ticket.
- `status` contains only `replied` or `escalated`.
- `request_type` contains only `product_issue`, `feature_request`, `bug`, or `invalid`.
- The code zip excludes `.env`, caches, virtual environments, `__pycache__`, and debug logs.

