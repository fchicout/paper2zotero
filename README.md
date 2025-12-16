# CSV to BibTeX Converter

Convert Springer search results (CSV format) to BibTeX.

## Description

This Python script converts CSV files exported from Springer to BibTeX format, making it easy to import bibliographic references into reference managers like Zotero, Mendeley, or directly into LaTeX documents.

## Features

- ✅ Automatically converts multiple entries
- ✅ Cleans and normalizes text (HTML entities, Unicode)
- ✅ Generates unique BibTeX keys automatically
- ✅ Detects entry type (article, inproceedings, book, etc.)
- ✅ Preserves DOI and URLs
- ✅ Supports journals, conferences, and book series

## Requirements

- Python 3.6 or higher
- Standard libraries (csv, re, html, unicodedata)

## How to Use

1. Export your Springer search results in CSV format
2. Place the CSV file in the same directory as the script
3. Run the script:

```bash
python csv_to_bibtex_v2.py
```

4. The `springer_results.bib` file will be generated in the same directory

## Customization

To use different files, edit the lines at the end of the script:

```python
input_csv = "your_file.csv"
output_bib = "output.bib"
```

## Output Format

The script generates BibTeX entries in the format:

```bibtex
@article{LastName_2024_Keyword,
  title = {Article Title},
  author = {Authors},
  year = {2024},
  doi = {10.1234/example},
  journal = {Journal Name},
  volume = {10},
  number = {2},
  publisher = {Springer}
}
```

## Notes

- Author names from Springer may need manual formatting
- Springer concatenates names without clear separators
- Review generated entries before using in publications

## License

MIT License

## Author

Developed to facilitate academic bibliographic reference management.
