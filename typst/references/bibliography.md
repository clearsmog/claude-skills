# Bibliographies and Citations in Typst

Typst supports citations and bibliographies using BibTeX (.bib) or Hayagriva (.yml) format files.

## Basic Setup

```typst
// In your document, cite with @label
Some text with a citation @smith2023.
Multiple citations @jones2024 @doe2025.

// At the end of your document
#bibliography("references.bib", title: "References", style: "ieee")
```

## Citation Syntax

```typst
// Basic citation
@smith2023

// Citation with page numbers
@smith2023[p. 42]

// Citation with prefix
@smith2023[see][pp. 10-15]

// Multiple citations
@smith2023 @jones2024

// Suppress author (for "Smith (2023) argues...")
Smith #cite(<smith2023>, form: "year") argues...

// Full citation inline
#cite(<smith2023>, form: "full")
```

## Citation Styles

Common built-in styles:

| Style | Format | Example |
|-------|--------|---------|
| `"ieee"` | Numeric | [1], [2], [3] |
| `"apa"` | Author-year | (Smith, 2023) |
| `"chicago-author-date"` | Author-year | (Smith 2023) |
| `"chicago-notes"` | Footnotes | ¹ |
| `"mla"` | Author-page | (Smith 42) |
| `"harvard-cite-them-right"` | Author-year | (Smith, 2023) |
| `"american-physics-society"` | Numeric | [1] |
| `"nature"` | Numeric superscript | ¹ |

```typst
#bibliography("refs.bib", style: "apa")
```

## BibTeX Format (.bib files)

### Common Entry Types

```bibtex
@article{smith2023,
  title = {Title of the Article},
  author = {Smith, John and Doe, Jane},
  journal = {Journal Name},
  year = {2023},
  volume = {10},
  number = {3},
  pages = {123--145},
  doi = {10.1234/example.2023.001},
  url = {https://doi.org/10.1234/example.2023.001},
}

@book{doe2025,
  title = {Book Title},
  author = {Doe, Jane},
  publisher = {Publisher Name},
  year = {2025},
  isbn = {978-0-123456-78-9},
  url = {https://example.com/book},
}

@inproceedings{conference2024,
  title = {Conference Paper Title},
  author = {Author, First and Author, Second},
  booktitle = {Proceedings of the Conference},
  year = {2024},
  pages = {1--10},
  doi = {10.1234/conf.2024.001},
}

@online{webresource,
  title = {Web Page Title},
  author = {Author Name},
  year = {2024},
  url = {https://example.com/page},
  urldate = {2024-11-19},
}

@misc{software2024,
  title = {Software Name},
  author = {Developer, Name},
  year = {2024},
  version = {1.2.3},
  url = {https://github.com/user/repo},
  note = {Open source software},
}

@thesis{phd2023,
  title = {Dissertation Title},
  author = {Student, Graduate},
  school = {University Name},
  year = {2023},
  type = {PhD thesis},
  url = {https://example.edu/thesis},
}
```

### Author Formatting

```bibtex
// Single author
author = {Smith, John},

// Multiple authors (use "and")
author = {Smith, John and Doe, Jane and Brown, Bob},

// Corporate author
author = {{World Health Organization}},

// With Jr., III, etc.
author = {King, Martin Luther, Jr.},
```

## Hayagriva Format (.yml files)

Typst's native bibliography format with better type safety:

```yaml
smith2023:
  type: article
  title: Title of the Article
  author:
    - Smith, John
    - Doe, Jane
  date: 2023
  parent:
    type: periodical
    title: Journal Name
    volume: 10
    issue: 3
  page-range: 123-145
  doi: 10.1234/example.2023.001
  url: https://doi.org/10.1234/example.2023.001

doe2025:
  type: book
  title: Book Title
  author: Doe, Jane
  publisher: Publisher Name
  date: 2025
  isbn: 978-0-123456-78-9
  url: https://example.com/book

webresource:
  type: web
  title: Web Page Title
  author: Author Name
  date: 2024
  url: https://example.com/page
  accessed: 2024-11-19
```

## Bibliography Function Parameters

```typst
#bibliography(
  "file.bib",           // Path to bibliography file (or array of paths)
  title: "References",  // Section title (or none for no title)
  style: "ieee",        // Citation style
  full: false,          // true = show all entries; false = only cited ones
)

// Multiple bibliography files
#bibliography(("main.bib", "extra.bib"))

// No title
#bibliography("refs.bib", title: none)

// Show all entries even if not cited
#bibliography("refs.bib", full: true)
```

## Best Practices

### Always Include URLs

```bibtex
// Good - includes DOI/URL for verification
@article{example,
  title = {Article Title},
  author = {Author, Name},
  journal = {Journal},
  year = {2023},
  doi = {10.1234/example},
  url = {https://doi.org/10.1234/example},
}

// Bad - no way to verify source
@article{example,
  title = {Article Title},
  author = {Author, Name},
  journal = {Journal},
  year = {2023},
}
```

### Cite Everything Relevant

Don't just list references - cite them in text:

```typst
// Good - citation in context
Recent studies @smith2023 @jones2024 have shown...

// Bad - references exist but aren't cited
Recent studies have shown... (uncited)
```

### Consistent Formatting

```bibtex
// Use consistent key naming
@article{smith2023,      // author + year
@article{smith:ml:2023,  // author:topic:year
@article{Smith_2023,     // Author_year

// Pick one style and stick with it
```

### Handle Special Characters

```bibtex
// Escape special characters
title = {The {\LaTeX} Companion},
title = {100\% Effective Methods},
title = {C++ Programming},

// Use proper dashes
pages = {10--20},  // en-dash for ranges
note = {First edition---revised},  // em-dash
```

## Working with Templates

Some templates handle bibliography internally:

```typst
// Template manages bibliography
#import "@preview/charged-ieee:0.1.4": *

#show: ieee.with(
  // ...
  bibliography: bibliography("refs.bib"),  // Passed to template
)

// Don't add another #bibliography() call
```

Check template documentation for bibliography handling.

## Troubleshooting

### "Reference not found"

```typst
// Check for typos in citation key
@smtih2023  // Typo!
@smith2023  // Correct

// Ensure bibliography is included
#bibliography("refs.bib")  // Must be in document
```

### Style Not Working

```typst
// Check style name spelling
style: "IEEE"   // Wrong (case-sensitive)
style: "ieee"   // Correct
```

### Special Characters in Titles

```bibtex
// Protect case-sensitive words with braces
title = {A Study of {DNA} Replication},
title = {{COVID-19} Impact Analysis},
```

### Missing Fields Warning

Add required fields for the entry type:

```bibtex
// @article requires: author, title, journal, year
// @book requires: author, title, publisher, year
// @inproceedings requires: author, title, booktitle, year
```
