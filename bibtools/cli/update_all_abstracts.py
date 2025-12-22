#!/usr/bin/env python3
"""Force update ALL abstracts in raw_springer, even if they already exist."""

import requests
import time
from bibtools.cli.fetch_abstracts import (
    fetch_abstract_springer,
    fetch_abstract_openalex,
    fetch_abstract_crossref,
    fetch_abstract_semanticscholar,
    fetch_abstract_europepmc,
    fetch_abstract_doi_org
)
from bibtools.utils.config import get_zotero_config, get_springer_api_key

# Load configuration from .env.local
zotero_config = get_zotero_config()
API_KEY = zotero_config['api_key']
LIBRARY_ID = zotero_config['library_id']
COLLECTION_ID = "6WXB8QRV"  # TODO: Move to .env.local as ZOTERO_COLLECTION_ID
SPRINGER_KEY = get_springer_api_key()

print("Updating ALL abstracts in raw_springer collection")
print("=" * 70)
print("This will replace ALL abstracts with complete versions")
print("=" * 70)
print()

# Fetch all items
print("Fetching all items from raw_springer...")
headers = {'Zotero-API-Key': API_KEY}
base_url = f'https://api.zotero.org/groups/{LIBRARY_ID}'

all_items = []
start = 0
limit = 100

while True:
    url = f'{base_url}/collections/{COLLECTION_ID}/items?start={start}&limit={limit}'
    response = requests.get(url, headers=headers)
    items = response.json()
    
    if not items:
        break
    
    all_items.extend(items)
    start += limit
    print(f"  Fetched {len(all_items)} items...")

print(f"\nTotal items: {len(all_items)}")

# Filter items with DOIs
items_with_doi = []
for item in all_items:
    data = item.get('data', {})
    doi = data.get('DOI', '').strip()
    if doi:
        items_with_doi.append({
            'key': item['key'],
            'version': item['version'],
            'doi': doi,
            'title': data.get('title', 'Untitled')[:60],
            'current_abstract': data.get('abstractNote', '').strip(),
            'data': data
        })

print(f"Items with DOI: {len(items_with_doi)}")
print()

# Update all abstracts
updated = 0
failed = 0
skipped = 0

for i, item in enumerate(items_with_doi, 1):
    print(f"[{i}/{len(items_with_doi)}] {item['title']}...")
    
    # Fetch new abstract
    abstract = None
    source = None
    
    # Try Springer API first
    if SPRINGER_KEY:
        abstract = fetch_abstract_springer(item['doi'], SPRINGER_KEY)
        if abstract:
            source = 'Springer API'
    
    # Try other sources
    if not abstract:
        abstract = fetch_abstract_openalex(item['doi'])
        if abstract:
            source = 'OpenAlex'
    
    if not abstract:
        abstract = fetch_abstract_crossref(item['doi'])
        if abstract:
            source = 'CrossRef'
    
    if not abstract:
        abstract = fetch_abstract_semanticscholar(item['doi'])
        if abstract:
            source = 'Semantic Scholar'
    
    if not abstract:
        abstract = fetch_abstract_europepmc(item['doi'])
        if abstract:
            source = 'Europe PMC'
    
    if not abstract:
        abstract = fetch_abstract_doi_org(item['doi'])
        if abstract:
            source = 'DOI.org (scraped)'
    
    # Update if found
    if abstract:
        # Check if it's different/longer than current
        current_len = len(item['current_abstract'])
        new_len = len(abstract)
        
        if new_len > current_len:
            # Update in Zotero
            item['data']['abstractNote'] = abstract
            update_url = f"{base_url}/items/{item['key']}"
            update_headers = {
                **headers,
                'Content-Type': 'application/json',
                'If-Unmodified-Since-Version': str(item['version'])
            }
            
            try:
                update_response = requests.patch(
                    update_url,
                    headers=update_headers,
                    json=item['data']
                )
                
                if update_response.status_code == 204:
                    updated += 1
                    print(f"  ✓ Updated ({current_len} → {new_len} chars) [{source}]")
                else:
                    failed += 1
                    print(f"  ✗ Failed to update")
            except Exception as e:
                failed += 1
                print(f"  ✗ Error: {e}")
        else:
            skipped += 1
            print(f"  → Skipped (current is same/longer: {current_len} chars)")
    else:
        print(f"  ✗ No abstract found")
    
    # Rate limiting
    time.sleep(0.5)

print()
print("=" * 70)
print("✓ Update completed!")
print()
print(f"Total items:     {len(items_with_doi)}")
print(f"Updated:         {updated}")
print(f"Skipped:         {skipped}")
print(f"Failed:          {failed}")
print("=" * 70)
