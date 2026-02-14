/**
 * Maico VMC Card - Custom Lovelace Card for Maico WS VMC Integration
 * Auto-discovers Maico entities and provides a beautiful UI
 */

const LitElement = customElements.get("hui-masonry-view")
  ? Object.getPrototypeOf(customElements.get("hui-masonry-view"))
  : Object.getPrototypeOf(customElements.get("hui-view"));
const html = LitElement.prototype.html;
const css = LitElement.prototype.css;

// User's custom SVG for heat exchanger
const EXCHANGER_SVG = `
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 50 50">
    <g transform="matrix(0.62 0 0 0.53 24 25)">
        <path style="stroke: rgb(114,114,114); stroke-width: 3; stroke-dasharray: none; stroke-linecap: butt; stroke-dashoffset: 0; stroke-linejoin: miter; stroke-miterlimit: 4; fill: rgb(242,242,242); fill-rule: nonzero; opacity: 1;" vector-effect="non-scaling-stroke" transform=" translate(0, 0)" d="M 16.23943 -28.12732 L 32.47864 0 L 16.23943 28.12732 L -16.23943 28.12732 L -32.47864 0 L -16.23943 -28.12732 z" stroke-linecap="round" />
    </g>
    <g transform="matrix(0.2 0 0 0.3 25.5 24)">
        <path style="stroke: rgb(49,168,247); stroke-width: 4; stroke-dasharray: none; stroke-linecap: butt; stroke-dashoffset: 0; stroke-linejoin: miter; stroke-miterlimit: 4; fill: rgb(255,255,255); fill-opacity: 0; fill-rule: nonzero; opacity: 1;" vector-effect="non-scaling-stroke" transform=" translate(0, 0)" d="M -110 40 L -90 40 L 90 -40 L 110 -40" stroke-linecap="round" />
    </g>
    <g transform="matrix(0 -0.1 0.06 0 2.5 36)">
        <path style="stroke: none; stroke-width: 1; stroke-dasharray: none; stroke-linecap: butt; stroke-dashoffset: 0; stroke-linejoin: miter; stroke-miterlimit: 4; fill: rgb(49,168,247); fill-rule: nonzero; opacity: 1;" vector-effect="non-scaling-stroke" transform=" translate(-40, -40)" d="M 60 40 L 80 80 L 40 80 L 0 80 L 20 40 L 40 0 L 60 40 z" stroke-linecap="round" />
    </g>
    <g transform="matrix(0 -0.1 -0.06 0 47.5 36)">
        <path style="stroke: none; stroke-width: 1; stroke-dasharray: none; stroke-linecap: butt; stroke-dashoffset: 0; stroke-linejoin: miter; stroke-miterlimit: 4; fill: rgb(49,168,247); fill-rule: nonzero; opacity: 1;" vector-effect="non-scaling-stroke" transform=" translate(-40, -40)" d="M 60 40 L 80 80 L 40 80 L 0 80 L 20 40 L 40 0 L 60 40 z" stroke-linecap="round" />
    </g>
    <g transform="matrix(-0.19 0 0 0.3 24 24)">
        <path style="stroke: rgb(49,168,247); stroke-width: 4; stroke-dasharray: none; stroke-linecap: butt; stroke-dashoffset: 0; stroke-linejoin: miter; stroke-miterlimit: 4; fill: none; fill-rule: nonzero; opacity: 1;" vector-effect="non-scaling-stroke" transform=" translate(0, 0)" d="M -110 40 L -90 40 L 90 -40 L 110 -40" stroke-linecap="round" />
    </g>
</svg>
`;

