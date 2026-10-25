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

from . import i18n
from .coordinator import RhizomeCoordinator
from .entity import RhizomeEntity
from .lifecycle import parse_date
from .phenology import fenetres_theoriques

PHASES_SANS_PREVISION = {"seme", "plante", "en_recolte", "termine", "perdu"}

# Nombre d'annees de previsions qu'une seule requete peut demander. Une vue
# calendrier en affiche une ; dix laissent la place a tout usage reel.
ANNEES_MAX = 10


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
        langue = self.coordinator.langue
        actions = self.coordinator.data["actions"]
        if actions:
            action = actions[0]
            return _evenement_etape(action["nom"], action["etape"], langue)

        prochaines = [
            (entree["prochaine"], entree["nom_affiche"])
            for entree in self.coordinator.data["plantes"].values()
            if entree["prochaine"] is not None
        ]
        if not prochaines:
            return None
        etape, nom = min(prochaines, key=lambda couple: couple[0].debut)
        return _evenement_etape(nom, etape, langue)

    async def async_get_events(
        self, hass: HomeAssistant, start_date: datetime, end_date: datetime
    ) -> list[CalendarEvent]:
        debut = dt_util.as_local(start_date).date()
        fin = dt_util.as_local(end_date).date()

        # La plage vient du client, sans borne : l'API calendrier de Home
        # Assistant accepte les dates qu'on lui donne. Or les previsions se
        # recalculent annee par annee, pour chaque plante — 0,9 s de boucle
        # bloquee pour cinq siecles et dix plantes, mesure. Un affichage
        # demande au plus quelques annees ; au-dela, c'est du gaspillage ou
        # un abus, et dans les deux cas la boucle d'evenements le paie.
        if fin.year - debut.year > ANNEES_MAX:
            fin = fin.replace(year=debut.year + ANNEES_MAX)

        evenements: list[CalendarEvent] = []
        langue = self.coordinator.langue

        for entree in self.coordinator.data["plantes"].values():
            nom = entree["nom_affiche"]
            plante = entree["plante"]
            culture = entree["culture"]
            phase = entree["resume"]["phase"]

            # Les faits du journal, qui peuvent remonter a plusieurs saisons.
            for evt in plante.get("evenements") or []:
                jour = parse_date(evt["date"])
                if debut <= jour <= fin:
                    evenements.append(
                        _evenement_journal(nom, culture, evt, jour, langue)
                    )

            # Les etapes calculees depuis le journal pour la saison en cours.
            for etape in entree["etapes"]:
                if etape.fin >= debut and etape.debut <= fin:
                    evenements.append(_evenement_etape(nom, etape, langue))

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
                        evenements.append(_evenement_etape(nom, etape, langue))

        # Deduplique : une etape reelle et sa prevision peuvent se superposer.
        uniques = {(e.uid, e.start): e for e in evenements}
        return sorted(uniques.values(), key=lambda e: e.start)


def _evenement_etape(nom: str, etape, langue: str = "fr") -> CalendarEvent:
    # L'`uid` reste bati sur le type et la date, jamais sur un libelle traduit :
    # changer de langue ne doit pas transformer le meme evenement en un
    # evenement neuf aux yeux des clients calendrier.
    return CalendarEvent(
        summary=i18n.t(
            langue,
            "cal_resume_etape",
            verbe=i18n.libelle_etape(langue, etape.type),
            plante=nom,
        ),
        start=etape.debut,
        # Fin exclusive pour un evenement sur la journee entiere.
        end=etape.fin + timedelta(days=1),
        description=i18n.t(
            langue,
            "cal_fenetre_reelle" if etape.reelle else "cal_fenetre_prevue",
            debut=i18n.date_longue(langue, etape.debut),
            fin=i18n.date_longue(langue, etape.fin),
        ),
        uid=f"{nom}|{etape.type}|{etape.debut.isoformat()}|{etape.source}",
    )


def _evenement_journal(
    nom: str, culture: dict, evt: dict, jour: date, langue: str = "fr"
) -> CalendarEvent:
    details = []
    if evt.get("quantite_g"):
        details.append(f"{evt['quantite_g'] / 1000:.2f} kg")
    if evt.get("cause"):
        details.append(i18n.t(langue, "cal_cause", cause=evt["cause"]))
    if evt.get("note"):
        details.append(evt["note"])

    resume = i18n.t(
        langue,
        "cal_resume_journal",
        emoji=culture["emoji"],
        evenement=i18n.libelle_evenement(langue, evt["type"]),
        plante=nom,
    )
    if evt.get("quantite_g"):
        resume += f" ({evt['quantite_g'] / 1000:.2f} kg)"

    return CalendarEvent(
        summary=resume,
        start=jour,
        end=jour + timedelta(days=1),
        description=" — ".join(details) or i18n.t(langue, "cal_note_defaut"),
        uid=f"{nom}|journal|{evt['type']}|{evt['date']}",
    )
