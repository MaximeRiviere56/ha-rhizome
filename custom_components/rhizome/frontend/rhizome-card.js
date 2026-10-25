/**
 * Carte Lovelace « Rhizome ».
 *
 * Elle lit les attributs des capteurs déjà présents : aucune requête
 * supplémentaire, donc elle s'affiche instantanément sur un tableau de bord
 * déjà chargé. Les boutons écrivent par les mêmes commandes que le panneau.
 *
 * Usage :
 *   type: custom:rhizome-card
 *   titre: Au potager
 *   vue: tout        # tout (défaut) · actions · arrosage
 *   max: 8
 */

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
  if (enCours) return "c'est le moment";
  if (jours === 0) return "aujourd'hui";
  if (jours === 1) return "demain";
  if (jours > 1) return `dans ${jours} jours`;
  return `depuis ${Math.abs(jours)} jours`;
};

const quandEau = (jours) => {
  if (jours > 1) return `depuis ${jours} jours`;
  if (jours === 1) return "depuis hier";
  if (jours === 0) return "aujourd'hui";
  return `dans ${-jours} j`;
};

class RhizomeCard extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
  }

  setConfig(config) {
    this._config = { titre: "Au potager", vue: "tout", max: 8, ...config };
    this._rendu = false;
  }

  getCardSize() {
    return 1 + Math.min(this._lignes().length, this._config?.max ?? 8);
  }

  set hass(hass) {
    this._hass = hass;
    this._rendre();
  }

  /** Le capteur d'actions est détecté si l'utilisateur ne l'a pas nommé :
   *  une entité de plus à saisir pour rien est une entité de trop. */
  _entiteActions() {
    if (this._config?.entity) return this._config.entity;
    return Object.keys(this._hass?.states || {}).find(
      (id) => id.startsWith("sensor.") && id.endsWith("_actions_a_mener")
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
      this._erreur = err?.message || "Action refusée.";
      this._rendu = false;
      this._rendre();
    }
  }

  _rendre() {
    if (!this._hass || !this._config) return;

    const vue = this._config.vue;
    const actions = vue === "arrosage" ? [] : this._actions().slice(0, this._config.max);
    const eau = vue === "actions" ? [] : this._plantesArrosables();
    const aArroser = eau.filter((p) => p.aFaire);
    const reste = eau.filter((p) => !p.aFaire).slice(0, Math.max(0, this._config.max - aArroser.length));

    const signature = JSON.stringify([actions, aArroser, reste, this._erreur]);
    if (this._rendu && signature === this._signature) return;
    this._signature = signature;
    this._rendu = true;

    if (!this._entiteActions()) {
      this.shadowRoot.innerHTML = `<ha-card header="${echappe(this._config.titre)}">
          <div class="vide">Capteur du potager introuvable. L'intégration
          Rhizome est-elle installée ?</div>
        </ha-card>`;
      return;
    }

    const ligneEau = (p) => `
      <div class="ligne ${p.aFaire ? "urgent" : ""}">
        <ha-icon icon="mdi:watering-can" class="goutte"></ha-icon>
        <div class="corps">
          <div class="nom">${echappe(p.nom)}</div>
          <div class="detail">
            ${p.aFaire ? `<span class="verbe">À arroser</span> · ` : ""}${quandEau(
      p.jours
    )} · ${echappe(p.zone)}${
      p.frequence ? ` · tous les ${p.frequence} j` : ""
    }
          </div>
        </div>
        <button data-eau="${p.uid}">Arrosé</button>
      </div>`;

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
        .goutte { color: var(--rhizome-eau, #29b6f6); }
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
      <ha-card header="${echappe(this._config.titre)}">
        ${this._erreur ? `<div class="erreur">${echappe(this._erreur)}</div>` : ""}

        ${
          actions.length
            ? `<div class="section">À faire</div>` +
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
                    ? `<button data-action="${i}">Fait</button>`
                    : ""
                }
              </div>`
                )
                .join("")
            : ""
        }

        ${
          aArroser.length
            ? `<div class="section">À arroser · ${aArroser.length}</div>` +
              aArroser.map(ligneEau).join("") +
              (aArroser.length > 1
                ? `<div class="ligne" style="justify-content:center">
                     <button class="discret" data-eau-tout="${aArroser
                       .map((p) => p.uid)
                       .join(",")}">
                       Tout arroser (${aArroser.length})
                     </button>
                   </div>`
                : "")
            : ""
        }

        ${
          reste.length
            ? `<div class="section">Prochains arrosages</div>` +
              reste.map(ligneEau).join("")
            : ""
        }

        ${
          !actions.length && !eau.length
            ? `<div class="vide">Rien à faire au potager aujourd'hui 🌿</div>`
            : ""
        }

        <a class="lien" href="/rhizome">Ouvrir Rhizome →</a>
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
        this._commander(
          { type: "rhizome/arroser", uid: bouton.dataset.eau },
          bouton
        );
      })
    );

    this.shadowRoot.querySelectorAll("button[data-eau-tout]").forEach((bouton) =>
      bouton.addEventListener("click", () => {
        this._erreur = null;
        this._commander(
          { type: "rhizome/arroser", uid: bouton.dataset.eauTout.split(",") },
          bouton
        );
      })
    );
  }

  static getStubConfig() {
    return { titre: "Au potager", vue: "tout", max: 8 };
  }
}

customElements.define("rhizome-card", RhizomeCard);

window.customCards = window.customCards || [];
window.customCards.push({
  type: "rhizome-card",
  name: "Rhizome",
  description:
    "Ce qu'il y a à semer, repiquer, récolter ou arroser, avec un bouton pour le noter.",
  preview: true,
});
