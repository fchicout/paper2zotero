import requests
from typing import List
from paper2zotero.core.interfaces import CitationGateway

class CrossRefAPIClient(CitationGateway):
    BASE_URL = "https://api.crossref.org/works/"

    def get_references_by_doi(self, doi: str) -> List[str]:
        """
        Retrieves a list of DOIs of papers referenced by the given DOI using CrossRef API.
        Returns an empty list if no references or DOI not found.
        """
        url = f"{self.BASE_URL}{doi}"
        try:
            response = requests.get(url, headers={'User-Agent': 'paper2zotero/1.0 (mailto:fchicout@gmail.com)'})
            response.raise_for_status()  # Raise an exception for HTTP errors
            data = response.json()

            referenced_dois = []
            # CrossRef references are often nested under message.reference
            references = data.get('message', {}).get('reference', [])
            for ref in references:
                if 'DOI' in ref and ref['DOI']:
                    referenced_dois.append(ref['DOI'])
            return referenced_dois
        except requests.exceptions.RequestException as e:
            print(f"Error fetching references for DOI {doi} from CrossRef: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response content: {e.response.text}")
            return []
