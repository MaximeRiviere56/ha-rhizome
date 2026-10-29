/**
 * Carte Lovelace « Rhizome ».
 *
 * Elle lit les attributs des capteurs déjà présents : aucune requête
 * supplémentaire, donc elle s'affiche instantanément sur un tableau de bord
 * déjà chargé. Les boutons écrivent par les mêmes commandes que le panneau.
 *
 * Usage :
 *   type: custom:rhizome-card
 *   titre: Au potager   # facultatif : traduit par défaut
 *   vue: tout           # tout (défaut) · actions · arrosage
 *   max: 8
 *
 * Langue : la carte n'interroge pas l'intégration, elle lit des états. Elle
 * n'a donc pas accès au réglage de Rhizome et suit `hass.language`, la langue
 * de qui regarde le tableau de bord. Les deux coïncident dès que le réglage
 * vaut « auto », qui est le défaut. Ce qu'elle affiche de nommé — le nom de la
 * plante, le verbe de l'étape, la zone — vient de toute façon des attributs du
 * capteur, donc déjà traduit par le serveur : seuls ses propres libellés sont
 * concernés.
 */

const LANGUE_DEFAUT = "fr";

const TEXTES = {
  fr: {
    titreDefaut: "Au potager",
    sectionAFaire: "À faire",
    sectionAArroser: "À arroser · {nombre}",
    sectionProchains: "Prochains arrosages",
    // L'etat se lit dans la pastille, au passe quand c'est un fait ; le bouton
    // ne porte que le geste, a l'imperatif.
    eauChipRetard: "À arroser · {jours} j de retard",
    eauChipAujourdhui: "À arroser aujourd'hui",
    eauChipOk: "Arrosé · prochain dans {jours} j",
    eauChipFait: "Arrosé · c'est noté",
    boutonArroser: "Arroser",
    boutonFait: "Fait",
    boutonToutArroser: "Tout arroser ({nombre})",
    tousLesNJours: "tous les {jours} j",
    quandMaintenant: "c'est le moment",
    quandAujourdhui: "aujourd'hui",
    quandDemain: "demain",
    quandDans: "dans {jours} jours",
    quandDepuis: "depuis {jours} jours",
    rienAFaire: "Rien à faire au potager aujourd'hui 🌿",
    capteurIntrouvable:
      "Capteur du potager introuvable. L'intégration Rhizome est-elle installée ?",
    actionRefusee: "Action refusée.",
    ouvrirRhizome: "Ouvrir Rhizome →",
    descriptionCarte:
      "Ce qu'il y a à semer, repiquer, récolter ou arroser, avec un bouton pour le noter.",
  },
  en: {
    titreDefaut: "In the garden",
    sectionAFaire: "To do",
    sectionAArroser: "Needs watering · {nombre}",
    sectionProchains: "Next waterings",
    eauChipRetard: "Needs water · {jours} d overdue",
    eauChipAujourdhui: "Needs water today",
    eauChipOk: "Watered · next in {jours} d",
    eauChipFait: "Watered · recorded",
    boutonArroser: "Water",
    boutonFait: "Done",
    boutonToutArroser: "Water all ({nombre})",
    tousLesNJours: "every {jours} d",
    quandMaintenant: "now is the time",
    quandAujourdhui: "today",
    quandDemain: "tomorrow",
    quandDans: "in {jours} days",
    quandDepuis: "{jours} days ago",
    rienAFaire: "Nothing to do in the garden today 🌿",
    capteurIntrouvable:
      "Garden sensor not found. Is the Rhizome integration installed?",
    actionRefusee: "Action refused.",
    ouvrirRhizome: "Open Rhizome →",
    descriptionCarte:
      "What there is to sow, transplant, harvest or water, with a button to record it.",
  },
};

/** Langue courante, au niveau du module : une carte ne vit jamais seule sur un
 *  tableau de bord, et elles partagent toutes la langue de Home Assistant. */
let LANGUE = LANGUE_DEFAUT;

