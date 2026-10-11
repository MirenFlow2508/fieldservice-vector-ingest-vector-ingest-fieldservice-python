from fieldservice_ingest import WorkOrder, chunk_text, ingest_work_order


def test_work_order_text_keeps_the_three_operational_signals():
    order = WorkOrder("WO-7", "en route", "Call customer after repair", "Loose conduit by panel")
    text = order.as_text()
    assert "WO-7" in text
    assert "en route" in text
    assert "Call customer after repair" in text
    assert "Loose conduit by panel" in text


def test_chunk_text_is_deterministic_and_bounded():
    chunks = chunk_text("one two three four five", size=2)
    assert chunks == ["one two", "three four", "five"]


def test_documented_path_does_not_create_persistent_resources():
    class Client:
        def parse_pdf(self, pdf):
            return pdf

        def embed(self, texts):
            return [[0.1, 0.2] for _ in texts]

    assert ingest_work_order(Client(), WorkOrder("WO-7", "open", "Call", "Loose conduit")) == 1
