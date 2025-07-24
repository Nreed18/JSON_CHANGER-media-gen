import os
import re

class FileSystemLoader:
    def __init__(self, searchpath):
        if isinstance(searchpath, str):
            searchpath = [searchpath]
        self.searchpath = searchpath

def _load_template(name, searchpath):
    for sp in searchpath:
        path = os.path.join(sp, name)
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()
    raise FileNotFoundError(name)

class Template:
    def __init__(self, text):
        self.text = text
    def render(self, **context):
        def repl(match):
            key = match.group(1).strip()
            return str(context.get(key, ''))
        return re.sub(r"\{\{([^{}]+)\}\}", repl, self.text)

class Environment:
    def __init__(self, loader):
        self.loader = loader
    def get_template(self, name):
        text = _load_template(name, self.loader.searchpath)
        return Template(text)
