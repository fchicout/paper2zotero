import argparse
import os
import sys
from arxiv2zotero.infra.zotero_api import ZoteroAPIClient
from arxiv2zotero.client import Arxiv2ZoteroClient, CollectionNotFoundError

def main():
    parser = argparse.ArgumentParser(description="Add an arXiv paper to Zotero.")
    parser.add_argument("--arxiv-id", required=True, help="The arXiv ID of the paper.")
    parser.add_argument("--title", required=True, help="The title of the paper.")
    parser.add_argument("--abstract", required=True, help="The abstract of the paper.")
    parser.add_argument("--folder", required=True, help="The Zotero collection (folder) name.")

    args = parser.parse_args()

    api_key = os.environ.get("ZOTERO_API_KEY")
    group_url = os.environ.get("ZOTERO_TARGET_GROUP")

    if not api_key:
        print("Error: ZOTERO_API_KEY environment variable not set.")
        sys.exit(1)
    
    if not group_url:
        print("Error: ZOTERO_TARGET_GROUP environment variable not set.")
        sys.exit(1)

    # Simple logic to extract group ID. 
    # In a real app, this might deserve its own utility or be part of config validation.
    import re
    match = re.search(r'/groups/(\d+)', group_url)
    group_id = match.group(1) if match else None

    if not group_id:
        print(f"Error: Could not extract Group ID from URL: {group_url}")
        sys.exit(1)

    # Composition Root
    gateway = ZoteroAPIClient(api_key, group_id)
    client = Arxiv2ZoteroClient(gateway)

    try:
        success = client.add_paper(args.arxiv_id, args.abstract, args.title, args.folder)
        if success:
            print(f"Successfully added '{args.title}' to '{args.folder}'.")
        else:
            print(f"Failed to add '{args.title}' to '{args.folder}'. Check logs.")
            sys.exit(1)
    except CollectionNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
