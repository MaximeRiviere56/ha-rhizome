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

from . import i18n
from .catalog import localiser, nom_localise
from .coordinator import RhizomeCoordinator
from .entity import RhizomeEntity, RhizomePlanteEntity, suivre_les_plantes
from .serialisation import libelle_phase

PLATEFORME = "sensor"
SUFFIXE = "etat"

# Rien a interroger : le calcul est local, et les entites se rafraichissent
# ensemble depuis le coordinateur.
PARALLEL_UPDATES = 0


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

    # Nom pose a l'instanciation, et non une `translation_key` : Home Assistant
    # derive alors l'entity_id du nom de la langue par defaut de l'integration,
    # ce qui le ferait changer selon le canal par lequel l'entite est creee. Le
    # nom affiche suit la langue de l'installation ; l'entity_id, lui, est fige
    # a la creation de l'entite et ne bouge plus — c'est ce qui rend ce
    # reglage sans danger pour les automatisations existantes.
    _attr_icon = "mdi:sprout"
    _attr_native_unit_of_measurement = "actions"
    _attr_state_class = SensorStateClass.MEASUREMENT
    # La liste change chaque jour et ne vaut rien en historique : l'archiver
    # ferait grossir la base pour une courbe que personne ne lira.
    _unrecorded_attributes = frozenset({"actions"})

    def __init__(self, coordinator: RhizomeCoordinator) -> None:
        super().__init__(coordinator, "actions")
        self._attr_name = i18n.t(coordinator.langue, "entite_actions")

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
                    "action": i18n.libelle_etape(
                        self.coordinator.langue, action["etape"].type
                    ),
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

    _attr_icon = "mdi:basket"
    _attr_device_class = SensorDeviceClass.WEIGHT
    _attr_native_unit_of_measurement = UnitOfMass.KILOGRAMS
    _attr_state_class = SensorStateClass.TOTAL
    _attr_suggested_display_precision = 2
    _unrecorded_attributes = frozenset({"par_culture_g"})

    def __init__(self, coordinator: RhizomeCoordinator) -> None:
        super().__init__(coordinator, "recolte")
        self._attr_name = i18n.t(coordinator.langue, "entite_recolte")

    @property
    def native_value(self) -> float:
        return round(self.coordinator.data["total_recolte_g"] / 1000, 3)

    @property
    def extra_state_attributes(self) -> dict:
        par_culture: dict[str, int] = {}
        for entree in self.coordinator.data["plantes"].values():
            grammes = entree["resume"].get("recolte_saison_g", 0)
            if grammes:
                nom = nom_localise(entree["culture"], self.coordinator.langue)
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

    _attr_icon = "mdi:watering-can"
    _attr_native_unit_of_measurement = "plantes"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _unrecorded_attributes = frozenset({"plantes"})

    def __init__(self, coordinator: RhizomeCoordinator) -> None:
        super().__init__(coordinator, "arrosage")
        self._attr_name = i18n.t(coordinator.langue, "entite_arrosage")

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
    # La fiche de culture est fixe, et le compte a rebours change chaque jour :
    # ni l'une ni l'autre n'a d'interet en base. Seul l'etat (la phase) est
    # historise, et c'est bien lui qui raconte la saison.
    _unrecorded_attributes = frozenset(
        {
            "conseils",
            "sol",
            "arrosage_notes",
            "arrosage_besoin",
            "arrosage_tous_les_jours",
            "arrosage_prochain",
            "arrosage_jours_restants",
            "arrosage_motif_exclusion",
            "espacement_cm",
            "jours_restants",
            "prochaine_date",
            "prochaine_fin",
            "fenetre_ouverte",
        }
    )

    def __init__(self, coordinator: RhizomeCoordinator, uid: str) -> None:
        super().__init__(coordinator, uid, SUFFIXE)
        # Les options d'un capteur `enum` doivent contenir tous les etats qu'il
        # peut prendre : traduire la phase sans traduire cette liste rendrait
        # l'entite invalide a chaque changement d'etat.
        self._attr_options = i18n.phases_libellees(coordinator.langue)

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
        if entree is None:
            return None
        return libelle_phase(entree["resume"]["phase"], self.coordinator.langue)

    @property
    def extra_state_attributes(self) -> dict:
        entree = self.entree
        if entree is None:
            return {}

        langue = self.coordinator.langue
        fiche = localiser(entree["culture"], langue)
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
                    "arrosage_motif_exclusion": (
                        i18n.t(langue, etat_eau.motif_cle)
                        if etat_eau.motif_cle
                        else etat_eau.motif_exclusion
                    ),
                }
            )

        if prochaine is not None:
            attributs.update(
                {
                    "prochaine_action": i18n.libelle_etape(langue, prochaine.type),
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
