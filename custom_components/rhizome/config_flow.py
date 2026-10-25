"""Configuration de Rhizome.

Deux reglages seulement comptent vraiment : les dates de gelees locales, qui
calent tout le calendrier, et les destinataires des rappels. Plutot que de
demander a froid « votre derniere gelee de printemps ? », on propose des
preselections climatiques ; les dates restent modifiables pour qui les connait.
"""

from __future__ import annotations

from typing import Any

from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlow,
)
from homeassistant.core import callback
from homeassistant.helpers import selector
import voluptuous as vol

from .const import (
    CONF_ARROSAGE_ACTIF,
    CONF_GELEES_DERNIERE,
    CONF_GELEES_PREMIERE,
    CONF_NOTIFY_HEURE,
    CONF_NOTIFY_TARGETS,
    CONF_PRESET_CLIMAT,
    CONF_RAPPEL_JOURS,
    DEFAUT_ARROSAGE_ACTIF,
    DEFAUT_GELEES_DERNIERE,
    DEFAUT_GELEES_PREMIERE,
    DEFAUT_NOTIFY_HEURE,
    DEFAUT_RAPPEL_JOURS,
    DOMAIN,
    PRESET_PERSONNALISE,
    PRESETS_CLIMAT,
)

MOTIF_JOUR_MOIS = vol.Match(
    r"^(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])$",
    msg="Format attendu : MM-JJ, par exemple 04-15.",
)


def _services_mobiles(hass) -> list[selector.SelectOptionDict]:
    """Les services notify.mobile_app_*, seuls a porter des boutons d'action.

    `notify.send_message` ne transporte pas d'actions : sans ces services, un
    rappel ne pourrait pas offrir « C'est fait » et il faudrait rouvrir
    l'application pour tenir son journal.
    """
    services = hass.services.async_services().get("notify", {})
    options = [
        selector.SelectOptionDict(
            value=f"notify.{nom}",
            label=nom.removeprefix("mobile_app_").replace("_", " ").title(),
        )
        for nom in sorted(services)
        if nom.startswith("mobile_app_")
    ]
    options.append(
        selector.SelectOptionDict(
            value="persistent_notification", label="Notification dans Home Assistant"
        )
    )
    return options


def _schema(hass, valeurs: dict[str, Any]) -> vol.Schema:
    presets = [
        selector.SelectOptionDict(value="oceanique", label="Ouest océanique (Bretagne, Loire)"),
        selector.SelectOptionDict(value="nord_est", label="Nord et Est continental"),
        selector.SelectOptionDict(value="midi", label="Midi méditerranéen"),
        selector.SelectOptionDict(value="montagne", label="Montagne"),
        selector.SelectOptionDict(value=PRESET_PERSONNALISE, label="Dates personnalisées"),
    ]
    return vol.Schema(
        {
            vol.Required(
                CONF_PRESET_CLIMAT,
                default=valeurs.get(CONF_PRESET_CLIMAT, "oceanique"),
            ): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=presets, mode=selector.SelectSelectorMode.DROPDOWN
                )
            ),
            vol.Required(
                CONF_GELEES_DERNIERE,
                default=valeurs.get(CONF_GELEES_DERNIERE, DEFAUT_GELEES_DERNIERE),
            ): MOTIF_JOUR_MOIS,
            vol.Required(
                CONF_GELEES_PREMIERE,
                default=valeurs.get(CONF_GELEES_PREMIERE, DEFAUT_GELEES_PREMIERE),
            ): MOTIF_JOUR_MOIS,
            vol.Optional(
                CONF_NOTIFY_TARGETS,
                default=valeurs.get(CONF_NOTIFY_TARGETS, []),
            ): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=_services_mobiles(hass),
                    multiple=True,
                    mode=selector.SelectSelectorMode.LIST,
                )
            ),
            vol.Required(
                CONF_NOTIFY_HEURE,
                default=valeurs.get(CONF_NOTIFY_HEURE, DEFAUT_NOTIFY_HEURE),
            ): selector.TimeSelector(),
            vol.Required(
                CONF_ARROSAGE_ACTIF,
                default=valeurs.get(CONF_ARROSAGE_ACTIF, DEFAUT_ARROSAGE_ACTIF),
            ): selector.BooleanSelector(),
            vol.Required(
                CONF_RAPPEL_JOURS,
                default=valeurs.get(CONF_RAPPEL_JOURS, DEFAUT_RAPPEL_JOURS),
            ): selector.NumberSelector(
                selector.NumberSelectorConfig(
                    min=0, max=30, step=1, unit_of_measurement="jours",
                    mode=selector.NumberSelectorMode.SLIDER,
                )
            ),
        }
    )


def _appliquer_preset(saisie: dict[str, Any]) -> dict[str, Any]:
    """Le preselection climatique prime sur les dates, sauf en personnalise."""
    preset = saisie.get(CONF_PRESET_CLIMAT)
    if preset in PRESETS_CLIMAT:
        saisie[CONF_GELEES_DERNIERE] = PRESETS_CLIMAT[preset]["derniere"]
        saisie[CONF_GELEES_PREMIERE] = PRESETS_CLIMAT[preset]["premiere"]
    saisie[CONF_RAPPEL_JOURS] = int(saisie[CONF_RAPPEL_JOURS])
    return saisie


class RhizomeConfigFlow(ConfigFlow, domain=DOMAIN):
    """Un seul potager par instance : tout se gere ensuite dans le panneau."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        if user_input is not None:
            options = _appliquer_preset(dict(user_input))
            return self.async_create_entry(title="Rhizome", data={}, options=options)

        return self.async_show_form(step_id="user", data_schema=_schema(self.hass, {}))

    @staticmethod
    @callback
    def async_get_options_flow(entry: ConfigEntry) -> RhizomeOptionsFlow:
        return RhizomeOptionsFlow()


class RhizomeOptionsFlow(OptionsFlow):
    """Modifier les gelees ou les destinataires redessine tout le calendrier."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        if user_input is not None:
            # Fusion, et non remplacement : ce formulaire ne connait que les
            # reglages d'origine. Le panneau en gere d'autres (granularite des
            # rappels, affichage), qu'un passage par « Configurer » effacerait
            # s'il ecrivait seulement ses propres champs.
            fusion = {
                **self.config_entry.options,
                **_appliquer_preset(dict(user_input)),
            }
            return self.async_create_entry(data=fusion)

        return self.async_show_form(
            step_id="init",
            data_schema=_schema(self.hass, dict(self.config_entry.options)),
        )
