import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from formgen import frontmatter, schema, pdfgen

WIDGET_SCHEMAS_DIR = Path(__file__).parent.parent / "tem-404_widget" / "schemas"


def main(md_path):
    md_path = Path(md_path)
    root = md_path.parent
    front, body = frontmatter.parse(md_path.read_text(encoding="utf-8"))
    fields_by_id = schema.load_fields(front)

    out_path = root / front["pdf"]["output"].format(document_version=front["form"]["document_version"])
    pdfgen.generate(front, body, fields_by_id, out_path)

    schema_path = root / "schemas" / f"v{front['form']['schema_version']}.json"
    schema.export_schema(front, fields_by_id, schema_path)

    WIDGET_SCHEMAS_DIR.mkdir(parents=True, exist_ok=True)
    widget_schema_path = WIDGET_SCHEMAS_DIR / schema_path.name
    shutil.copy(schema_path, widget_schema_path)

    print(f"PDF généré : {out_path}")
    print(f"Schéma exporté : {schema_path}")
    print(f"Schéma copié pour le widget : {widget_schema_path}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage : python build_form.py <chemin_vers_TEM-404.md>")
        sys.exit(1)
    main(sys.argv[1])
