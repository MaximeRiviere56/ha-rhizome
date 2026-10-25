"""Calendrier du potager : ce qui est prevu, et ce qui s'est passe.

Le journal entre dans le calendrier au meme titre que les previsions. Un
potager se relit autant qu'il se planifie : savoir qu'on a seme les tomates le
7 mars l'an dernier vaut la prevision de cette annee.
"""

from __future__ import annotations

from datetime import date, datetime, timedelta

from homeassistant.components.calendar import CalendarEntity, CalendarEvent
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util import dt as dt_util

from .coordinator import RhizomeCoordinator
from .entity import RhizomeEntity
from .lifecycle import LIBELLES_EVENEMENTS, parse_date
from .phenology import fenetres_theoriques

PHASES_SANS_PREVISION = {"seme", "plante", "en_recolte", "termine", "perdu"}


PARALLEL_UPDATES = 0


async def async_setup_entry(
    hass: HomeAssistant, entry, async_add_entities: AddEntitiesCallback
) -> None:
    async_add_entities([RhizomeCalendar(entry.runtime_data)])


class RhizomeCalendar(RhizomeEntity, CalendarEntity):
    """Un seul calendrier pour tout le potager."""

    _attr_name = None
    _attr_icon = "mdi:calendar-blank-multiple"

    def __init__(self, coordinator: RhizomeCoordinator) -> None:
        super().__init__(coordinator, "calendrier")

    @property
    def event(self) -> CalendarEvent | None:
        """La prochaine echeance, toutes plantes confondues."""
        actions = self.coordinator.data["actions"]
        if actions:
            action = actions[0]
            return _evenement_etape(action["nom"], action["etape"])

        prochaines = [
            (entree["prochaine"], entree["nom_affiche"])
            for entree in self.coordinator.data["plantes"].values()
            if entree["prochaine"] is not None
        ]
        if not prochaines:
            return None
        etape, nom = min(prochaines, key=lambda couple: couple[0].debut)
        return _evenement_etape(nom, etape)

    async def async_get_events(
        self, hass: HomeAssistant, start_date: datetime, end_date: datetime
    ) -> list[CalendarEvent]:
        debut = dt_util.as_local(start_date).date()
        fin = dt_util.as_local(end_date).date()
        evenements: list[CalendarEvent] = []

        for entree in self.coordinator.data["plantes"].values():
            nom = entree["nom_affiche"]
            plante = entree["plante"]
            culture = entree["culture"]
            phase = entree["resume"]["phase"]

            # Les faits du journal, qui peuvent remonter a plusieurs saisons.
            for evt in plante.get("evenements") or []:
                jour = parse_date(evt["date"])
                if debut <= jour <= fin:
                    evenements.append(_evenement_journal(nom, culture, evt, jour))

            # Les etapes calculees depuis le journal pour la saison en cours.
            for etape in entree["etapes"]:
                if etape.fin >= debut and etape.debut <= fin:
                    evenements.append(_evenement_etape(nom, etape))

            # Les previsions saisonnieres, annee par annee. Inutiles des que la
            # plante est en terre : son calendrier reel a pris le relais.
            if phase in PHASES_SANS_PREVISION and not culture.get("perenne"):
                continue
            decalage = self.coordinator.store.decalage_zone(plante.get("zone"))
            for annee in range(debut.year, fin.year + 1):
                for etape in fenetres_theoriques(
                    culture, self.coordinator.gelees, decalage, annee
                ):
                    if etape.fin >= debut and etape.debut <= fin:
                        evenements.append(_evenement_etape(nom, etape))

        # Deduplique : une etape reelle et sa prevision peuvent se superposer.
        uniques = {(e.uid, e.start): e for e in evenements}
        return sorted(uniques.values(), key=lambda e: e.start)


def _evenement_etape(nom: str, etape) -> CalendarEvent:
    qualite = "prévu" if not etape.reelle else "d'après votre journal"
    return CalendarEvent(
        summary=f"{etape.libelle} : {nom}",
        start=etape.debut,
        # Fin exclusive pour un evenement sur la journee entiere.
        end=etape.fin + timedelta(days=1),
        description=(
            f"Fenêtre {qualite}, du {etape.debut:%d/%m/%Y} au {etape.fin:%d/%m/%Y}."
        ),
        uid=f"{nom}|{etape.type}|{etape.debut.isoformat()}|{etape.source}",
    )


def _evenement_journal(nom: str, culture: dict, evt: dict, jour: date) -> CalendarEvent:
    libelle = LIBELLES_EVENEMENTS.get(evt["type"], evt["type"])
    details = []
    if evt.get("quantite_g"):
        details.append(f"{evt['quantite_g'] / 1000:.2f} kg")
    if evt.get("cause"):
        details.append(f"cause : {evt['cause']}")
    if evt.get("note"):
        details.append(evt["note"])

    resume = f"{culture['emoji']} {libelle} : {nom}"
    if evt.get("quantite_g"):
        resume += f" ({evt['quantite_g'] / 1000:.2f} kg)"

    return CalendarEvent(
        summary=resume,
        start=jour,
        end=jour + timedelta(days=1),
        description=" — ".join(details) or "Noté au journal du potager.",
        uid=f"{nom}|journal|{evt['type']}|{evt['date']}",
    )
