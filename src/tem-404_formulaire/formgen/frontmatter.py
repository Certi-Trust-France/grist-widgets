import re

import yaml

# Ligne composée uniquement de '---' : un '---' en commentaire YAML (ex. un séparateur de
# section dans la liste `fields`) ne doit pas être confondu avec le délimiteur de front matter.
DELIM_RE = re.compile(r"(?m)^---\s*$")


def parse(md_text):
    """Sépare le front matter YAML (entre les deux premières lignes `---`) du corps markdown."""
    if not md_text.startswith("---"):
        raise ValueError("TEM-404.md doit commencer par un front matter YAML délimité par '---'")

    parts = DELIM_RE.split(md_text, maxsplit=2)
    if len(parts) < 3:
        raise ValueError("front matter YAML mal délimité (deux lignes '---' seules attendues)")
    _, front_raw, body = parts
    front = yaml.safe_load(front_raw) or {}
    return front, body.lstrip("\n")
