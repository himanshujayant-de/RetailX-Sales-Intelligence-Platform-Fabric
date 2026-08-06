import json
from pathlib import Path
from typing import Any


NOTEBOOK_ROOT = Path(notebooks)


def repair_notebook(path Path) - bool
    Add missing required fields without changing notebook code.

    try
        notebook dict[str, Any] = json.loads(
            path.read_text(encoding=utf-8)
        )
    except (OSError, json.JSONDecodeError) as exc
        print(fCould not read {path} {exc})
        return False

    changed = False

    for cell in notebook.get(cells, [])
        if cell.get(cell_type) != code
            continue

        if execution_count not in cell
            cell[execution_count] = None
            changed = True

        if outputs not in cell
            cell[outputs] = []
            changed = True

    if changed
        path.write_text(
            json.dumps(notebook, indent=2, ensure_ascii=False) + n,
            encoding=utf-8,
        )
        print(fFIXED {path})
    else
        print(fNO CHANGE {path})

    return changed


def main() - None
    notebook_files = list(NOTEBOOK_ROOT.rglob(.ipynb))

    if not notebook_files
        raise SystemExit(No notebook files found.)

    repaired_count = 0

    for notebook_file in notebook_files
        if repair_notebook(notebook_file)
            repaired_count += 1

    print(
        fnCompleted checked {len(notebook_files)} notebooks, 
        frepaired {repaired_count}.
    )


if __name__ == __main__
    main()