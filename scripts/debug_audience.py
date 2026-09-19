from pathlib import Path
from bench import parse_md_file, DATA_DIR

for p in sorted(DATA_DIR.glob("*.md")):
    fm, body = parse_md_file(p)
    print(p.stem, "audience=", repr(fm.get("audience")), "keys=", list(fm.keys()))