// Translations
const TRANSLATIONS = {
  en: {
    efficiency: "Efficiency",
    temp_outdoor: "Outdoor Air",
    temp_exhaust: "Exhaust Air",
    temp_extract: "Extract Air",
    temp_supply: "Supply Air",
    open: "Open",
    closed: "Closed",
    filter_device: "Device Filter",
    filter_outdoor: "Outdoor Filter",
    filter_room: "Room Filter",
    mode_off: "Off",
    mode_auto: "Humidity",
    mode_low: "Reduced",
    mode_medium: "Normal",
    mode_high: "Intensive",
    power: "Power",
    ventilation: "Ventilation",
    boost: "Boost",
  },
  fr: {
    efficiency: "Rendement",
    temp_outdoor: "Air ext",
    temp_exhaust: "Air rejeté",
    temp_extract: "Air extrait",
    temp_supply: "Air insufflé",
    open: "Ouvert",
    closed: "Fermé",
    filter_device: "Filtre appareil",
    filter_outdoor: "Filtre extérieur",
    filter_room: "Filtre pièce",
    mode_off: "Arrêt",
    mode_auto: "Humidité",
    mode_low: "Réduit",
    mode_medium: "Normal",
    mode_high: "Intensif",
    power: "Alimentation",
    ventilation: "Ventilation",
    boost: "Surventilation",
  },
  de: {
    efficiency: "Wirkungsgrad",
    temp_outdoor: "Außenluft",
    temp_exhaust: "Fortluft",
    temp_extract: "Abluft",
    temp_supply: "Zuluft",
    open: "Offen",
    closed: "Geschlossen",
    filter_device: "Gerätefilter",
    filter_outdoor: "Außenfilter",
    filter_room: "Raumfilter",
    mode_off: "Aus",
    mode_auto: "Feuchte",
    mode_low: "Reduziert",
    mode_medium: "Normal",
    mode_high: "Intensiv",
    power: "Stromversorgung",
    ventilation: "Lüftung",
    boost: "Stoßlüftung",
  }
};

class MaicoVMCCard extends LitElement {
  static get properties() {
    return {
      hass: { type: Object },
      config: { type: Object },
      _entities: { type: Object },
      _history: { type: Array },
      _drawerOpen: { type: Boolean },
    };
  }

  _localize(key) {
    const lang = this.hass?.language || "en";
    return (TRANSLATIONS[lang] && TRANSLATIONS[lang][key]) || TRANSLATIONS["en"][key] || key;
  }

  constructor() {
    super();
    this._history = [];
    this._historyInterval = null;
    this._drawerOpen = false;
  }

  static getConfigElement() {
    return document.createElement("maico-vmc-card-editor");
  }

  static getStubConfig() {
    return {
      name: "VMC",
      show_efficiency: true,
      show_graph: true,
      graph_hours: 24,
    };
  }

  setConfig(config) {
    this.config = {
      name: config.name || "VMC",
      show_efficiency: config.show_efficiency !== false,
      show_graph: config.show_graph !== false,
      graph_hours: config.graph_hours || 24,
      graph_color: config.graph_color || "var(--accent-color, var(--primary-color))",
      show_humidity: config.show_humidity !== false,
      show_fan_mode: config.show_fan_mode !== false,
      climate_entity: config.climate_entity || null,
      ...config,
    };
  }

  connectedCallback() {
    super.connectedCallback();
    if (this.config?.show_graph) {
      this._fetchHistory();
      this._historyInterval = setInterval(() => this._fetchHistory(), 300000); // 5 min
    }
  }

  disconnectedCallback() {
    super.disconnectedCallback();
    if (this._historyInterval) {
      clearInterval(this._historyInterval);
    }
  }

  async _fetchHistory() {
    const entities = this._discoverEntities();
    if (!entities.humidity || !this.hass) return;

    const endTime = new Date().toISOString();
    const startTime = new Date(
      Date.now() - this.config.graph_hours * 60 * 60 * 1000
    ).toISOString();

    try {
      const url = `history/period/${startTime}?filter_entity_id=${entities.humidity}&end_time=${endTime}&minimal_response&no_attributes`;
      const response = await this.hass.callApi("GET", url);

      if (response && response[0]) {
        this._history = response[0]
          .filter((point) => !isNaN(parseFloat(point.state)))
          .map((point) => ({
            time: new Date(point.last_changed).getTime(),
            value: parseFloat(point.state),
          }));
        this.requestUpdate();
      }
    } catch (e) {
      console.warn("Failed to fetch history:", e);
    }
  }

