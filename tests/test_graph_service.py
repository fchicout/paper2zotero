import unittest
from unittest.mock import Mock, MagicMock
from paper2zotero.core.interfaces import ZoteroGateway, CitationGateway
from paper2zotero.core.zotero_item import ZoteroItem
from paper2zotero.core.services.graph_service import CitationGraphService

class TestCitationGraphService(unittest.TestCase):
    def setUp(self):
        self.mock_zotero_gateway = Mock(spec=ZoteroGateway)
        self.mock_citation_gateway = Mock(spec=CitationGateway)
        self.service = CitationGraphService(self.mock_zotero_gateway, self.mock_citation_gateway)

        self.mock_zotero_gateway.get_collection_id_by_name.return_value = "COL_ID"
    
    def _create_zotero_item(self, key, title=None, doi=None):
        raw_item = {
            'key': key,
            'data': {
                'version': 1,
                'itemType': 'journalArticle',
                'title': title,
                'DOI': doi,
            }
        }
        return ZoteroItem.from_raw_zotero_item(raw_item)

    def test_build_graph_simple_case(self):
        # Setup mock Zotero items
        item_a = self._create_zotero_item("KEY_A", "Paper A", "10.1/A")
        item_b = self._create_zotero_item("KEY_B", "Paper B", "10.1/B")
        item_c = self._create_zotero_item("KEY_C", "Paper C", "10.1/C")
        
        self.mock_zotero_gateway.get_items_in_collection.return_value = iter([item_a, item_b, item_c])

        # Setup mock citation references: A cites B, B cites C
        self.mock_citation_gateway.get_references_by_doi.side_effect = \
            lambda doi: {
                "10.1/A": ["10.1/B", "10.999/external"], # A cites B and an external
                "10.1/B": ["10.1/C"],
                "10.1/C": []
            }.get(doi, [])

        graph_dot = self.service.build_graph(["My Collection"])
        
        expected_dot_lines = [
            "digraph CitationGraph {",
            '  rankdir="LR";',
            '  "10.1/A" [label="Paper A"];',
            '  "10.1/B" [label="Paper B"];',
            '  "10.1/C" [label="Paper C"];',
            '  "10.1/A" -> "10.1/B";',
            '  "10.1/B" -> "10.1/C";',
            "}"
        ]
        # Compare line by line, ignoring order of nodes/edges as sets
        self.assertIn("digraph CitationGraph {", graph_dot)
        self.assertIn('  rankdir="LR";', graph_dot)
        self.assertIn('  "10.1/A" [label="Paper A"];', graph_dot)
        self.assertIn('  "10.1/B" [label="Paper B"];', graph_dot)
        self.assertIn('  "10.1/C" [label="Paper C"];', graph_dot)
        self.assertIn('  "10.1/A" -> "10.1/B";', graph_dot)
        self.assertIn('  "10.1/B" -> "10.1/C";', graph_dot)
        self.assertIn("}", graph_dot)
        # Ensure no external links (10.999/external) are added as nodes or edges
        self.assertNotIn('10.999/external', graph_dot)


    def test_build_graph_no_dois_in_collection(self):
        item_no_doi = self._create_zotero_item("KEY_X", "Paper X", None)
        self.mock_zotero_gateway.get_items_in_collection.return_value = iter([item_no_doi])
        self.mock_citation_gateway.get_references_by_doi.return_value = []

        graph_dot = self.service.build_graph(["My Collection"])
        
        self.assertIn("digraph CitationGraph {", graph_dot)
        self.assertIn('  rankdir="LR";', graph_dot)
        self.assertIn("}", graph_dot)
        # No nodes or edges should be added if no DOIs are present
        self.assertNotIn("Paper X", graph_dot)

    def test_build_graph_no_references(self):
        item_a = self._create_zotero_item("KEY_A", "Paper A", "10.1/A")
        self.mock_zotero_gateway.get_items_in_collection.return_value = iter([item_a])
        self.mock_citation_gateway.get_references_by_doi.return_value = [] # No references found

        graph_dot = self.service.build_graph(["My Collection"])
        
        self.assertIn("digraph CitationGraph {", graph_dot)
        self.assertIn('  rankdir="LR";', graph_dot)
        self.assertIn('  "10.1/A" [label="Paper A"];', graph_dot) # Node should still be there
        self.assertNotIn("->", graph_dot) # No edges
        self.assertIn("}", graph_dot)

    def test_build_graph_multiple_collections(self):
        item_a = self._create_zotero_item("KEY_A", "Paper A", "10.1/A")
        item_b = self._create_zotero_item("KEY_B", "Paper B", "10.1/B")
        item_c = self._create_zotero_item("KEY_C", "Paper C", "10.1/C") # In a different collection
        
        # Mock gateway for two collections
        def get_items_side_effect(col_id):
            if col_id == "COL_ID_1":
                return iter([item_a, item_b])
            elif col_id == "COL_ID_2":
                return iter([item_c])
            return iter([])

        self.mock_zotero_gateway.get_items_in_collection.side_effect = get_items_side_effect
        self.mock_zotero_gateway.get_collection_id_by_name.side_effect = \
            lambda name: "COL_ID_1" if name == "Collection 1" else \
                         ("COL_ID_2" if name == "Collection 2" else None)

        # A cites B, B cites C
        self.mock_citation_gateway.get_references_by_doi.side_effect = \
            lambda doi: {
                "10.1/A": ["10.1/B"],
                "10.1/B": ["10.1/C"],
                "10.1/C": []
            }.get(doi, [])
        
        graph_dot = self.service.build_graph(["Collection 1", "Collection 2"])
        
        self.assertIn('  "10.1/A" [label="Paper A"];', graph_dot)
        self.assertIn('  "10.1/B" [label="Paper B"];', graph_dot)
        self.assertIn('  "10.1/C" [label="Paper C"];', graph_dot)
        self.assertIn('  "10.1/A" -> "10.1/B";', graph_dot)
        self.assertIn('  "10.1/B" -> "10.1/C";', graph_dot)


if __name__ == '__main__':
    unittest.main()
