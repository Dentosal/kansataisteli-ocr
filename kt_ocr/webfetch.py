import json
import regex
import requests

from .config import BASE_URL, RESULT_FOLDER, PDF_FOLDER
from .dataset import Category, Story

def fetch_categories():
    r = requests.get(BASE_URL+"/index.php")
    r.encoding = "utf-8"
    categories = []
    for code, name in regex.findall("category.php\?type=([^\"]+).+?>([^<>]+?)</h3>", r.text, regex.DOTALL):
        categories.append(Category(code, name))
    return categories

def fetch_stories(category):
    r = requests.get(category.url)
    r.encoding = "utf-8"
    stories = []
    for story_data in r.json():
        stories.append(Story(story_data, category.code))
    return stories

def fetch_all_metadata():
    categories = fetch_categories()
    all_stories = {} # story.code -> Story

    for category in categories:
        for story in fetch_stories(category):
            all_stories[story.code] = story

    return categories, all_stories.values()

def download_story(story, force=False):
    path = PDF_FOLDER / (story.code+".pdf")
    if path.exists() and not force:
        return

    r = requests.get(story.pdf_url)
    with open(path, "wb") as f:
        f.write(r.content)
