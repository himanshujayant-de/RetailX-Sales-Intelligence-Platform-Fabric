import glob

import nbformat


for path in glob.glob("**/*.ipynb", recursive=True):
    try:
        notebook = nbformat.read(path, as_version=4)
        nbformat.validate(notebook)
        print(f"VALID: {path}")
    except Exception as exc:
        print(f"BROKEN: {path} -> {exc}")