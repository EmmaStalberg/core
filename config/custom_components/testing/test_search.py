"""Tests Search functionality."""

import unittest
from unittest.mock import patch

from custom_components.open_street_map.search import (
    get_address_coordinates,
    get_Coordinates,
    search_address,
)

import requests


class TestSearchFunctions(unittest.TestCase):
    """Class for tests regarding the search function."""

    @patch("custom_component.open_street_map.search.requests.get")
    def test_search_address_success(self, mock_get):
        """Tests the success of the search function."""
        # Mock a successful API response with address and coordinates
        mock_response = {
            "status_code": 200,
            "json": lambda: [
                {
                    "display_name": "Sample Address",
                    "lat": "57.69168362481461",
                    "lon": "11.95719433068511",
                }
            ],
        }
        mock_get.return_value = type("MockResponse", (object,), mock_response)
        # Call the function and check the result
        result = search_address("Sample Address")
        self.assertIsInstance(result, list)
        self.assertIn("display_name", result[0])

    @patch("custom_component.open_street_map.search.requests.get")
    def test_search_address_timeout(self, mock_get):
        """Tests the time out of search function."""
        # Stimulate a timeout error
        mock_get.side_effect = requests.exceptions.Timeout
        result = search_address("Sample Address")
        self.assertEqual(result, {"error": "Request timed out"})

    @patch("custom_component.open_street_map.search.requests.get")
    def test_search_address_failure(self, mock_get):
        """Tests the failure of search function."""
        # Simulate a request failure
        mock_get.side_effect = requests.exceptions.RequestException("Mock failure")
        result = search_address("Sample Address")
        self.assertEqual(result, {"error": "Request failed: Mock failure"})

    def test_get_Coordinates_success(self):
        """Tests the success of get_coordinates function."""
        # Simulate valid JSON data with lat and lon
        sample_json = [
            {
                "lat": "57.69168362481461",
                "lon": "11.95719433068511",
            }
        ]
        result = get_Coordinates(sample_json)
        # Make sure that the extraction of coordinates are correct
        self.assertEqual(result, [57.69168362481461, 11.95719433068511])

    def test_get_Coordinates_failure(self):
        # Simulate empty JSON data
        """Tests the failure of get_coordinates function."""
        sample_json = []
        result = get_Coordinates(sample_json)
        # Check the error message when no coordinates are found
        self.assertEqual(result, {"error": "Coordinates could not be extracted"})

        # Simulate invalid coordinate data
        sample_json = [
            {
                "lat": "invalid",
                "lon": "data",
            }
        ]
        result = get_Coordinates(sample_json)
        # Check the error for invalid data
        self.assertEqual(result, {"error": "Coordinates could not be extracted"})

    @patch("custom_component.open_street_map.search.search_address")
    def test_get_address_coordinates_success(self, mock_search):
        """Test the success of get_address_coordinates function."""
        # Mock a successful search with coordinates
        mock_search.return_value = [
            {
                "lat": "57.69168362481461",
                "lon": "11.95719433068511",
            }
        ]
        result = get_address_coordinates("Sample Address")
        # Make sure the correct coordinates are returned
        self.assertEqual(result, [57.69168362481461, 11.95719433068511])

    @patch("custom_component.open_street_map.search.search_address")
    def test_get_address_coordinates_fail(self, mock_search):
        """Test the failure of get address coordinates function."""
        # Mock a failed search response
        mock_search.return_value = {"error": "Request failed"}
        result = get_address_coordinates("Sample Address")
        # Make sure the error message is returned
        self.assertEqual(result, {"error": "Request failed"})


if __name__ == "__main__":
    unittest.main()
