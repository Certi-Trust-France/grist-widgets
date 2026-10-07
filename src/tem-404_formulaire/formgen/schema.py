import json
from dataclasses import dataclass, field, asdict

VALID_TYPES = {"text", "checkbox", "radio", "choice"}
VALID_GRIST_TABLES = {"Entreprises", "Contacts", "Sites", "Systemes_Information"}


@dataclass
class Field:
    id: str
    type: str
    label: str = ""
    grist_column: str = ""
    grist_table: str = None  # table cible pour l'écriture structurée ; absent = champ JSON uniquement (Json_Complet/Json_Utile)
    required: bool = False
    since: str = ""
    maxlen: int = None
    pattern: str = None
    options: list = field(default_factory=list)
    deprecated: str = None
    replaced_by: str = None
    read_only: bool = False


def load_fields(front):
    raw_fields = front.get("fields") or []
    fields = [Field(**f) for f in raw_fields]

    seen = set()
    for f in fields:
        if f.id in seen:
            raise ValueError(f"id de champ dupliqué : {f.id}")
        seen.add(f.id)
        if f.type not in VALID_TYPES:
            raise ValueError(f"type inconnu pour le champ {f.id} : {f.type}")
        if f.type in ("radio", "choice") and not f.options:
            raise ValueError(f"le champ {f.id} (type {f.type}) doit déclarer des options")
        if f.deprecated and not f.replaced_by:
            raise ValueError(f"le champ {f.id} est deprecated mais n'indique pas replaced_by")
        if f.grist_table and f.grist_table not in VALID_GRIST_TABLES:
            raise ValueError(f"le champ {f.id} déclare une grist_table inconnue : {f.grist_table}")
        if f.grist_table and not f.grist_column:
            raise ValueError(f"le champ {f.id} déclare grist_table sans grist_column")

    return {f.id: f for f in fields}


def export_schema(front, fields_by_id, out_path):
    payload = {
        "form_id": front["form"]["id"],
        "schema_version": front["form"]["schema_version"],
        "fields": [asdict(f) for f in fields_by_id.values()],
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
