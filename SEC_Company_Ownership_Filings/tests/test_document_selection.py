from edgar_ownership_etl.extract.filing_document_extractor import select_ownership_document


class Resp:
    def __init__(self, text=None, json_data=None):
        self.text = text
        self._json = json_data

    def json(self):
        return self._json


class Client:
    def get(self, url):
        if url.endswith("index.json"):
            return Resp(json_data={"directory": {"item": [{"name": "a.xml"}]}})
        return Resp(text="<ownershipDocument></ownershipDocument>")


def test_select_ownership_document_from_index():
    name, txt = select_ownership_document(Client(), "http://example", None)
    assert name == "a.xml"
    assert "ownershipDocument" in txt
