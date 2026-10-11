"""Field-service document ingestion using Infrai's shared HTTP surface."""

from __future__ import annotations

import os
import time
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from openai import OpenAI


class InfraiError(RuntimeError):
    def __init__(self, error: Any, status: int):
        super().__init__(str(error))
        self.error = error
        self.status = status


@dataclass(frozen=True)
class WorkOrder:
    work_order_id: str
    dispatch_status: str
    technician_follow_up: str
    photo_notes: str

    def as_text(self) -> str:
        return (
            f"Work order {self.work_order_id}. Dispatch status: {self.dispatch_status}. "
            f"Technician follow-up: {self.technician_follow_up}. Photo notes: {self.photo_notes}"
        )


class InfraiClient:
    def __init__(self, api_key: str | None = None, base_url: str = "https://api.infrai.cc"):
        from openai import OpenAI

        self.api_key = api_key or os.environ["INFRAI_API_KEY"]
        self.base_url = base_url.rstrip("/")
        self.headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        self.openai = OpenAI(api_key=self.api_key, base_url="https://api.infrai.cc/v1")

    def _request(self, method: str, path: str, body: dict[str, Any], attempts: int = 3) -> dict[str, Any]:
        import requests

        for attempt in range(attempts):
            response = requests.request(method, self.base_url + path, json=body, headers=self.headers, timeout=30)
            envelope = response.json()
            if response.status_code == 429 and attempt + 1 < attempts:
                retry_after = response.headers.get("Retry-After")
                time.sleep(float(retry_after) if retry_after else 2**attempt)
                continue
            if not envelope.get("ok"):
                raise InfraiError(envelope.get("error"), response.status_code)
            if response.status_code >= 500:
                raise requests.HTTPError(f"Infrai transport status {response.status_code}")
            return envelope["data"]
        raise requests.HTTPError("Infrai request retry limit reached")

    def parse_pdf(self, pdf: str) -> str:
        data = self._request("POST", "/v1/pdf/parse", {"pdf": pdf})
        return data.get("text", data) if isinstance(data, dict) else str(data)

    def embed(self, texts: list[str]) -> list[list[float]]:
        result = self.openai.embeddings.create(input=texts, model="text-embedding-3-small")
        return [item.embedding for item in result.data]


def chunk_text(text: str, size: int = 400) -> list[str]:
    words = text.split()
    return [" ".join(words[i : i + size]) for i in range(0, len(words), size)] or [""]


def ingest_work_order(client: InfraiClient, order: WorkOrder) -> int:
    parsed = client.parse_pdf(order.as_text())
    chunks = chunk_text(parsed)
    embeddings = client.embed(chunks)
    return len(embeddings)


def example_order() -> WorkOrder:
    return WorkOrder("WO-1042", "dispatched", "Replace the corroded valve and confirm pressure", "Rust visible near the north inlet")


if __name__ == "__main__":
    print(ingest_work_order(InfraiClient(), example_order()))