  _generateGraphPath() {
    if (!this._history || this._history.length < 2) return "";

    const width = 400;
    const height = 80;
    const padding = 0;

    // Downsample to max 30 points for smoother curve
    let data = this._history;
    const maxPoints = 30;
    if (data.length > maxPoints) {
      const step = Math.ceil(data.length / maxPoints);
      data = data.filter((_, i) => i % step === 0 || i === data.length - 1);
    }

    const values = data.map((p) => p.value);
    const minVal = Math.min(...values) - 5;
    const maxVal = Math.max(...values) + 5;
    const range = maxVal - minVal || 1;

    // Calculate points
    const coords = data.map((point, i) => {
      const x = padding + (i / (data.length - 1)) * (width - 2 * padding);
      const y = height - padding - ((point.value - minVal) / range) * (height - 2 * padding);
      return { x, y };
    });

    // Create smooth cubic bezier curve path (Catmull-Rom spline)
    let path = `M ${coords[0].x},${coords[0].y}`;

    for (let i = 0; i < coords.length - 1; i++) {
      const p0 = coords[i === 0 ? i : i - 1];
      const p1 = coords[i];
      const p2 = coords[i + 1];
      const p3 = coords[i + 2 >= coords.length ? i + 1 : i + 2];

      // Catmull-Rom to Cubic Bezier conversion - lower tension = smoother
      const tension = 0.25;
      const cp1x = p1.x + (p2.x - p0.x) * tension;
      const cp1y = p1.y + (p2.y - p0.y) * tension;
      const cp2x = p2.x - (p3.x - p1.x) * tension;
      const cp2y = p2.y - (p3.y - p1.y) * tension;

      path += ` C ${cp1x},${cp1y} ${cp2x},${cp2y} ${p2.x},${p2.y}`;
    }

    // Add fill area
    const lastX = coords[coords.length - 1].x;
    const fillPath = `${path} L ${lastX},${height} L ${padding},${height} Z`;

    return { line: path, fill: fillPath };
  }

  // Auto-discover Maico entities
  _discoverEntities() {
    if (!this.hass) return {};

    const entities = {};
    const allEntities = Object.keys(this.hass.states);

    // Find climate entity
    entities.climate =
      this.config.climate_entity ||
      allEntities.find((e) => e.startsWith("climate.maico"));

    // Find temperature sensors
    // Find temperature sensors
    entities.temp_inlet = allEntities.find(
      (e) => e.includes("maico") && (e.includes("entrant") || e.includes("inlet") || e.includes("air_entrant") || e.includes("lufteintritt"))
    );
    entities.temp_exhaust = allEntities.find(
      (e) => e.includes("maico") && (e.includes("rejete") || e.includes("exhaust") || e.includes("air_rejete") || e.includes("fortluft"))
    );
    entities.temp_extract = allEntities.find(
      (e) => e.includes("maico") && (e.includes("extrait") || e.includes("extract") || e.includes("air_extrait") || e.includes("abluft"))
    );
    entities.temp_supply = allEntities.find(
      (e) => e.includes("maico") && e.startsWith("sensor.") &&
        (e.includes("souffle") || e.includes("supply_air_temp") || e.includes("zuluft")) &&
        !e.includes("fan") && !e.includes("ventilateur") && !e.includes("geschwindigkeit")
    );
    entities.temp_room = allEntities.find(
      (e) => e.includes("maico") && (e.includes("ambiant") || e.includes("room_temp") || e.includes("raumtemperatur"))
    );

    // Find humidity sensor
    entities.humidity = allEntities.find(
      (e) => e.includes("maico") && (e.includes("humidite") || e.includes("humidity") || e.includes("feuchtigkeit"))
    );

    // Find efficiency sensor
    entities.efficiency = allEntities.find(
      (e) => e.includes("maico") && (e.includes("rendement") || e.includes("efficiency") || e.includes("effizienz"))
    );

    // Find fan entity
    entities.fan = allEntities.find((e) => e.startsWith("fan.maico"));

    // Find bypass sensor (bypass_status)
    entities.bypass = allEntities.find(
      (e) => e.includes("maico") && (e.includes("bypass") || e.includes("etat_bypass"))
    );

    // Find filter sensors (3 types) - prefer remaining days
    entities.filter_device = allEntities.find(
      (e) => e.includes("maico") &&
        (e.includes("filter_device") || e.includes("filtre_appareil") || e.includes("geratefilter")) &&
        (e.includes("days") || e.includes("jours") || e.includes("restant") || e.includes("verbleibend"))
    );
    entities.filter_outdoor = allEntities.find(
      (e) => e.includes("maico") &&
        (e.includes("filter_outdoor") || e.includes("filtre_exterieur") || e.includes("filtre_ext") || e.includes("aussenfilter")) &&
        (e.includes("days") || e.includes("jours") || e.includes("restant") || e.includes("verbleibend"))
    );
    entities.filter_room = allEntities.find(
      (e) => e.includes("maico") &&
        (e.includes("filter_room") || e.includes("filtre_piece") || e.includes("filtre_interieur") || e.includes("raumfilter")) &&
        (e.includes("days") || e.includes("jours") || e.includes("restant") || e.includes("verbleibend"))
    );

    // Find power switch
    entities.power_switch = allEntities.find(
      (e) => e.startsWith("switch.maico") && (e.includes("power") || e.includes("alimentation") || e.includes("stromversorgung"))
    );

    // Find boost switch
    entities.boost_switch = allEntities.find(
      (e) => e.startsWith("switch.maico") && (e.includes("boost") || e.includes("surventilation"))
    );

    return entities;
  }

