"""Diagnostics : de quoi comprendre un calendrier faux sans lire le jardin.

Ce qui sert a diagnostiquer, c'est la forme du jardin — combien de plantes,
dans quelles phases, avec quelles fiches et quels reperes de gelees — et non
ce que le jardinier y a ecrit. Les surnoms, notes et causes sont des textes
libres qui parlent de sa vie ; les destinataires de rappel nomment ses
appareils. Tout cela est masque.
"""

from __future__ import annotations

from typing import Any

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.core import HomeAssistant

from .const import CONF_NOTIFY_TARGETS, DOMAIN
from .coordinator import RhizomeCoordinator

A_MASQUER = {CONF_NOTIFY_TARGETS, "surnom", "note", "cause", "notes"}


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: Any
) -> dict[str, Any]:
    """Etat de l'integration, sans les textes libres de l'utilisateur."""
    coordinateur: RhizomeCoordinator = entry.runtime_data
    donnees = coordinateur.data or {}

    plantes = []
    for entree in donnees.get("plantes", {}).values():
        brute = entree["plante"]
        etat_eau = entree.get("arrosage")
        plantes.append(
            {
                "culture_id": brute["culture_id"],
                "fiche_personnelle": bool(entree["culture"].get("perso")),
                "zone": brute.get("zone"),
                "phase": entree["resume"]["phase"],
                "nb_evenements": entree["resume"]["nb_evenements"],
                "nb_arrosages": len(brute.get("arrosages") or []),
                "notifs": brute.get("notifs", True),
                "rappel_jours": brute.get("rappel_jours"),
                "echelonnement_jours": brute.get("echelonnement_jours"),
                "prochaine_etape": (
                    entree["prochaine"].type if entree["prochaine"] else None
                ),
                "arrosage_concerne": etat_eau.concernee if etat_eau else None,
                # La cle et non le libelle traduit : un diagnostic doit se lire
                # de la meme facon quelle que soit la langue de l'instance qui
                # l'a produit.
                "arrosage_motif_exclusion": (
                    etat_eau.motif_cle if etat_eau else None
                ),
            }
        )

    etat_notifs = coordinateur.store.etat_notifs
    return {
        "domaine": DOMAIN,
        "options": async_redact_data(dict(entry.options), A_MASQUER),
        "gelees": {
            "derniere": coordinateur.gelees.derniere,
            "premiere": coordinateur.gelees.premiere,
        },
        "calcul": {
            "date": str(donnees.get("calcule_le")),
            "dernier_succes": coordinateur.last_update_success,
            "nb_actions": len(donnees.get("actions", [])),
            "nb_arrosages_dus": len(donnees.get("arrosages", [])),
        },
        "catalogue": {
            "total": len(coordinateur.catalogue.toutes()),
            "fiches_personnelles": len(coordinateur.catalogue.perso()),
        },
        "zones": [
            {
                "id": z["id"],
                "decalage_jours": z.get("decalage_jours", 0),
                "abritee": bool(z.get("abritee")),
            }
            for z in donnees.get("zones", [])
        ],
        "plantes": plantes,
        # Les compteurs, pas les cles : elles portent les identifiants de
        # plantes, et leur nombre est justement ce qui renseigne (voir E4).
        "rappels": {
            "envoyees": len(etat_notifs.get("envoyees", {})),
            "reports": len(etat_notifs.get("reports", {})),
        },
    }