function T(cle, params) {
  const table = TEXTES[LANGUE] || TEXTES[LANGUE_DEFAUT];
  let texte = table[cle] ?? TEXTES[LANGUE_DEFAUT][cle];
  if (texte == null) return cle;
  if (params) {
    for (const [nom, valeur] of Object.entries(params)) {
      texte = texte.replaceAll(`{${nom}}`, String(valeur));
    }
  }
  return texte;
}

/** Retient la base de la langue de Home Assistant : « en-GB » devient « en ».
 *  Renvoie vrai si elle a change, pour declencher un nouveau rendu. */
function definirLangue(langueHass) {
  const base = String(langueHass || "")
    .replace("_", "-")
    .split("-")[0]
    .toLowerCase();
  const retenue = TEXTES[base] ? base : LANGUE_DEFAUT;
  if (retenue === LANGUE) return false;
  LANGUE = retenue;
  return true;
}

const EVT_POUR_ETAPE = {
  semis_interieur: { evenement: "seme", mode: "interieur" },
  semis_direct: { evenement: "seme", mode: "direct" },
  repiquage: { evenement: "repique" },
  plantation: { evenement: "plante" },
  recolte: { evenement: "recolte" },
  ressemer: { commande: "rhizome/ressemer" },
};

// Voir la note de `rhizome-panel.js` : `textContent` puis `innerHTML`
// n'echappe pas les guillemets, et cette fonction sert aussi a l'interieur
// d'attributs (`<ha-card header="...">`).
const ENTITES = {
  "&": "&amp;",
  "<": "&lt;",
  ">": "&gt;",
  '"': "&quot;",
  "'": "&#39;",
};