  _getState(entityId) {
    if (!entityId || !this.hass.states[entityId]) return "—";
    const state = this.hass.states[entityId].state;
    return state === "unavailable" || state === "unknown" ? "—" : state;
  }

  _getAttribute(entityId, attr) {
    if (!entityId || !this.hass.states[entityId]) return null;
    return this.hass.states[entityId].attributes[attr];
  }

  _getFanModeLabel(mode) {
    const modes = {
      off: this._localize("mode_off"),
      auto: this._localize("mode_auto"),
      low: this._localize("mode_low"),
      medium: this._localize("mode_medium"),
      high: this._localize("mode_high"),
    };
    return modes[mode] || mode || "—";
  }

  _calculateEfficiency(entities) {
    // If we have an efficiency sensor, use it
    if (entities.efficiency) {
      return this._getState(entities.efficiency);
    }

    // Otherwise calculate from temperatures
    const tempInlet = parseFloat(this._getState(entities.temp_inlet));
    const tempSupply = parseFloat(this._getState(entities.temp_supply));
    const tempExtract = parseFloat(this._getState(entities.temp_extract));

    if (isNaN(tempInlet) || isNaN(tempSupply) || isNaN(tempExtract)) {
      return "—";
    }

    // Efficiency = (Tsupply - Tinlet) / (Textract - Tinlet) * 100
    const efficiency =
      ((tempSupply - tempInlet) / (tempExtract - tempInlet)) * 100;
    return efficiency.toFixed(1);
  }

  _handleFanUp() {
    const entities = this._discoverEntities();
    if (!entities.climate) return;

    const fanModes = ["off", "low", "medium", "high"];
    const currentMode = this._getAttribute(entities.climate, "fan_mode") || "low";
    const currentIndex = fanModes.indexOf(currentMode);
    const newIndex = Math.min(currentIndex + 1, fanModes.length - 1);

    this.hass.callService("climate", "set_fan_mode", {
      entity_id: entities.climate,
      fan_mode: fanModes[newIndex],
    });
  }

  _handleFanDown() {
    const entities = this._discoverEntities();
    if (!entities.climate) return;

    const fanModes = ["off", "low", "medium", "high"];
    const currentMode = this._getAttribute(entities.climate, "fan_mode") || "low";
    const currentIndex = fanModes.indexOf(currentMode);
    const newIndex = Math.max(currentIndex - 1, 0);

    this.hass.callService("climate", "set_fan_mode", {
      entity_id: entities.climate,
      fan_mode: fanModes[newIndex],
    });
  }

  _handleMoreInfo() {
    const entities = this._discoverEntities();
    const event = new CustomEvent("hass-more-info", {
      bubbles: true,
      composed: true,
      detail: { entityId: entities.climate || entities.fan },
    });
    this.dispatchEvent(event);
  }

  _toggleDrawer() {
    this._drawerOpen = !this._drawerOpen;
  }

  _handlePower() {
    const entities = this._discoverEntities();
    if (entities.power_switch) {
      this.hass.callService("switch", "toggle", { entity_id: entities.power_switch });
    }
  }

  _handleVentilation() {
    const entities = this._discoverEntities();
    if (entities.fan) {
      this.hass.callService("fan", "toggle", { entity_id: entities.fan });
    }
  }

  _handleBoost() {
    const entities = this._discoverEntities();
    if (entities.boost_switch) {
      this.hass.callService("switch", "toggle", { entity_id: entities.boost_switch });
    }
  }

