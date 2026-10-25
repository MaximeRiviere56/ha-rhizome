"""Liste de taches du potager, et second chemin vers le journal.

Cocher une tache n'est pas un geste decoratif : c'est enregistrer l'evenement
correspondant au journal, donc recalculer la suite du cycle. Avec le bouton
« C'est fait » des notifications, cela fait deux chemins qui tiennent le suivi
reel sans jamais ouvrir de formulaire.
"""

from __future__ import annotations

import logging

from homeassistant.components.todo import (
    TodoItem,
    TodoItemStatus,
    TodoListEntity,
    TodoListEntityFeature,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .coordinator import RhizomeCoordinator
from .entity import RhizomeEntity
from .lifecycle import ErreurJournal
from .notifier import JOURNAL_POUR_ETAPE
from .phenology import ETAPE_RESSEMER

_LOGGER = logging.getLogger(__name__)

SEPARATEUR = "|"


PARALLEL_UPDATES = 0


async def async_setup_entry(
    hass: HomeAssistant, entry, async_add_entities: AddEntitiesCallback
) -> None:
    async_add_entities([RhizomeTodo(entry.runtime_data)])


class RhizomeTodo(RhizomeEntity, TodoListEntity):
    """Taches derivees du calcul : rien n'est stocke ici.

    Un element coche disparait de lui-meme, puisque la phase de la plante a
    avance et que l'etape n'est plus a faire.
    """

    _attr_name = None
    _attr_icon = "mdi:format-list-checks"
    _attr_supported_features = TodoListEntityFeature.UPDATE_TODO_ITEM

    def __init__(self, coordinator: RhizomeCoordinator) -> None:
        super().__init__(coordinator, "taches")

    @property
    def todo_items(self) -> list[TodoItem]:
        aujourdhui = self.coordinator.data["calcule_le"]
        elements: list[TodoItem] = []

        for action in self.coordinator.data["actions"]:
            etape = action["etape"]
            if etape.type not in JOURNAL_POUR_ETAPE and etape.type != ETAPE_RESSEMER:
                continue
            elements.append(
                TodoItem(
                    uid=SEPARATEUR.join(
                        (action["uid"], etape.type, etape.debut.isoformat())
                    ),
                    summary=f"{action['emoji']} {etape.libelle} : {action['nom']}",
                    status=TodoItemStatus.NEEDS_ACTION,
                    due=max(etape.debut, aujourdhui),
                    description=(
                        f"{action['zone']} — fenêtre jusqu'au {etape.fin:%d/%m}."
                    ),
                )
            )
        return elements

    async def async_update_todo_item(self, item: TodoItem) -> None:
        """Cocher enregistre l'evenement ; decocher ne defait rien.

        L'annulation passe par `rhizome.annuler_dernier_evenement`, qui sait
        exactement quel evenement retirer — une case decochee, non.
        """
        if item.status != TodoItemStatus.COMPLETED or not item.uid:
            return

        morceaux = item.uid.split(SEPARATEUR)
        if len(morceaux) != 3:
            return
        uid, type_etape, _ = morceaux

        store = self.coordinator.store
        jour = self.coordinator.data["calcule_le"]

        if type_etape == ETAPE_RESSEMER:
            mutation = lambda: store.ressemer(uid, jour)  # noqa: E731
        else:
            inscription = JOURNAL_POUR_ETAPE.get(type_etape)
            if inscription is None:
                return
            type_evt, details = inscription
            mutation = lambda: store.noter(uid, type_evt, jour, **details)  # noqa: E731

        try:
            await self.coordinator.async_appliquer(mutation)
        except ErreurJournal as err:
            _LOGGER.debug("Tache non enregistrable (%s) : %s", uid, err)
