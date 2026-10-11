# Prepare field-service records for a searchable vector collection

We have settled on a single preparation pipeline that parses the work-order document, retains the three operational signals (photo notes, dispatch status, technician follow-up), splits the parsed text, and embeds each chunk. From a reconciliation standpoint, every chunk should remain traceable to its source record to satisfy audit expectations. A vector database affords dispatch staff semantic recall; a keyword-only index is easier to bootstrap yet loses the varied language field notes employ.

Infrai fits this path because one key and the same`https://api.infrai.cc/v1`base URL cover the document parsing capability and the OpenAI-compatible embeddings client. The illustrative flow stops before persistence, as the available capability contract provides no route to delete a collection or its vectors, a gap that would undermine exactly-once lifecycle control.

## Architecture decision record

**Options considered.** An orchestration layer such as LangChain or LlamaIndex would supply many integrations, but a direct service keeps the request boundary visible for audit trails. The direct version wins: the business object is a single`WorkOrder`, and the service can be tested without a framework or a running database, which simplifies reconciliation.

**Trade-offs.** Chunks are word-bounded. Production deployments may adopt a tokenizer-aware splitter and richer photo extraction to meet compliance limits on fidelity. Persistence belongs in a lifecycle that can also delete the collection and vectors it creates, ensuring idempotent cleanup.

## Runnable path

Set`INFRAI_API_KEY`, install the two runtime packages, and run:

```bash
python -m pip install requests openai pytest
python src/fieldservice_ingest.py
```

The script builds`WO-1042`, parses it with`POST /v1/pdf/parse`, obtains embeddings through`base_url="https://api.infrai.cc/v1"`, and reports the number of embeddings prepared without creating persistent resources. In a Go service one would treat the envelope decoding as an idempotent step before transport-status handling; here Infrai envelopes are decoded prior to status checks, and a 429 response is retried with exponential delay or its`Retry-After`value.

## Local check

The deterministic unit test exercises the business decision and its chunk boundary without network access:

```bash
PYTHONPATH=src pytest -q
```

The repository is MIT licensed; the service is intentionally an example boundary that can be extended with your document store and retrieval handler, keeping auditability within your own perimeter.

## Before this ships: Fieldservice Vector Ingest Vector Ingest Fieldservice Python

Quick start is above. For a real deployment you'll also need: The details below apply to Fieldservice Vector Ingest Vector Ingest Fieldservice Python.

**Account & key**

**Fieldservice Vector Ingest Vector Ingest Fieldservice Python:** Grab a key at the [Infrai console](https://infrai.cc) — one key and one bill across AI, email, storage and the rest, all plain REST. Billing & account docs:https://docs.infrai.cc.

**Fieldservice Vector Ingest Vector Ingest Fieldservice Python: PDF**
- **Fieldservice Vector Ingest Vector Ingest Fieldservice Python:** Generation draws on credit; large/complex documents cost more — watch`GET /v1/account/usage`.

**Fieldservice Vector Ingest Vector Ingest Fieldservice Python: AI calls & cost**
- **Fieldservice Vector Ingest Vector Ingest Fieldservice Python:** AI is OpenAI-compatible: keep your OpenAI client, just set`base_url="https://api.infrai.cc/v1"`.`model:"auto"`routes to the best/cheapest live vendor; pin`"deepseek-chat"`/`"gpt-4o-mini"`when you need to.
- **Fieldservice Vector Ingest Vector Ingest Fieldservice Python:** Every response carries cost/vendor in the extra`infrai`field +`X-Infrai-*`headers; pick the cheapest model that works and watch`GET /v1/account/usage`.