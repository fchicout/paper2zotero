import requests
from bibtools.utils.config import get_zotero_config

# Load configuration from .env.local
zotero_config = get_zotero_config()
api_key = zotero_config['api_key']
library_id = zotero_config['library_id']
collection_id = "6WXB8QRV"  # TODO: Move to .env.local as ZOTERO_COLLECTION_ID

headers = {'Zotero-API-Key': api_key}

# Get all items (paginated)
all_items = []
start = 0
limit = 1000

print("Fetching all items from raw_springer...")
while True:
    url = f'https://api.zotero.org/groups/{library_id}/collections/{collection_id}/items?start={start}&limit={limit}'
    response = requests.get(url, headers=headers)
    items = response.json()
    
    if not items:
        break
    
    all_items.extend(items)
    start += limit
    print(f"Fetched {len(all_items)} items so far...")

# Count items without abstracts
without_abstract = []
for item in all_items:
    data = item.get('data', {})
    abstract = data.get('abstractNote', '').strip()
    if not abstract:
        title = data.get('title', 'Untitled')[:60]
        doi = data.get('DOI', 'No DOI')
        without_abstract.append({'title': title, 'doi': doi})

print("\n" + "=" * 70)
print(f"Total items in raw_springer: {len(all_items)}")
print(f"Items WITH abstract: {len(all_items) - len(without_abstract)}")
print(f"Items WITHOUT abstract: {len(without_abstract)}")
print("=" * 70)

if without_abstract:
    print("\nItems without abstract:")
    for i, item in enumerate(without_abstract[:10], 1):
        print(f"{i}. {item['title']}")
        print(f"   DOI: {item['doi']}")
    if len(without_abstract) > 10:
        print(f"\n... and {len(without_abstract) - 10} more")
