"""Capteurs : etat du potager, recolte de la saison, et une fiche par plante."""

from __future__ import annotations

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import UnitOfMass
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .coordinator import RhizomeCoordinator, libelle_phase
from .entity import RhizomeEntity, RhizomePlanteEntity, suivre_les_plantes
from .lifecycle import PHASES_LIBELLES

PLATEFORME = "sensor"
SUFFIXE = "etat"


async def async_setup_entry(
    hass: HomeAssistant, entry, async_add_entities: AddEntitiesCallback
) -> None:
    coordinator: RhizomeCoordinator = entry.runtime_data
    async_add_entities(
        [
            ActionsSensor(coordinator),
            RecolteSensor(coordinator),
            ArrosageSensor(coordinator),
        ]
    )

    suivre_les_plantes(
        hass,
        entry,
        coordinator,
        async_add_entities,
        lambda coord, uid: [PlanteSensor(coord, uid)],
        PLATEFORME,
        SUFFIXE,
    )


class ActionsSensor(RhizomeEntity, SensorEntity):
    """Combien d'actions reclament une attention, et lesquelles."""

    _attr_name = "Actions à mener"
    _attr_icon = "mdi:sprout"
    _attr_native_unit_of_measurement = "actions"
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, coordinator: RhizomeCoordinator) -> None:
        super().__init__(coordinator, "actions")

    @property
    def native_value(self) -> int:
        return len(self.coordinator.data["actions"])

    @property
    def extra_state_attributes(self) -> dict:
        return {
            # `uid` et `etape` ne sont pas decoratifs : ils permettent a la
            # carte Lovelace d'enregistrer « C'est fait » sans autre requete.
            "actions": [
                {
                    "uid": action["uid"],
                    "plante": action["nom"],
                    "emoji": action["emoji"],
                    "action": action["etape"].libelle,
                    "etape": action["etape"].type,
                    "zone": action["zone"],
                    "debut": action["etape"].debut.isoformat(),
                    "fin": action["etape"].fin.isoformat(),
                    "jours_restants": action["jours_restants"],
                    "en_cours": action["en_cours"],
                }
                for action in self.coordinator.data["actions"]
            ],
            "nb_plantes": len(self.coordinator.data["plantes"]),
        }


class RecolteSensor(RhizomeEntity, SensorEntity):
    """Total recolte, en kilos. `total` plutot que `total_increasing` : une
    annulation au journal doit pouvoir faire redescendre le compteur."""

    _attr_name = "Récolte de la saison"
    _attr_icon = "mdi:basket"
    _attr_device_class = SensorDeviceClass.WEIGHT
    _attr_native_unit_of_measurement = UnitOfMass.KILOGRAMS
    _attr_state_class = SensorStateClass.TOTAL
    _attr_suggested_display_precision = 2

    def __init__(self, coordinator: RhizomeCoordinator) -> None:
        super().__init__(coordinator, "recolte")

    @property
    def native_value(self) -> float:
        return round(self.coordinator.data["total_recolte_g"] / 1000, 3)

    @property
    def extra_state_attributes(self) -> dict:
        par_culture: dict[str, int] = {}
        for entree in self.coordinator.data["plantes"].values():
            grammes = entree["resume"].get("recolte_saison_g", 0)
            if grammes:
                nom = entree["culture"]["nom"]
                par_culture[nom] = par_culture.get(nom, 0) + grammes
        return {
            "saison": self.coordinator.data["saison"],
            "par_culture_g": dict(
                sorted(par_culture.items(), key=lambda kv: -kv[1])
            ),
            "nb_recoltes": sum(
                e["resume"]["nb_recoltes"]
                for e in self.coordinator.data["plantes"].values()
            ),
            # Conserve pour ne rien perdre : le cumul de toutes les saisons.
            "total_toutes_saisons_kg": round(
                self.coordinator.data["total_toutes_saisons_g"] / 1000, 3
            ),
        }


class ArrosageSensor(RhizomeEntity, SensorEntity):
    """Combien de plantes attendent de l'eau, et lesquelles.

    Separe du capteur d'actions : l'arrosage revient tous les deux jours quand
    un semis revient une fois l'an. Les melanger rendrait les deux illisibles.
    """

    _attr_name = "À arroser"
    _attr_icon = "mdi:watering-can"
    _attr_native_unit_of_measurement = "plantes"
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, coordinator: RhizomeCoordinator) -> None:
        super().__init__(coordinator, "arrosage")

    @property
    def native_value(self) -> int:
        return len(self.coordinator.data.get("arrosages", []))

    @property
    def extra_state_attributes(self) -> dict:
        return {
            "plantes": [
                {
                    "uid": besoin["uid"],
                    "plante": besoin["nom"],
                    "emoji": besoin["emoji"],
                    "zone": besoin["zone"],
                    "jours_de_retard": -besoin["etat"].jours_restants,
                    "dernier_arrosage": (
                        besoin["etat"].dernier.isoformat()
                        if besoin["etat"].dernier
                        else None
                    ),
                }
                for besoin in self.coordinator.data.get("arrosages", [])
            ],
        }


