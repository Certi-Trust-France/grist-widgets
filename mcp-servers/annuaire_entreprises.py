import httpx
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("annuaire-entreprises")

API_URL = "https://recherche-entreprises.api.gouv.fr/search"


def _adresse(etab: dict) -> dict:
    return {
        "siret": etab.get("siret"),
        "adresse": etab.get("adresse"),
        "code_postal": etab.get("code_postal"),
        "commune": etab.get("libelle_commune"),
        "est_siege": etab.get("est_siege"),
        "etat_administratif": etab.get("etat_administratif"),
    }


@mcp.tool()
async def rechercher_entreprise(requete: str, nombre: int = 5) -> dict:
    """Recherche des entreprises françaises par nom, SIREN (9 chiffres) ou SIRET (14 chiffres).
    Renvoie l'identité, l'adresse du siège et les établissements correspondants."""
    nombre = max(1, min(nombre, 10))

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(API_URL, params={"q": requete, "per_page": nombre})
            response.raise_for_status()
            data = response.json()
    except httpx.HTTPStatusError as e:
        return {"erreur": f"HTTP {e.response.status_code}", "detail": e.response.text[:300]}
    except httpx.HTTPError as e:
        return {"erreur": type(e).__name__, "detail": str(e)}

    return {
        "total_results": data.get("total_results"),
        "results": [
            {
                "siren": r.get("siren"),
                "nom_complet": r.get("nom_complet"),
                "etat_administratif": r.get("etat_administratif"),
                "siege": _adresse(r.get("siege") or {}),
                "nombre_etablissements_ouverts": r.get("nombre_etablissements_ouverts"),
                "etablissements": [_adresse(e) for e in r.get("matching_etablissements") or []],
            }
            for r in data.get("results", [])
        ],
    }


if __name__ == "__main__":
    mcp.run(transport="stdio")