  render() {
    if (!this.hass) return html``;

    const entities = this._discoverEntities();
    const climate = entities.climate ? this.hass.states[entities.climate] : null;

    const efficiency = this._calculateEfficiency(entities);
    const roomTemp =
      climate?.attributes?.current_temperature ||
      this._getState(entities.temp_room);
    const humidity = this._getState(entities.humidity);
    const fanMode = climate?.attributes?.fan_mode || "—";
    const bypassState = this._getState(entities.bypass);

    // Get all 3 filter types
    const filterDevice = this._getState(entities.filter_device);
    const filterOutdoor = this._getState(entities.filter_outdoor);
    const filterRoom = this._getState(entities.filter_room);

    const graphPaths = this._generateGraphPath();

    return html`
      <ha-card>
        <!-- Background graph -->
        ${this.config.show_graph && graphPaths
        ? html`
              <div class="graph-background">
                <svg viewBox="0 0 400 80" preserveAspectRatio="none">
                  <defs>
                    <linearGradient id="graphGradient" x1="0%" y1="0%" x2="0%" y2="100%">
                      <stop offset="0%" style="stop-color:${this.config.graph_color};stop-opacity:0.3" />
                      <stop offset="100%" style="stop-color:${this.config.graph_color};stop-opacity:0.05" />
                    </linearGradient>
                  </defs>
                  <path d="${graphPaths.fill}" fill="url(#graphGradient)" />
                  <path d="${graphPaths.line}" fill="none" stroke="${this.config.graph_color}" stroke-width="2" stroke-opacity="0.5" />
                </svg>
              </div>
            `
        : ""}

        <div class="card-body">
          <div class="main-section">
            <div class="card-header" @click="${this._handleMoreInfo}">
              <div class="header-left">
                <span class="name">${this.config.name}</span>
              </div>
              <div class="header-center">
                ${this.config.show_efficiency
        ? html`
                      <span class="efficiency" title="${this._localize("efficiency")}">
                        <ha-icon icon="mdi:gauge"></ha-icon>
                        ${efficiency} %
                      </span>
                    `
        : ""}
              </div>
              <div class="header-right"></div>
            </div>

            <div class="card-content">
              <!-- Left temperatures -->
              <div class="temp-info left-top">
                <span class="temp-label">${this._localize("temp_outdoor")}</span>
                <span class="temp-value">${this._getState(entities.temp_inlet)}</span>
              </div>
              <div class="temp-info left-bottom">
                <span class="temp-label">${this._localize("temp_exhaust")}</span>
                <span class="temp-value">${this._getState(entities.temp_exhaust)}</span>
              </div>

              <!-- Heat exchanger SVG -->
              <div class="exchanger" .innerHTML="${EXCHANGER_SVG}"></div>

              <!-- Right temperatures -->
              <div class="temp-info right-top">
                <span class="temp-label">${this._localize("temp_extract")}</span>
                <span class="temp-value">${this._getState(entities.temp_extract)}</span>
              </div>
              <div class="temp-info right-bottom">
                <span class="temp-label">${this._localize("temp_supply")}</span>
                <span class="temp-value">${this._getState(entities.temp_supply)}</span>
              </div>
            </div>
          </div>

          <!-- Side info column -->
          <div class="side-section">
            <div class="side-info">
              <div class="info-item">
                <ha-icon icon="mdi:thermometer"></ha-icon>
                <span>${roomTemp}</span>
              </div>
              ${this.config.show_humidity
        ? html`
                    <div class="info-item humidity">
                      <ha-icon icon="mdi:water-percent"></ha-icon>
                      <span>${humidity}</span>
                    </div>
                  `
        : ""}
              ${this.config.show_fan_mode
        ? html`
                    <div class="info-item fan">
                      <ha-icon
                        icon="mdi:fan"
                        class="${fanMode !== "off" ? "spinning" : ""}"
                      ></ha-icon>
                      <span>${this._getFanModeLabel(fanMode)}</span>
                    </div>
                  `
        : ""}
            </div>
          </div>

          <!-- Control buttons column with drawer -->
          <div class="controls-section">
            <div class="controls-wrapper ${this._drawerOpen ? 'drawer-open' : ''}">
              <!-- Drawer panel -->
              <div class="drawer">
                <button class="drawer-btn ${this._getState(entities.power_switch) === 'on' ? 'active' : ''}" 
                        @click="${this._handlePower}" 
                        title="${this._localize('power')}">
                  <ha-icon icon="mdi:power"></ha-icon>
                </button>
                <button class="drawer-btn ${this._getState(entities.fan) === 'on' ? 'active' : ''}" 
                        @click="${this._handleVentilation}"
                        title="${this._localize('ventilation')}">
                  <ha-icon icon="mdi:fan"></ha-icon>
                </button>
                <button class="drawer-btn ${this._getState(entities.boost_switch) === 'on' ? 'active boost' : ''}" 
                        @click="${this._handleBoost}"
                        title="${this._localize('boost')}">
                  <ha-icon icon="mdi:fan-speed-3"></ha-icon>
                </button>
              </div>
              <!-- Main controls -->
              <div class="controls">
                <button class="control-btn" @click="${this._handleFanUp}">
                  <ha-icon icon="mdi:chevron-up"></ha-icon>
                </button>
                <button class="control-btn" @click="${this._toggleDrawer}">
                  <ha-icon icon="mdi:menu"></ha-icon>
                </button>
                <button class="control-btn" @click="${this._handleFanDown}">
                  <ha-icon icon="mdi:chevron-down"></ha-icon>
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Footer row with bypass and filters -->
        <div class="card-footer">
          ${bypassState !== "—"
        ? html`
                <div class="footer-item bypass ${bypassState === "on" ? "open" : "closed"}">
                  <ha-icon icon="mdi:valve"></ha-icon>
                  <span>${bypassState === "on" ? this._localize("open") : this._localize("closed")}</span>
                </div>
              `
        : ""}
          ${filterDevice !== "—"
        ? html`
                <div class="footer-item filter ${parseInt(filterDevice) < 30 ? "warning" : ""}">
                  <ha-icon icon="mdi:air-filter"></ha-icon>
                  <span title="${this._localize("filter_device")}">${filterDevice}j</span>
                </div>
              `
        : ""}
          ${filterOutdoor !== "—"
        ? html`
                <div class="footer-item filter ${parseInt(filterOutdoor) < 30 ? "warning" : ""}">
                  <ha-icon icon="mdi:weather-windy"></ha-icon>
                  <span title="${this._localize("filter_outdoor")}">${filterOutdoor}j</span>
                </div>
              `
        : ""}
          ${filterRoom !== "—"
        ? html`
                <div class="footer-item filter ${parseInt(filterRoom) < 30 ? "warning" : ""}">
                  <ha-icon icon="mdi:home-outline"></ha-icon>
                  <span title="${this._localize("filter_room")}">${filterRoom}j</span>
                </div>
              `
        : ""}
        </div>
      </ha-card>
    `;
  }

