import unittest
from unittest.mock import patch, Mock
import requests
from paper2zotero.infra.zotero_api import ZoteroAPIClient

class TestZoteroAPIClientMove(unittest.TestCase):
    def setUp(self):
        self.api_key = "test_key"
        self.group_id = "12345"
        self.client = ZoteroAPIClient(self.api_key, self.group_id)

    @patch('requests.patch')
    def test_update_item_collections_success(self, mock_patch):
        # Setup mock response
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None  # No exception
        mock_patch.return_value = mock_response

        # Inputs
        item_key = "ABC12345"
        version = 42
        new_collections = ["COL1", "COL2"]

        # Action
        result = self.client.update_item_collections(item_key, version, new_collections)

        # Assertion
        self.assertTrue(result)
        
        expected_url = f"https://api.zotero.org/groups/{self.group_id}/items/{item_key}"
        expected_headers = {
            'Zotero-API-Version': '3',
            'Zotero-API-Key': self.api_key,
            'If-Match': '42'
        }
        expected_payload = {'collections': new_collections}

        mock_patch.assert_called_once_with(
            expected_url, 
            headers=expected_headers, 
            json=expected_payload
        )

    @patch('requests.patch')
    def test_update_item_collections_failure(self, mock_patch):
        # Setup mock exception
        mock_patch.side_effect = requests.exceptions.RequestException("API Error")

        # Action
        result = self.client.update_item_collections("ABC", 1, [])

        # Assertion
        self.assertFalse(result)

if __name__ == '__main__':
    unittest.main()
