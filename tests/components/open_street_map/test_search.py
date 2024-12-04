"""Tests Search functionality."""

import unittest
from unittest.mock import patch

import requests

from homeassistant.components.open_street_map import (
    get_address_coordinates,
    get_Coordinates,
    search_address,
)


class TestSearchFunctions(unittest.TestCase):
    """Class for tests regarding the search function."""

    @patch("homeassistant.components.open_street_map.search.requests.get")
    def test_search_address_success(self, mock_get):
        """Tests the success of the search function."""
        # Mock a successful API response with address and coordinates
        mock_response = {
            "status_code": 200,
            "json": lambda: [
                {
                    "display_name": "Test Address",
                    "lat": "57.69168362481461",
                    "lon": "11.95719433068511",
                }
            ],
        }
        # The @patch decorator replaces requests.get with mock_get, a mock object.
        # When search_address("Test Address") is called, requests.get() is replaced by mock_get.
        # mock_get returns the MockResponse object that is defined earlier, simulating an API response.
        # MockResponse includes a json() method (via lambda) that provides mocked JSON data.
        # The search_address function processes this mock data as if it came from the real API.

        mock_get.return_value = type("MockResponse", (object,), mock_response)
        # Call the function and check the result
        result = search_address("Test Address")
        # Use plain assert statements
        assert isinstance(result, list)
        assert "display_name" in result[0]

    @patch("homeassistant.components.open_street_map.search.requests.get")
    def test_search_address_timeout(self, mock_get):
        """Tests the time out of search function."""
        # Stimulate a timeout error
        mock_get.side_effect = requests.exceptions.Timeout
        result = search_address("Test Address")
        assert result == {"error": "Request timed out"}

    @patch("homeassistant.components.open_street_map.search.requests.get")
    def test_search_address_failure(self, mock_get):
        """Tests the failure of search function."""
        # Simulate a request failure
        mock_get.side_effect = requests.exceptions.RequestException("Mock failure")
        result = search_address("Test Address")
        assert result == {"error": "Request failed: Mock failure"}

    def test_get_Coordinates_success(self):
        """Tests the success of get_coordinates function."""
        # Simulate valid JSON data with lat and lon
        # No @patch is needed since we don't mock any API
        # Instead we write down the lat and lon we want to check
        sample_json = [
            {
                "lat": "57.69168362481461",
                "lon": "11.95719433068511",
            }
        ]
        result = get_Coordinates(sample_json)
        # Make sure that the extraction of coordinates are correct
        assert result == [57.69168362481461, 11.95719433068511]

    def test_get_Coordinates_failure(self):
        # Simulate empty JSON data
        """Tests the failure of get_coordinates function."""
        sample_json = []
        result = get_Coordinates(sample_json)
        # Check the error message when no coordinates are found
        assert result == {"error": "Coordinates could not be extracted"}

        # Simulate invalid coordinate data
        sample_json = [
            {
                "lat": "invalid",
                "lon": "data",
            }
        ]
        result = get_Coordinates(sample_json)
        # Check the error for invalid data
        assert result == {"error": "Coordinates could not be extracted"}

    @patch("homeassistant.components.open_street_map.search.search_address")
    def test_get_address_coordinates_success(self, mock_search):
        """Test the success of get_address_coordinates function."""
        # Mock a successful search with coordinates
        mock_search.return_value = [
            {
                "lat": "57.69168362481461",
                "lon": "11.95719433068511",
            }
        ]
        result = get_address_coordinates("Test Address")
        # Make sure the correct coordinates are returned
        assert result == [57.69168362481461, 11.95719433068511]

    @patch("homeassistant.components.open_street_map.search.search_address")
    def test_get_address_coordinates_fail(self, mock_search):
        """Test the failure of get address coordinates function."""
        # Mock a failed search response
        mock_search.return_value = {"error": "Request failed"}
        result = get_address_coordinates("Test Address")
        # Make sure the error message is returned
        assert result == {"error": "Request failed"}


if __name__ == "__main__":
    unittest.main()
