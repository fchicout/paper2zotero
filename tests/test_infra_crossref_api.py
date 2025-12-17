import unittest
from unittest.mock import patch, Mock
import requests
from paper2zotero.infra.crossref_api import CrossRefAPIClient

class TestCrossRefAPIClient(unittest.TestCase):
    def setUp(self):
        self.client = CrossRefAPIClient()

    @patch('requests.get')
    def test_get_references_by_doi_success(self, mock_get):
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "message": {
                "reference": [
                    {"DOI": "10.1000/cited.paper.1"},
                    {"unrelated_field": "some_value"},
                    {"DOI": "10.1000/cited.paper.2"},
                    {"DOI": ""} # Empty DOI should not be included
                ]
            }
        }
        mock_get.return_value = mock_response

        doi = "10.1000/main.paper"
        references = self.client.get_references_by_doi(doi)

        self.assertIsInstance(references, list)
        self.assertEqual(len(references), 2)
        self.assertIn("10.1000/cited.paper.1", references)
        self.assertIn("10.1000/cited.paper.2", references)
        mock_get.assert_called_once_with(
            f"https://api.crossref.org/works/{doi}",
            headers={'User-Agent': 'paper2zotero/1.0 (mailto:fchicout@gmail.com)'}
        )

    @patch('requests.get')
    def test_get_references_by_doi_no_references(self, mock_get):
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "message": {
                "reference": [
                    {"unrelated_field": "some_value"}
                ]
            }
        }
        mock_get.return_value = mock_response

        doi = "10.1000/main.paper.no.refs"
        references = self.client.get_references_by_doi(doi)

        self.assertIsInstance(references, list)
        self.assertEqual(len(references), 0)

    @patch('requests.get')
    @patch('builtins.print') # Patch print to capture output
    def test_get_references_by_doi_api_error(self, mock_print, mock_get):
        mock_get.side_effect = requests.exceptions.RequestException("Network error")

        doi = "10.1000/error.paper"
        references = self.client.get_references_by_doi(doi)

        self.assertIsInstance(references, list)
        self.assertEqual(len(references), 0)
        
        # Assert that print was called with an error message
        mock_print.assert_called_once()
        self.assertIn("Error fetching references for DOI", mock_print.call_args[0][0])
        self.assertIn("Network error", mock_print.call_args[0][0])

    @patch('requests.get')
    def test_get_references_by_doi_no_message_key(self, mock_get):
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {"other_key": "other_value"} # Missing "message" key
        mock_get.return_value = mock_response # Set return_value for this specific test
        
        references = self.client.get_references_by_doi("10.123/missing.message")
        self.assertEqual(references, [])


    def test_get_references_by_doi_no_reference_key(self):
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {"message": {"other_sub_key": "other_value"}} # Missing "reference" key
        
        with patch('requests.get', return_value=mock_response):
            references = self.client.get_references_by_doi("10.123/missing.reference")
            self.assertEqual(references, [])


if __name__ == '__main__':
    unittest.main()
