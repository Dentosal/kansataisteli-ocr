from .text import Text
from .config import BASE_URL

class Category(object):
    def __init__(self, code, name):
        self.code = code
        self.name = name

    def serialize(self):
        return {"code": self.code, "name": self.name}

    @classmethod
    def deserialize(cls, data):
        return cls(data["code"], data["name"])

    @property
    def url(self):
        return f"{BASE_URL}/data/{self.code.lower()}.json"

class Story(object):
    def __init__(self, data, category_code):
        self.data = data
        self.category_code = category_code

    def serialize(self):
        return {**self.data, **{"category_code": self.category_code}}

    @classmethod
    def deserialize(cls, data):
        return cls(data, data["category_code"])

    @property
    def code(self):
        return self.data["nimi"]

    @property
    def author(self):
        return self.data["kirjoittaja"]

    @property
    def title(self):
        return self.data["otsikko"]

    @property
    def written_year(self):
        return self.data["kVuosi"]

    @property
    def event_year(self):
        return self.data["tVuosi"]

    @property
    def unit(self):
        return self.data["joukko"]

    @property
    def location(self):
        return self.data["paikka"]

    @property
    def pdf_url(self):
        return f"{BASE_URL}/kirjoitukset/{self.category_code.lower()}/{self.code}.pdf"