  static get styles() {
    return css`
      :host {
        --vmc-primary: var(--primary-color);
        --vmc-info: var(--info-color, #039be5);
        display: block;
        height: 100%;
        container-type: size;
      }

      ha-card {
        padding: 8px;
        overflow: hidden;
        position: relative;
        box-sizing: border-box;
        height: 100%;
        display: flex;
        flex-direction: column;
      }

      .graph-background {
        position: absolute;
        left: 0;
        right: 0;
        bottom: 0;
        height: 40%; /* Responsive height */
        min-height: 80px;
        pointer-events: none;
        z-index: 0;
      }

      .graph-background svg {
        width: 100%;
        height: 100%;
      }

      .card-body {
        display: flex;
        flex: 1;
        position: relative;
        z-index: 1;
        height: 100%;
        min-height: 0;
        padding-bottom: 2px;
      }

      .main-section {
        flex: 1;
        display: flex;
        flex-direction: column;
        padding: 12px 6px 12px 12px;
        min-width: 0;
      }

      .controls-section {
        width: 60px; /* Reserve space for closed controls */
        padding: 12px 6px 12px 0;
        display: flex;
        flex-direction: column;
        flex-shrink: 0;
        position: relative;
        z-index: 20;
        margin-right: 6px;
      }

      .side-section {
        width: auto;
        padding: 12px 6px 12px 0;
        display: flex;
        flex-direction: column;
        flex-shrink: 0;
      }

      .card-header {
        display: flex;
        align-items: center;
        margin-bottom: 8px;
        cursor: pointer;
        min-height: 24px;
        gap: 8px;
      }
      
      .header-left { 
        flex: 0 1 auto;
        min-width: 0;
      }
      .header-center { 
        flex: 1;
        display: flex;
        justify-content: center;
        min-width: 0;
      }
      .header-right { 
        flex: 0 0 auto;
      }

      .name {
        font-size: 18px;
        font-weight: bold;
        white-space: nowrap;
        color: var(--primary-text-color);
      }

      .efficiency {
        display: flex;
        align-items: center;
        gap: 4px;
        font-size: 14px;
        color: var(--secondary-text-color);
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        max-width: 100%;
      }

      .efficiency ha-icon {
        --mdc-icon-size: 20px;
        color: var(--vmc-primary);
      }

      .card-content {
        display: grid;
        grid-template-columns: minmax(50px, 1fr) minmax(50px, 100px) minmax(50px, 1fr);
        grid-template-rows: 1fr 1fr;
        gap: 2px 4px;
        align-items: center;
        width: 100%;
        box-sizing: border-box;
        flex: 1;
        min-height: 0;
      }

      .temp-info {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 4px;
      }

      .temp-label {
        font-size: 14px;
        color: var(--secondary-text-color);
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        max-width: 100%;
        text-align: center;
      }

      .temp-value {
        font-size: 14px;
        font-weight: 500;
        color: var(--primary-text-color);
      }

      .left-top { grid-area: 1 / 1; }
      .left-bottom { grid-area: 2 / 1; }
      .right-top { grid-area: 1 / 3; }
      .right-bottom { grid-area: 2 / 3; }

      .exchanger {
        grid-area: 1 / 2 / 3 / 3;
        width: 100%;
        max-width: 80px;
        aspect-ratio: 1;
        justify-self: center;
        overflow: hidden;
        z-index: 1;
      }

      .exchanger svg {
        width: 100%;
        height: 100%;
      }

      .side-info {
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        height: 100%;
        align-self: stretch;
        padding: 4px 6px;
        position: relative;
        z-index: 5;
      }

      .info-item {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 2px;
        font-size: 14px;
        text-align: center;
        color: var(--primary-text-color);
      }

      .info-item ha-icon {
        --mdc-icon-size: 24px;
        color: var(--secondary-text-color);
      }

      .info-item.humidity ha-icon { color: var(--info-color, #039be5); }
      .info-item.fan ha-icon { color: var(--primary-text-color); }

      .spinning {
        animation: spin 2s linear infinite;
      }

      @keyframes spin {
        100% { transform: rotate(360deg); }
      }

      /* Controls wrapper - unified container for drawer + controls */
      .controls-wrapper {
        /* Glass effect using color-mix for compatibility */
        background: color-mix(in srgb, var(--card-background-color, #202020) 80%, transparent);
        border: 1px solid var(--divider-color, rgba(255, 255, 255, 0.1));
        border-radius: 24px;
        display: flex;
        flex-direction: row;
        /* Height matches container naturally or set 100% of parent relative height */
        position: absolute;
        top: 12px;
        bottom: 12px;
        right: 6px;
        width: auto;
        z-index: 20;
        box-shadow: 0 4px 8px rgba(0,0,0,0.3);
        overflow: hidden;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
      }

      /* Drawer panel - hidden by default */
      .drawer {
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        gap: 8px;
        width: 0;
        overflow: hidden;
        transition: all 0.3s ease;
        opacity: 0;
      }

      .controls-wrapper.drawer-open .drawer {
        width: 48px;
        padding: 8px 6px;
        opacity: 1;
      }

      .drawer-btn {
        background: none;
        border: none;
        padding: 10px;
        cursor: pointer;
        border-radius: 50%;
        color: var(--secondary-text-color);
        transition: all 0.2s;
        display: flex;
        align-items: center;
        justify-content: center;
      }

      .drawer-btn:hover {
        background: rgba(var(--rgb-primary-text-color), 0.1);
      }

      .drawer-btn ha-icon {
        --mdc-icon-size: 24px;
      }

      .drawer-btn.active {
        color: var(--success-color, #4caf50);
      }

      .drawer-btn.active.boost {
        color: var(--warning-color, #ff9800);
      }

      .controls {
        display: flex;
        flex-direction: column;
        justify-content: space-around;
        align-items: center;
        gap: 4px;
        padding: 8px 6px;
        box-sizing: border-box;
        height: 100%;
      }

      .control-btn {
        background: none;
        border: none;
        padding: 8px;
        cursor: pointer;
        border-radius: 50%;
        color: var(--primary-text-color);
        transition: background 0.2s;
        display: flex;
        align-items: center;
        justify-content: center;
      }

      .control-btn:hover {
        background: rgba(var(--rgb-primary-text-color), 0.1);
      }

      .control-btn ha-icon {
        --mdc-icon-size: 24px;
      }

      /* Footer with bypass and filters */
      .card-footer {
        display: flex;
        flex-wrap: wrap;
        justify-content: space-around;
        gap: 6px 12px;
        padding: 6px 0 0 0;
        margin-top: 2px;
        position: relative;
        z-index: 1;
        flex-shrink: 0;
        width: 100%;
      }

      .footer-item {
        display: flex;
        align-items: center;
        gap: 4px;
        font-size: 13px;
        color: var(--primary-text-color);
      }

      .footer-item ha-icon {
        --mdc-icon-size: 18px;
      }

      .footer-item.bypass ha-icon { color: var(--vmc-info); }
      .footer-item.bypass.open ha-icon { color: var(--warning-color, #ff9800); }
      .footer-item.bypass.closed ha-icon { color: var(--success-color, #4caf50); }
      .footer-item.filter ha-icon { color: var(--success-color, #4caf50); }
      .footer-item.filter.warning ha-icon { color: var(--error-color, #f44336); }

      /* Compact mode - when card is small */
      @media (max-width: 400px) {
        .card-content {
          grid-template-columns: 1fr minmax(40px, 50px) 1fr auto;
        }
        
        .side-info {
          padding: 0 4px 0 8px;
        }
        
        .exchanger { max-width: 50px; }
        .temp-label { font-size: 12px; }
        .temp-value { font-size: 12px; }
        
        .name { font-size: 14px; }
        .efficiency { font-size: 12px; }
        .info-item { font-size: 12px; }
      }

      /* Very compact vertical mode */
      @container (max-height: 200px) {
        .main-section { padding: 4px 6px 4px 8px !important; }
        .controls-section { padding: 4px 8px 4px 6px !important; }
        .card-header { margin-bottom: 2px !important; }
        .card-footer { display: none; }
      }

      @media (max-width: 300px) {
        .side-info { display: none; }
        .card-content {
          grid-template-columns: 1fr minmax(40px, 50px) 1fr;
        }
      }
    `;
  }