const echappe = (texte) =>
  texte == null ? "" : String(texte).replace(/[&<>"']/g, (c) => ENTITES[c]);

const quand = (jours, enCours) => {
  if (enCours) return T("quandMaintenant");
  if (jours === 0) return T("quandAujourdhui");
  if (jours === 1) return T("quandDemain");
  if (jours > 1) return T("quandDans", { jours });
  return T("quandDepuis", { jours: Math.abs(jours) });
};

/** Les trois etats d'arrosage, chacun avec son icone et son fond.
 *
 *  Un bouton bleu « Arrosé » posait la mauvaise question : etait-ce un constat
 *  ou une commande ? L'etat vit desormais dans une pastille — au passe quand
 *  c'est un fait — et le bouton ne porte plus que le geste. L'icone tranche
 *  sans qu'on lise : alerte, arrosoir, ou coche.
 *
 *  `retard` compte les jours de retard, donc l'oppose de `jours_restants` :
 *  cette carte les a deja inverses en construisant sa liste. */
const NIVEAUX_EAU = {
  retard: { icone: "mdi:water-alert", cle: "eauChipRetard" },
  jour: { icone: "mdi:watering-can", cle: "eauChipAujourdhui" },
  ok: { icone: "mdi:water-check", cle: "eauChipOk" },
  fait: { icone: "mdi:check-circle", cle: "eauChipFait" },
};

const niveauEau = (retard) => (retard > 0 ? "retard" : retard === 0 ? "jour" : "ok");

const pastilleEau = (retard, confirme = false) => {
  const niveau = confirme ? "fait" : niveauEau(retard);
  const { icone, cle } = NIVEAUX_EAU[niveau];
  return `<span class="chip-eau" data-niveau="${niveau}">
      <ha-icon icon="${icone}"></ha-icon>
      ${T(cle, { jours: Math.abs(retard) })}
    </span>`;
};

class RhizomeCard extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
  }

  setConfig(config) {
    // Le titre n'est pas pose ici mais au rendu : `setConfig` est appele avant
    // que `hass` arrive, donc avant que la langue soit connue. Un titre fourni
    // par l'utilisateur, lui, l'emporte toujours.
    this._config = { vue: "tout", max: 8, ...config };
    this._rendu = false;
  }

  getCardSize() {
    return 1 + Math.min(this._lignes().length, this._config?.max ?? 8);
  }

  set hass(hass) {
    this._hass = hass;
    if (definirLangue(hass?.language)) this._rendu = false;
    this._rendre();
  }

  /** Le capteur d'actions est détecté si l'utilisateur ne l'a pas nommé :
   *  une entité de plus à saisir pour rien est une entité de trop.
   *
   *  La détection porte sur les attributs et non sur le nom de l'entité.
   *  Chercher le suffixe « _actions_a_mener » ne tenait que tant que
   *  l'intégration était francophone : une installation créée en anglais
   *  nomme la même entité `sensor.rhizome_tasks_due`, et la carte restait
   *  vide sans rien dire. `actions` et `nb_plantes` ensemble n'existent que
   *  sur ce capteur. */
  _entiteActions() {
    if (this._config?.entity) return this._config.entity;
    const etats = this._hass?.states || {};
    return Object.keys(etats).find(
      (id) =>
        id.startsWith("sensor.") &&
        Array.isArray(etats[id]?.attributes?.actions) &&
        etats[id].attributes.nb_plantes !== undefined
    );
  }

  _actions() {
    const etat = this._hass?.states?.[this._entiteActions()];
    return etat?.attributes?.actions || [];
  }

  /** Les plantes concernées par l'arrosage, les plus assoiffées d'abord.
   *
   *  On balaie les capteurs de plantes plutôt que le capteur « À arroser » :
   *  celui-ci ne liste que ce qui est dû, alors que la carte doit montrer
   *  tout le potager, avec son bouton à portée de pouce. */
  _plantesArrosables() {
    const etats = this._hass?.states || {};
    // On passe par les clés : elles portent toujours l'entity_id, là où
    // l'objet d'état ne le garantit pas.
    return Object.entries(etats)
      .filter(
        ([id, e]) =>
          id.startsWith("sensor.") &&
          e?.attributes?.uid &&
          e.attributes.arrosage_concernee
      )
      .map(([, e]) => ({
        uid: e.attributes.uid,
        nom: e.attributes.culture,
        zone: e.attributes.zone,
        jours: -e.attributes.arrosage_jours_restants,
        aFaire: !!e.attributes.arrosage_a_faire,
        dernier: e.attributes.arrosage_dernier,
        frequence: e.attributes.arrosage_frequence_jours,
        nomComplet: e.attributes.friendly_name,
      }))
      .sort((a, b) => b.jours - a.jours);
  }

  _lignes() {
    const vue = this._config?.vue || "tout";
    return [
      ...(vue !== "arrosage" ? this._actions() : []),
      ...(vue !== "actions" ? this._plantesArrosables() : []),
    ];
  }

  async _commander(message, bouton) {
    bouton.disabled = true;
    try {
      await this._hass.callWS(message);
    } catch (err) {
      bouton.disabled = false;
      this._erreur = err?.message || T("actionRefusee");
      this._rendu = false;
      this._rendre();
    }
  }

  /** Note l'arrosage, et retient quelques secondes que ce clic a ete pris.
   *
   *  Les etats arrivent par le flux de Home Assistant : la ligne va changer
   *  d'elle-meme, mais avec un simple decalage du compte a rebours, que
   *  personne ne remarque. La pastille verte, elle, se voit. */
  async _arroser(uids, bouton) {
    await this._commander({ type: "rhizome/arroser", uid: uids }, bouton);
    if (this._erreur) return;
    this._eauConfirmee = new Set(uids);
    clearTimeout(this._minuteurEau);
    this._minuteurEau = setTimeout(() => {
      this._eauConfirmee = null;
      this._rendu = false;
      this._rendre();
    }, 4000);
    this._rendu = false;
    this._rendre();
  }

  _rendre() {
    if (!this._hass || !this._config) return;

    const vue = this._config.vue;
    const actions = vue === "arrosage" ? [] : this._actions().slice(0, this._config.max);
    const eau = vue === "actions" ? [] : this._plantesArrosables();
    const aArroser = eau.filter((p) => p.aFaire);
    const reste = eau.filter((p) => !p.aFaire).slice(0, Math.max(0, this._config.max - aArroser.length));

    const titre = this._config.titre ?? T("titreDefaut");
    const signature = JSON.stringify([
      actions, aArroser, reste, this._erreur, LANGUE,
      [...(this._eauConfirmee || [])],
    ]);
    if (this._rendu && signature === this._signature) return;
    this._signature = signature;
    this._rendu = true;

    if (!this._entiteActions()) {
      this.shadowRoot.innerHTML = `<ha-card header="${echappe(titre)}">
          <div class="vide">${T("capteurIntrouvable")}</div>
        </ha-card>`;
      return;
    }

    const ligneEau = (p) => {
      const confirme = this._eauConfirmee?.has(p.uid);
      return `
      <div class="ligne">
        <div class="corps">
          <div class="nom">${echappe(p.nom)}</div>
          <div class="detail etat">
            ${pastilleEau(p.jours, confirme)}
          </div>
          <div class="detail">
            ${echappe(p.zone)}${
        p.frequence ? ` · ${T("tousLesNJours", { jours: p.frequence })}` : ""
      }
          </div>
        </div>
        <button class="${
          p.aFaire && !confirme ? "" : "discret"
        }" data-eau="${p.uid}" aria-label="${T("boutonArroser")}">
          ${T("boutonArroser")}
        </button>
      </div>`;
    };

    this.shadowRoot.innerHTML = `
      <style>
        ha-card { overflow: hidden; }
        .section {
          padding: 10px 16px 4px; font-size: 12px; font-weight: 500;
          text-transform: uppercase; letter-spacing: .5px;
          color: var(--secondary-text-color);
        }
        .ligne {
          display: flex; align-items: center; gap: 12px;
          padding: 10px 16px; border-top: 1px solid var(--divider-color);
        }
        .section + .ligne { border-top: 0; }
        .emoji { font-size: 24px; line-height: 1; }
        .detail.etat { margin-top: 4px; }
        /* Trois fonds, trois icones : « c'est fait » et « c'est a faire » ne
           doivent pas se ressembler. Texte en couleur de premier plan, comme
           les badges de Home Assistant — teinte sur teinte passe mal en
           theme sombre. */
        .chip-eau {
          display: inline-flex; align-items: center; gap: 5px;
          font-size: 12px; font-weight: 500; padding: 3px 9px; border-radius: 999px;
          background: color-mix(in srgb, var(--secondary-text-color) 14%, transparent);
          color: var(--primary-text-color); white-space: nowrap;
        }
        .chip-eau ha-icon {
          --mdc-icon-size: 15px; color: var(--secondary-text-color); flex: 0 0 auto;
        }
        .chip-eau[data-niveau="retard"] {
          background: color-mix(in srgb, var(--warning-color, #ef6c00) 26%, transparent);
        }
        .chip-eau[data-niveau="retard"] ha-icon { color: var(--warning-color, #ef6c00); }
        .chip-eau[data-niveau="jour"] {
          background: color-mix(in srgb, var(--rhizome-eau, #29b6f6) 24%, transparent);
        }
        .chip-eau[data-niveau="jour"] ha-icon,
        .chip-eau[data-niveau="ok"] ha-icon { color: var(--rhizome-eau, #29b6f6); }
        .chip-eau[data-niveau="fait"] {
          background: color-mix(in srgb, var(--success-color, #7cb342) 30%, transparent);
        }
        .chip-eau[data-niveau="fait"] ha-icon { color: var(--success-color, #7cb342); }
        .corps { flex: 1; min-width: 0; }
        .nom { font-size: 15px; }
        .detail { font-size: 12px; color: var(--secondary-text-color); margin-top: 1px; }
        .urgent .verbe { color: var(--warning-color, #ef6c00); font-weight: 500; }
        button {
          border: 0; border-radius: 999px; padding: 7px 14px; cursor: pointer;
          background: var(--primary-color); color: var(--text-primary-color, #fff);
          font-size: 13px; font-weight: 500; font-family: inherit;
        }
        button:disabled { opacity: .5; cursor: default; }
        button.discret {
          background: var(--divider-color); color: var(--primary-text-color);
        }
        .vide { padding: 20px 16px; color: var(--secondary-text-color); text-align: center; }
        .erreur { padding: 10px 16px; color: var(--error-color); font-size: 13px; }
        a.lien {
          display: block; padding: 10px 16px; text-align: center;
          color: var(--primary-color); text-decoration: none; font-size: 13px;
          border-top: 1px solid var(--divider-color);
        }
      </style>
      <ha-card header="${echappe(titre)}">
        ${this._erreur ? `<div class="erreur">${echappe(this._erreur)}</div>` : ""}

        ${
          actions.length
            ? `<div class="section">${T("sectionAFaire")}</div>` +
              actions
                .map(
                  (a, i) => `
              <div class="ligne ${a.en_cours ? "urgent" : ""}">
                <div class="emoji">${echappe(a.emoji || "🌱")}</div>
                <div class="corps">
                  <div class="nom">${echappe(a.plante)}</div>
                  <div class="detail">
                    <span class="verbe">${echappe(a.action)}</span> ·
                    ${quand(a.jours_restants, a.en_cours)} · ${echappe(a.zone)}
                  </div>
                </div>
                ${
                  EVT_POUR_ETAPE[a.etape]
                    ? `<button data-action="${i}">${T("boutonFait")}</button>`
                    : ""
                }
              </div>`
                )
                .join("")
            : ""
        }

        ${
          aArroser.length
            ? `<div class="section">${T("sectionAArroser", {
                nombre: aArroser.length,
              })}</div>` +
              aArroser.map(ligneEau).join("") +
              (aArroser.length > 1
                ? `<div class="ligne" style="justify-content:center">
                     <button class="discret" data-eau-tout="${aArroser
                       .map((p) => p.uid)
                       .join(",")}">
                       ${T("boutonToutArroser", { nombre: aArroser.length })}
                     </button>
                   </div>`
                : "")
            : ""
        }

        ${
          reste.length
            ? `<div class="section">${T("sectionProchains")}</div>` +
              reste.map(ligneEau).join("")
            : ""
        }

        ${
          !actions.length && !eau.length
            ? `<div class="vide">${T("rienAFaire")}</div>`
            : ""
        }

        <a class="lien" href="/rhizome">${T("ouvrirRhizome")}</a>
      </ha-card>`;

    this.shadowRoot.querySelectorAll("button[data-action]").forEach((bouton) =>
      bouton.addEventListener("click", () => {
        this._erreur = null;
        const a = actions[Number(bouton.dataset.action)];
        const corr = EVT_POUR_ETAPE[a.etape];
        if (!corr) return;
        this._commander(
          corr.commande
            ? { type: corr.commande, uid: a.uid }
            : {
                type: "rhizome/noter",
                uid: a.uid,
                evenement: corr.evenement,
                ...(corr.mode ? { mode: corr.mode } : {}),
              },
          bouton
        );
      })
    );

    this.shadowRoot.querySelectorAll("button[data-eau]").forEach((bouton) =>
      bouton.addEventListener("click", () => {
        this._erreur = null;
        this._arroser([bouton.dataset.eau], bouton);
      })
    );

    this.shadowRoot.querySelectorAll("button[data-eau-tout]").forEach((bouton) =>
      bouton.addEventListener("click", () => {
        this._erreur = null;
        this._arroser(bouton.dataset.eauTout.split(","), bouton);
      })
    );
  }

  static getStubConfig() {
    return { vue: "tout", max: 8 };
  }
}

customElements.define("rhizome-card", RhizomeCard);

window.customCards = window.customCards || [];
window.customCards.push({
  type: "rhizome-card",
  name: "Rhizome",
  // Le selecteur de cartes est construit au chargement du tableau de bord,
  // avant qu'aucune carte n'ait recu `hass` : on y lit donc la langue du
  // navigateur, seule disponible a cet instant.
  description: (() => {
    definirLangue(navigator.language);
    return T("descriptionCarte");
  })(),
  preview: true,
});