class PlanteSensor(RhizomePlanteEntity, SensorEntity):
    """Une plante du jardin : sa phase en etat, sa fiche en attributs."""

    _attr_device_class = SensorDeviceClass.ENUM
    # `_attr_options` est declare comme une liste par l'API de Home Assistant :
    # un ClassVar ne conviendrait pas, d'ou la derogation.
    _attr_options = list(PHASES_LIBELLES.values())  # noqa: RUF012

    def __init__(self, coordinator: RhizomeCoordinator, uid: str) -> None:
        super().__init__(coordinator, uid, SUFFIXE)

    @property
    def icon(self) -> str:
        entree = self.entree
        if entree is None:
            return "mdi:sprout"
        return {
            "prevu": "mdi:calendar-clock",
            "seme": "mdi:seed",
            "plante": "mdi:sprout",
            "en_recolte": "mdi:basket",
            "termine": "mdi:check-circle-outline",
            "perdu": "mdi:emoticon-sad-outline",
        }.get(entree["resume"]["phase"], "mdi:sprout")

    @property
    def native_value(self) -> str | None:
        entree = self.entree
        return libelle_phase(entree["resume"]["phase"]) if entree else None

    @property
    def extra_state_attributes(self) -> dict:
        entree = self.entree
        if entree is None:
            return {}

        fiche = entree["culture"]
        infos = entree["resume"]
        prochaine = entree["prochaine"]
        aujourdhui = self.coordinator.data["calcule_le"]

        attributs = {
            # L'uid est ce que reclament les services `potager.*`. Sans lui
            # expose ici, il faudrait aller le chercher dans le stockage
            # interne : les services seraient inutilisables en automatisation.
            "uid": entree["uid"],
            "culture": fiche["nom"],
            "culture_id": fiche["id"],
            "famille": fiche["famille"],
            "zone": entree["zone"]["nom"],
            "exposition": fiche["exposition"],
            "arrosage_besoin": fiche["arrosage"]["besoin"],
            "arrosage_tous_les_jours": fiche["arrosage"]["frequence_jours"],
            "arrosage_notes": fiche["arrosage"]["notes"],
            "espacement_cm": fiche["espacement_cm"],
            "sol": fiche["sol"],
            "perenne": bool(fiche.get("perenne")),
            "conseils": fiche["conseils"],
            "date_semis": (
                infos["date_semis"].isoformat() if infos["date_semis"] else None
            ),
            "date_mise_en_place": (
                infos["date_mise_en_place"].isoformat()
                if infos["date_mise_en_place"]
                else None
            ),
            "nb_recoltes": infos["nb_recoltes"],
            "recolte_totale_g": infos["total_recolte_g"],
            "recolte_saison_g": infos.get("recolte_saison_g", 0),
            "echelonnement_jours": entree["plante"].get("echelonnement_jours"),
            "notifs_actives": entree["plante"].get("notifs", True),
        }

        etat_eau = entree.get("arrosage")
        if etat_eau is not None:
            attributs.update(
                {
                    "arrosage_concernee": etat_eau.concernee,
                    "arrosage_dernier": (
                        etat_eau.dernier.isoformat() if etat_eau.dernier else None
                    ),
                    "arrosage_prochain": (
                        etat_eau.prochain.isoformat() if etat_eau.prochain else None
                    ),
                    "arrosage_frequence_jours": etat_eau.frequence_jours,
                    "arrosage_jours_restants": etat_eau.jours_restants,
                    "arrosage_a_faire": etat_eau.a_arroser,
                    "arrosage_motif_exclusion": etat_eau.motif_exclusion,
                }
            )

        if prochaine is not None:
            attributs.update(
                {
                    "prochaine_action": prochaine.libelle,
                    "prochaine_date": prochaine.debut.isoformat(),
                    "prochaine_fin": prochaine.fin.isoformat(),
                    "jours_restants": prochaine.jours_restants(aujourdhui),
                    "fenetre_ouverte": prochaine.contient(aujourdhui),
                    # « reelle » signale une date calculee depuis le journal, et
                    # non depuis la moyenne saisonniere.
                    "calculee_depuis_le_journal": prochaine.reelle,
                }
            )
        else:
            attributs["prochaine_action"] = None

        return attributs