  getCardSize() {
    return 4;
  }

  // For sections view (grid layout) - each row is ~56px
  static getGridOptions() {
    return {
      columns: 12,        // Full width (12 columns = full section)
      min_columns: 6,     // Minimum half width
      rows: 3,            // Default 3 rows (~168px)
      min_rows: 2,        // Minimum 2 rows
      max_rows: 4,        // Maximum 4 rows
    };
  }
}

// Card Editor
class MaicoVMCCardEditor extends LitElement {
  static get properties() {
    return {
      hass: { type: Object },
      config: { type: Object },
    };
  }

  setConfig(config) {
    this.config = config;
  }

  render() {
    if (!this.hass || !this.config) return html``;

    return html`
      <div class="editor">
        <ha-textfield
          label="Nom de la carte"
          .value="${this.config.name || "VMC"}"
          @input="${this._nameChanged}"
        ></ha-textfield>

        <ha-formfield label="Afficher le rendement">
          <ha-switch
            .checked="${this.config.show_efficiency !== false}"
            @change="${this._efficiencyChanged}"
          ></ha-switch>
        </ha-formfield>

        <ha-formfield label="Afficher le graphique d'humidité">
          <ha-switch
            .checked="${this.config.show_graph !== false}"
            @change="${this._graphChanged}"
          ></ha-switch>
        </ha-formfield>

        <ha-formfield label="Afficher l'humidité">
          <ha-switch
            .checked="${this.config.show_humidity !== false}"
            @change="${this._humidityChanged}"
          ></ha-switch>
        </ha-formfield>

        <ha-formfield label="Afficher le mode ventilateur">
          <ha-switch
            .checked="${this.config.show_fan_mode !== false}"
            @change="${this._fanModeChanged}"
          ></ha-switch>
        </ha-formfield>
      </div>
    `;
  }

