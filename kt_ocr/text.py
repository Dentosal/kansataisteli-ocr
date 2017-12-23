import json
import string

LETTERS = string.ascii_letters + "åäöÅÄÖ"
SUBSET_PUNCTUATION = ".!?,:"
CHARSET = string.digits + LETTERS + SUBSET_PUNCTUATION + "-\\\"<>()* "

class Text(object):
    def __init__(self, words):
        self.words = words

    @property
    def human_readable(self):
        text = " ".join(self.words)
        for p in SUBSET_PUNCTUATION:
            text = text.replace(" "+p, p)
        return text

    def save(self, path):
        with open(path, "w") as f:
            json.dump(self.words, f)

    @classmethod
    def load(cls, path):
        with open(path) as f:
            return cls(json.load(self.words))
