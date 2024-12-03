"""Tests Search functionality."""

import unittest
from unittest.mock import patch

import requests

from ..open_street_map.search import (
    get_address_coordinates,
    get_Coordinates,
    search_address,
)


class TestSearchFunctions(unittest.TestCase):
    """Class for tests regarding the search function."""

    @patch("custom_component.open_street_map.search.requests.get")
    def test_search_address_success(self, mock_get):
        """Tests the success of the search function."""
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
        result = search_address("Sample Address")
        self.assertIsInstance(result, list)
        self.assertIn("display_name", result[0])


if __name__ == "__main__":
    unittest.main()