  _nameChanged(e) {
    this._updateConfig("name", e.target.value);
  }

  _efficiencyChanged(e) {
    this._updateConfig("show_efficiency", e.target.checked);
  }

  _graphChanged(e) {
    this._updateConfig("show_graph", e.target.checked);
  }

  _humidityChanged(e) {
    this._updateConfig("show_humidity", e.target.checked);
  }

  _fanModeChanged(e) {
    this._updateConfig("show_fan_mode", e.target.checked);
  }

  _updateConfig(key, value) {
    const newConfig = { ...this.config, [key]: value };
    const event = new CustomEvent("config-changed", {
      detail: { config: newConfig },
      bubbles: true,
      composed: true,
    });
    this.dispatchEvent(event);
  }

  static get styles() {
    return css`
      .editor {
        display: flex;
        flex-direction: column;
        gap: 16px;
        padding: 16px;
      }

      ha-textfield {
        width: 100%;
      }
    `;
  }
}

// Register elements
customElements.define("maico-vmc-card", MaicoVMCCard);
customElements.define("maico-vmc-card-editor", MaicoVMCCardEditor);

// Register card
window.customCards = window.customCards || [];
window.customCards.push({
  type: "maico-vmc-card",
  name: "Maico VMC Card",
  description: "Carte personnalisée pour VMC Maico WS avec auto-découverte",
  preview: true,
  documentationURL: "https://github.com/isaya07/ha-maicows-card",
});

console.info(
  "%c MAICO-VMC-CARD %c 1.2.0",
  "color: white; background: #039be5; font-weight: bold;",
  "color: #039be5; background: white; font-weight: bold;"
);
