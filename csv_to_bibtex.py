#!/usr/bin/env python3
"""
CSV to BibTeX Converter for Springer Search Results (v2 - Improved)
Converts Springer search results CSV to properly formatted BibTeX file
"""

import csv
import re
import html
from unicodedata import normalize

def clean_text(text):
    """Clean and normalize text for BibTeX"""
    if not text:
        return ""
    
    # Decode HTML entities
    text = html.unescape(text)
    
    # Normalize unicode characters
    text = normalize('NFKD', text)
    
    # Replace em/en dashes with LaTeX equivalents
    text = text.replace('–', '--').replace('—', '---')
    
    return text.strip()

def create_bibtex_key(authors, year, title):
    """Create a unique BibTeX key"""
    # Get first author's last name
    if authors:
        # Try to extract first surname
        match = re.search(r'([A-Z][a-z]+)\b', authors)
        last_name = match.group(1) if match else 'Unknown'
    else:
        last_name = 'Unknown'
    
    # Get first meaningful word of title (>3 chars)
    title_words = [w for w in re.findall(r'\w+', title) if len(w) > 3]
    first_word = title_words[0] if title_words else 'paper'
    
    # Create key: LastName_Year_FirstWord
    key = f"{last_name}_{year}_{first_word}"
    
    # Remove special characters and make safe
    key = re.sub(r'[^a-zA-Z0-9_]', '', key)
    
    return key

def format_authors_simple(authors_str):
    """
    Simplified author formatting that preserves original structure
    Springer concatenates names - we'll use as-is with minimal processing
    """
    if not authors_str:
        return ""
    
    # Just clean up the text and return
    # Users can manually fix author formatting if needed
    return clean_text(authors_str)

def get_entry_type(content_type):
    """Map Springer content type to BibTeX entry type"""
    content_type_lower = content_type.lower()
    
    if 'conference' in content_type_lower:
        return 'inproceedings'
    elif 'article' in content_type_lower or 'review' in content_type_lower:
        return 'article'
    elif 'book' in content_type_lower:
        return 'book'
    else:
        return 'misc'

def escape_bibtex_special_chars(text):
    """Escape special characters for BibTeX"""
    # Don't escape if already appears to be LaTeX
    if '\\' in text:
        return text
    
    # Escape special chars
    replacements = {
        '&': '\\&',
        '%': '\\%',
        '$': '\\$',
        '#': '\\#',
        '_': '\\_',
        '{': '\\{',
        '}': '\\}',
    }
    
    for old, new in replacements.items():
        text = text.replace(old, new)
    
    return text

def csv_to_bibtex(csv_file, output_base, entries_per_file=50):
    """Convert CSV to BibTeX, splitting into multiple files"""
    
    entries = []
    used_keys = set()
    
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            # Extract and clean data
            title = clean_text(row.get('Item Title', ''))
            authors = row.get('Authors', '').strip()  # Keep original
            year = row.get('Publication Year', '').strip()
            doi = row.get('Item DOI', '').strip()
            url = row.get('URL', '').strip()
            content_type = row.get('Content Type', 'Article')
            
            # Additional fields
            journal = clean_text(row.get('Publication Title', ''))
            book_series = clean_text(row.get('Book Series Title', ''))
            volume = row.get('Journal Volume', '').strip()
            issue = row.get('Journal Issue', '').strip()
            
            # Skip empty entries
            if not title:
                continue
            
            # Create BibTeX key (ensure uniqueness)
            base_key = create_bibtex_key(authors, year, title)
            key = base_key
            counter = 1
            while key in used_keys:
                key = f"{base_key}{counter}"
                counter += 1
            used_keys.add(key)
            
            # Determine entry type
            entry_type = get_entry_type(content_type)
            
            # Format authors (simplified)
            formatted_authors = format_authors_simple(authors)
            
            # Build BibTeX entry
            entry = f"@{entry_type}{{{key},\n"
            
            # Add title
            entry += f"  title = {{{title}}},\n"
            
            # Add authors (with note if empty)
            if formatted_authors:
                entry += f"  author = {{{formatted_authors}}},\n"
            else:
                entry += f"  author = {{Anonymous}},\n"
            
            # Add year
            if year:
                entry += f"  year = {{{year}}},\n"
            
            # Add DOI
            if doi:
                entry += f"  doi = {{{doi}}},\n"
            
            # Add URL
            if url:
                entry += f"  url = {{{url}}},\n"
            
            # Add journal/booktitle based on type
            if entry_type == 'article' and journal:
                entry += f"  journal = {{{journal}}},\n"
            elif entry_type == 'inproceedings':
                if journal:
                    entry += f"  booktitle = {{{journal}}},\n"
                if book_series:
                    entry += f"  series = {{{book_series}}},\n"
            
            # Add volume/issue
            if volume:
                entry += f"  volume = {{{volume}}},\n"
            if issue:
                entry += f"  number = {{{issue}}},\n"
            
            # Add publisher note
            entry += f"  publisher = {{Springer}},\n"
            
            # Remove trailing comma and close entry
            entry = entry.rstrip(',\n') + "\n}\n"
            
            entries.append(entry)
    
    # Split entries into multiple files
    total_entries = len(entries)
    num_files = (total_entries + entries_per_file - 1) // entries_per_file
    
    output_files = []
    for i in range(num_files):
        start_idx = i * entries_per_file
        end_idx = min((i + 1) * entries_per_file, total_entries)
        chunk = entries[start_idx:end_idx]
        
        # Create filename with part number
        if num_files > 1:
            output_file = f"{output_base}_part{i+1}.bib"
        else:
            output_file = f"{output_base}.bib"
        
        # Write to file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("\n".join(chunk))
        
        output_files.append(output_file)
    
    return total_entries, output_files

if __name__ == "__main__":
    input_csv = "SearchResults (1).csv"
    output_base = "springer_results"
    entries_per_file = 50  # Split into files of 50 entries each
    
    print("🔄 Converting CSV to BibTeX (v2 - Improved)...")
    count, files = csv_to_bibtex(input_csv, output_base, entries_per_file)
    print(f"✅ Successfully converted {count} entries!")
    print(f"📄 Created {len(files)} file(s):")
    for file in files:
        print(f"   - {file}")
    print(f"\n💡 Note: Author formatting may need manual review")
    print(f"   Springer concatenates names without clear separators")
