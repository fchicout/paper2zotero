from typing import Optional
from arxiv2zotero.core.interfaces import ZoteroGateway
from arxiv2zotero.core.models import ArxivPaper

class CollectionNotFoundError(Exception):
    """Raised when the specified Zotero collection cannot be found."""
    pass

class Arxiv2ZoteroClient:
    def __init__(self, gateway: ZoteroGateway):
        self.gateway = gateway

    def add_paper(self, arxiv_id: str, abstract: str, title: str, folder_name: str) -> bool:
        """
        Adds a paper from arXiv to a specified Zotero collection.
        
        Args:
            arxiv_id: The ID of the arXiv paper.
            abstract: The abstract of the paper.
            title: The title of the paper.
            folder_name: The name of the Zotero collection (folder) to add the item to.
            
        Returns:
            True if the item was successfully added, False otherwise.
            
        Raises:
            CollectionNotFoundError: If the folder_name does not exist in Zotero.
        """
        # 1. Resolve Collection ID
        collection_id = self.gateway.get_collection_id_by_name(folder_name)
        if not collection_id:
            raise CollectionNotFoundError(f"Collection '{folder_name}' not found.")

        # 2. Create Domain Model
        paper = ArxivPaper(arxiv_id=arxiv_id, title=title, abstract=abstract)

        # 3. Create Item via Gateway
        success = self.gateway.create_item(paper, collection_id)
        
        return success
