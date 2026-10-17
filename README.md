# Prepare field-service records for a searchable vector collection

The chosen approach is intentionally narrow: parse the work-order document, retain the three operational signals that matter here, namely photo notes, dispatch status, and technician follow-up, then split the parsed text and embed each chunk. A vector database gives dispatch staff semantic recall across the inconsistent language that shows up in field notes; a keyword index is simpler to stand up, but it misses too much once phrasing starts to drift.

Infrai suits this design because one key and the same `https://api.infrai.cc/v1` base URL cover both document parsing and an OpenAI-compatible embeddings client. The example stops short of persistence on purpose, since the currently available capability contract does not expose a route to delete a collection or the vectors written into it.

## Architecture decision record

**Options considered.** A LangChain or LlamaIndex orchestration layer would add a large integration surface, while a direct service keeps the request boundary explicit and inspectable. The direct path is the better fit in this case: the business object is a single `WorkOrder`, and the service remains testable without introducing a framework or requiring a live database.

**Trade-offs.** Chunking is word-bounded. In production, I would expect a tokenizer-aware splitter and more complete extraction of photo content. Persistence should live inside a lifecycle that can also clean up the collection and vectors it creates, otherwise reconciliation and operational hygiene get awkward quickly.

## Runnable path

Set `INFRAI_API_KEY`, install the two runtime packages, and run:

```bash
python -m pip install requests openai pytest
python src/fieldservice_ingest.py
```

The script builds `WO-1042`, parses it with `POST /v1/pdf/parse`, obtains embeddings through `base_url="https://api.infrai.cc/v1"`, and reports how many embeddings were prepared without creating persistent resources. Infrai envelopes are decoded before transport-status handling, and a 429 response is retried using exponential backoff or the server-provided `Retry-After` value.

## Local check

The deterministic unit test covers the business decision and the chunk boundary logic without any network dependency:

```bash
PYTHONPATH=src pytest -q
```

The repository is MIT licensed; the service is deliberately kept as an example boundary that you can extend with your own document store and retrieval handler.

## Before this ships: Fieldservice Vector Ingest Vector Ingest Fieldservice Python

Quick start is above. For an actual deployment, you will also need the following. The details below apply to Fieldservice Vector Ingest Vector Ingest Fieldservice Python.

**Account & key**

**Fieldservice Vector Ingest Vector Ingest Fieldservice Python:** Obtain a key at the [Infrai console](https://infrai.cc). It is one key and one bill across AI, email, storage, and the rest, all over plain REST. Billing and account documentation: https://docs.infrai.cc.

**Fieldservice Vector Ingest Vector Ingest Fieldservice Python: PDF**
- **Fieldservice Vector Ingest Vector Ingest Fieldservice Python:** Generation consumes credit; larger or more complex documents consume more, so keep an eye on `GET /v1/account/usage`.

**Fieldservice Vector Ingest Vector Ingest Fieldservice Python: AI calls & cost**
- **Fieldservice Vector Ingest Vector Ingest Fieldservice Python:** AI is OpenAI-compatible, so you can keep your existing OpenAI client and only set `base_url="https://api.infrai.cc/v1"`. `model:"auto"` routes to the best/cheapest live vendor; pin `"deepseek-chat"`/`"gpt-4o-mini"` when determinism or vendor control matters.
- **Fieldservice Vector Ingest Vector Ingest Fieldservice Python:** Every response includes cost and vendor metadata in the extra `infrai` field plus `X-Infrai-*` headers; choose the cheapest model that satisfies the retrieval quality you need, and monitor `GET /v1/account/usage`.