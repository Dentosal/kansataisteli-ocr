from pathlib import Path

import operator
from functools import reduce

import regex
import unicodedata

from PIL import Image
import cv2

import tesserocr

from .config import PNG_FOLDER
from .text import Text, LETTERS, SUBSET_PUNCTUATION, CHARSET

def process(image, threshold=True, deblur=True):
    img = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    if threshold:
        img = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
    if deblur:
        img = cv2.medianBlur(img, 3)

    return img

def image_to_string(img, lang):
    with tesserocr.PyTessBaseAPI(lang=lang, psm=3) as api:
        api.SetVariable("tessedit_char_whitelist", " \n"+CHARSET)
        api.SetImage(img)
        api.Recognize()

        words = []

        level = tesserocr.RIL.WORD
        for r in tesserocr.iterate_level(api.GetIterator(), level):
            word = r.GetUTF8Text(level)
            conf = r.Confidence(level)

            # print(f"{word} ({conf})")

            if words:
                previous = words[-1]
                if regex.match(r"[\p{Lu}\p{Ll}]+\-$", previous): # dash=>combine
                    words[-1] = words[-1][:-1] + word
                    continue

            # if conf > 0.95 or (all(c in LETTERS for c in word) and conf > 0.9):
            #     words.append(word)
            #     continue
            #
            # print(f"LOWCONF! {word} ({conf})")

            words.append(word)


    return filter(bool, words)

def fix_punctuation(words):
    new_words = []
    for word in words:
        if len(word) > 1:
            if any(word.startswith(p) for p in SUBSET_PUNCTUATION):
                new_words.append(word[0])
                new_words.append(word[1:])
                continue
            if any(word.endswith(p) for p in SUBSET_PUNCTUATION):
                new_words.append(word[:-1])
                new_words.append(word[-1])
                continue
        new_words.append(word)
    return new_words

def make_word(letters):
    assert all(len(l)==1 for l in letters)
    word = "".join(letters)
    for o, s in {"3": "a", "&": "a", "1": "l", "5": "s"}.items():
        word = word.replace(o, s)
    return word

def fix_fractured_words(words):
    i = 0
    seq_start = None

    while i < len(words):
        lone_letter = (len(words[i]) == 1 and words[i] not in list(SUBSET_PUNCTUATION))

        if seq_start is None:
            if lone_letter:
                seq_start = i
        else:
            if not lone_letter:
                if i - seq_start > 1:
                    words[seq_start:i] = [make_word(words[seq_start:i])]
                i, seq_start = seq_start, None
        i += 1
    return words

def ocr_read(img, lang):
    words = image_to_string(Image.fromarray(img), lang=lang)
    words = fix_punctuation(words)
    return fix_fractured_words(words)

def get_pages(story):
    pages = []
    for p in PNG_FOLDER.iterdir():
        if p.suffix != ".png":
            continue
        dname, index = p.stem.rsplit("-")
        if dname == story.code:
            pages.append(p)
    return pages

def read_story(story):
    pages = []
    for i, page in enumerate(get_pages(story)[:-1]): # discard last page
        img = process(cv2.imread(str(page)))
        pages.append(ocr_read(img, "fin"))

    words = reduce(operator.add, pages)

    if "Kirjoittajan nimimerkki" in " ".join(words[-100:]):
        remove_after = len(words)-100+words[-100:].index("Kirjoittajan")
        assert remove_after < len(words) - 2
        assert words[remove_after+1] == "nimimerkki"
        words = words[:remove_after]

    return Text(words)
