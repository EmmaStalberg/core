# OpenStreetMap Integration for Home Assistant

Enhance your Home Assistant experience with the OpenStreetMap (OSM) integration. This component provides basic map features, allowing users to view maps, search for locations, and change map layers, leveraging OpenStreetMap's open-source data.

## Features

- View and interact with maps directly in Home Assistant.
- Search for locations using addresses or coordinates with autocomplete suggestions.
- Customize map layers (e.g., satellite view, 3D maps).

## Installation

1. **Download the Integration**  
   Clone the repository and navigate to the `custom_components` directory:
   ```bash
   git clone https://github.com/EmmaStalberg/core.git
   ```

2. **Update Configuration**  
   Add the following configuration to your `configuration.yaml` file:
   ```yaml
   openstreetmap:
     default_map_layer: "standard"
   ```

   **Note:** The default map layer can be set to "standard" or any other supported type.

3. **Restart Home Assistant**  
   Restart your Home Assistant instance to load the new component.

4. **Verify Installation**  
   Check if the OpenStreetMap integration appears in the sidebar.

## Data Model

The OpenStreetMap integration for Home Assistant uses several key data components that are essential to its functionality:

- **Map Layers**: Users can select different map layers (e.g., standard, satellite, 3D) through configuration options, with these settings stored in the Home Assistant configuration (`configuration.yaml`).
- **Location Data**: Geocoding and reverse geocoding are handled by interacting with OpenStreetMap's Nominatim API. The retrieved coordinates are temporarily processed for visualization and automation purposes, without persistent storage.
- **Search Results**: Search data, such as addresses and points of interest, is fetched in real-time using the Nominatim API. This data is not stored locally; instead, it is used to provide immediate map interactions and event triggers.

## System Architecture

This integration relies on several RESTful APIs provided by OpenStreetMap:

- **Nominatim API**: Supports geocoding (searching by name or address) and reverse geocoding. This API is used for fetching location data, which is processed and used within Home Assistant.

The integration registers multiple services, including:
- **Search Service**: The `search` service is registered to find addresses or coordinates using the OpenStreetMap Nominatim API. It supports handling search queries and returning results, which are then fired as events within Home Assistant.
- **Get Coordinates Service**: The `get_coordinates` service extracts coordinates from a JSON payload, specifically designed to parse data from the OpenStreetMap APIs.
- **Get Address Coordinates Service**: The `get_address_coordinates` service combines the search functionality to return coordinates directly from an address query.

These services provide flexibility in how users can interact with the OpenStreetMap integration, enabling advanced geolocation features for various automation scenarios.

## Additional Resources

- [Home Assistant Documentation](https://www.home-assistant.io/)
- [Home Assistant Developer Documentation](https://developers.home-assistant.io/)
- [OpenStreetMap API Documentation](https://wiki.openstreetmap.org/wiki/API)

## License

This project is licensed under the [MIT License](LICENSE).  
OpenStreetMap data is available under the [Open Database License](https://opendatacommons.org/licenses/odbl/).
