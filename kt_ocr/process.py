import json
import subprocess

from .dataset import Category, Story
from .webfetch import fetch_all_metadata, download_story
from .ocr import read_story
from .config import METADATA_FILE, RESULT_FOLDER, PDF_FOLDER, PNG_FOLDER

def download_all_metadata():
    categories, stories = fetch_all_metadata()
    with open(METADATA_FILE, "w") as f:
        json.dump({
            "categories": [c.serialize() for c in categories],
            "stories": [s.serialize() for s in stories]
        }, f)

def get_metadata():
    if not METADATA_FILE.exists():
        download_all_metadata()

    with open(METADATA_FILE) as f:
        data = json.load(f)

    categories = [Category.deserialize(c) for c in data["categories"]]
    stories = [Story.deserialize(s) for s in data["stories"]]

    return categories, stories

def convert_story(story, force=False):
    if (PNG_FOLDER / (story.code+"-0.png")).exists() and not force:
        return

    subprocess.run([
        "convert",
        "-density", "300",
        "-depth", "8",
        "-quality", "100",
        str(PDF_FOLDER / (story.code+".pdf")),
        str(PNG_FOLDER / (story.code+".png"))
    ])

def remove_pngs(story):
    for path in PNG_FOLDER.iterdir():
        if path.suffix != ".png":
            continue
        if path.stem.rsplit("-", 1)[0] == story.code:
            path.unlink()

def main(quiet=False, force=False, keep_pngs=False):
    categories, stories = get_metadata()

    for i, story in enumerate(stories):
        if not quiet:
            print(f"Downloading [{i*100//(len(stories)-1)}%] {story.author} - {story.title}")

        download_story(story, force=force)

    for i, story in enumerate(stories):
        if not quiet:
            print(f"Converting [{i*100//(len(stories)-1)}%] {story.author} - {story.title}")

        convert_story(story, force=force)

        path = RESULT_FOLDER / (story.code + ".json")

        if (not path.exists()) or force:
            text = read_story(story)
            text.save(path)

        if not keep_pngs:
            remove_pngs(story)
