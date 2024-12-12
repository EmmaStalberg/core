import "https://unpkg.com/wired-card@2.1.0/lib/wired-card.js?module";
import {
  LitElement,
  html,
  css,
} from "https://unpkg.com/lit-element@2.4.0/lit-element.js?module";

class OpenStreetMapPanel extends HTMLElement {
    set hass(hass) {
        // Create the card container
        if (!this.content) {
            this.content = document.createElement("open-street-map-panel");
            this.appendChild(this.content);
            this.offsetHeight;
        }

        // Pass configuration to the OSM card
        const config = {
            type: "custom:osm",
            auto_fit: true,
            entities: ["zone.home"],
        };
        this.content.setConfig(config);
        this.content.hass = hass;
    }
}

customElements.define("openstreetmap-panel", OpenStreetMapPanel);



// class OpenStreetMapPanel extends LitElement {
//     static get properties() {
//         return {
//             hass: { type: Object },
//             narrow: { type: Boolean },
//             route: { type: Object },
//             panel: { type: Object },
//             configEntryId: { type: String },
//             // recipes, favorites etc
//             searchTerm: { type: String },
//         };
//     }

//     constructor() {
//         super();
//         this.configEntryId = '';
//         this.searchTerm = '';
//         // maybe add more of our variables
//     }

//     connectedCallback() {
//         super.connectedCallback();
//         this.setup();
//     }

//     async setup() {
//         await this._getConfigEntries(); // if we dont change and start to use entries, this is not needed!
//         // i don't think these needs to be run here
//         // await this._doSearch();
//         // await this._getAddressCoordinates();
//         // await this._getCoordinates();
//     }

//     // not sure about this method...
//     async _getConfigEntries() {
//         try {
//           const entries = await this.hass.callWS({ type: 'config_entries/get' });
//           console.log('Config Entries:', entries);
//           const entry = entries.find(entry => entry.domain === 'open_street_map');
//           console.log('our entry: ', entry)
//           if (entry) {
//             this.configEntryId = entry.entry_id;
//           }
//         } catch (error) {
//           console.error('Error fetching config entries:', error);
//         }
//     }

//     async _doSearch() {
//         //todo
//     }

//     async _getAddressCoordinates() {
//         try {
//             const coordinates = await this.hass.callService(
//                 "open_street_map",
//                 "get_address_coordinates",
//                 {
//                     config_entry_id: this.configEntryId,
//                     query: this.searchTerm,
//                 },
//                 undefined, undefined, true
//             );
//             // update map - center around it and add marker
//             // const lat = 57.6915335;
//             // const lon = 11.9571416;
//             const lat = coordinates[0];
//             const lon = coordinates[1];
//             console.log("Received coordinates, lat: ", lat)
//             console.log("Received coordinates, lon: ", lon)
//             // method below is still in frontend
//             // this._map?.fitMapToCoordinates([lat, lon], {zoom: 13});
//         } catch(error) {
//             console.log("Could not find coordinates", error)
//             //want to reset the searchterm if error occur?
//             this.searchTerm = '';
//          }
//     }

//     async _getCoordinates() {
//         // todo
//     }

//     // not sure which methods needs this in the beginning?
//     // if (!this.configEntryId) {
//     //     console.error('Config Entry ID not found');
//     //     return;
//     // }

//     // lägg till funktionerna...

//     // skapa on searchInputChange och även enterClicked-koppla till getAdC
//     async onSearchInputChange(event) {
//         console.log("updated search term to ", event.target.value);
//         this.searchTerm = event.target.value;

//         //here one could implement to get suggestions based on autocomplete, and call that service
//     }

//     render() {
//         return html`
//             <div style="max-width: 800px; margin: 0 auto;">
//                 <div style="display: flex;">
//                     <button @click="${this._getAddressCoordinates}">Get coordinates, ie search</button>
//                     <input type="text" placeholder="Search for address..." value="${this.searchTerm}" @input=${this.onSearchInputChange} />
//                 </div>
//             </div>
//         `;
//     }
// }
// customElements.define("openstreetmap-panel", OpenStreetMapPanel);
