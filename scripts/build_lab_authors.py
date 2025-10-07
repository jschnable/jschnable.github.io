#!/usr/bin/env python3
"""
Build lab_authors.yml by extracting names from multiple sources.
"""

import yaml
import re
from pathlib import Path
from collections import defaultdict

def extract_from_people_yml(people_file):
    """Extract names from _data/people.yml"""
    with open(people_file) as f:
        people = yaml.safe_load(f)

    authors = []
    for person in people:
        name = person.get('name', '')
        page_path = person.get('page_path', '')
        orcid = person.get('orcid', '')

        # Create author entry
        author = {
            'name': name,
            'page_path': page_path if page_path else None,
            'orcid': orcid if orcid else None,
            'active': True,
            'aliases': set()
        }
        authors.append(author)

    return authors

def extract_from_alumni_yml(alumni_file):
    """Extract names from _data/alumni.yml"""
    with open(alumni_file) as f:
        alumni_data = yaml.safe_load(f)

    authors = []
    for section in alumni_data:
        for person in section.get('people', []):
            name = person.get('name', '')
            link = person.get('link', '')
            orcid = person.get('orcid', '')

            author = {
                'name': name,
                'page_path': link if link else None,
                'orcid': orcid if orcid else None,
                'active': False,
                'aliases': set()
            }
            authors.append(author)

    return authors

def extract_from_peoplepages(peoplepages_dir):
    """Extract names from peoplepages/*.md front matter"""
    peoplepages_path = Path(peoplepages_dir)
    authors = []

    for md_file in peoplepages_path.glob('*.md'):
        if md_file.name == 'coi.md':
            continue

        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Extract front matter
        match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
        if match:
            try:
                front_matter = yaml.safe_load(match.group(1))
                if 'title' in front_matter:
                    name = front_matter['title']
                    # Check for ORCID in content
                    orcid_match = re.search(r'ORCID ID:\*\*\s*(\d{4}-\d{4}-\d{4}-\d{3}[0-9X])', content)
                    orcid = orcid_match.group(1) if orcid_match else None

                    author = {
                        'name': name,
                        'page_path': f'peoplepages/{md_file.name}',
                        'orcid': orcid,
                        'active': None,  # Will be determined by merging
                        'aliases': set()
                    }
                    authors.append(author)
            except:
                pass

    return authors

def extract_bold_names_from_papers(papers_file):
    """Extract all bold-tagged author names from papers.md"""
    with open(papers_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find all **Name** patterns
    bold_pattern = re.compile(r'\*\*([A-Za-z][^*]+?)\*\*')
    matches = bold_pattern.findall(content)

    # Filter out non-author entries
    non_authors = {
        'BMC Research Notes', 'Preprints', 'Cover Article', 'Research Highlight',
        'Ge Y', 'Yang J'  # These are collaborators, not lab members
    }

    author_names = set()
    for match in matches:
        # Skip entries that look like journal names or section headers
        if match not in non_authors and not match.endswith('Article'):
            author_names.add(match.strip())

    return author_names

def name_to_id(name):
    """Convert name to kebab-case ID"""
    # Remove quotes and special characters
    clean = name.replace('"', '').replace("'", '')
    # Remove parenthetical nicknames
    clean = re.sub(r'\s*\([^)]+\)\s*', ' ', clean)

    # Try to extract last name and initials
    parts = clean.split()
    if len(parts) >= 2:
        last = parts[-1].lower()
        # Get first name or initial
        first = parts[0].lower()
        # Remove any remaining special chars
        last = re.sub(r'[^a-z-]', '', last)
        first = re.sub(r'[^a-z]', '', first)
        return f"{last}-{first}"
    else:
        # Fallback for single names
        return re.sub(r'[^a-z-]', '', clean.lower())

def generate_aliases(name, bold_variants):
    """Generate common alias variants for a name"""
    aliases = set()

    # Add the exact name
    aliases.add(name)

    # Parse name components
    parts = name.replace('"', '').replace("'", '').split()
    if len(parts) < 2:
        return aliases

    # Extract components
    first_name = parts[0]
    last_name = parts[-1]
    middle_parts = parts[1:-1] if len(parts) > 2 else []

    # Get initials
    first_initial = first_name[0] if first_name else ''
    middle_initials = ''.join([p[0] for p in middle_parts])

    # Common patterns
    # LastName FirstInitial
    if first_initial:
        aliases.add(f"{last_name} {first_initial}")
        # LastName FirstInitial.
        aliases.add(f"{last_name} {first_initial}.")
        # LastName, FirstInitial
        aliases.add(f"{last_name}, {first_initial}")
        # LastName, FirstInitial.
        aliases.add(f"{last_name}, {first_initial}.")

    # With middle initials
    if middle_initials:
        full_initials = first_initial + middle_initials
        # LastName FirstMiddleInitials
        aliases.add(f"{last_name} {full_initials}")
        # LastName FirstInitial MiddleInitials
        aliases.add(f"{last_name} {first_initial} {middle_initials}")
        # LastName, FirstMiddleInitials
        aliases.add(f"{last_name}, {full_initials}")

    # Full name with comma
    aliases.add(f"{last_name}, {first_name}")
    if middle_parts:
        aliases.add(f"{last_name}, {first_name} {' '.join(middle_parts)}")

    # FirstInitial. LastName (e.g., J. C. Schnable)
    if first_initial:
        if middle_initials:
            aliases.add(f"{first_initial}. {middle_initials}. {last_name}")
            aliases.add(f"{first_initial} {middle_initials} {last_name}")
        else:
            aliases.add(f"{first_initial}. {last_name}")

    # Add any matching bold variants
    name_parts_lower = set([p.lower() for p in parts])
    for variant in bold_variants:
        variant_parts = variant.split()
        variant_parts_lower = set([p.lower().rstrip('.,') for p in variant_parts])
        # If the variant shares the last name, include it
        if last_name.lower() in variant_parts_lower:
            aliases.add(variant)

    return aliases

def merge_authors(people_authors, alumni_authors, peoplepage_authors, bold_names):
    """Merge all author sources into unified list"""
    # Create lookup by normalized name
    author_map = {}

    def normalize_for_matching(name):
        """Normalize name for matching purposes"""
        return re.sub(r'[^a-z]', '', name.lower())

    # Add people (current members)
    for author in people_authors:
        norm = normalize_for_matching(author['name'])
        author_map[norm] = author

    # Add alumni
    for author in alumni_authors:
        norm = normalize_for_matching(author['name'])
        if norm not in author_map:
            author_map[norm] = author
        else:
            # Merge data if exists in both
            if author.get('orcid') and not author_map[norm].get('orcid'):
                author_map[norm]['orcid'] = author['orcid']

    # Add peoplepages
    for author in peoplepage_authors:
        norm = normalize_for_matching(author['name'])
        if norm not in author_map:
            author_map[norm] = author
        else:
            # Merge ORCID if available
            if author.get('orcid') and not author_map[norm].get('orcid'):
                author_map[norm]['orcid'] = author['orcid']
            # Prefer peoplepages path if not set
            if author.get('page_path') and not author_map[norm].get('page_path'):
                author_map[norm]['page_path'] = author['page_path']

    # Generate aliases for each author
    for norm, author in author_map.items():
        author['aliases'] = generate_aliases(author['name'], bold_names)

    return list(author_map.values())

def write_lab_authors_yml(authors, output_file):
    """Write the final lab_authors.yml file"""
    output = []

    # Sort by last name
    def get_last_name(author):
        parts = author['name'].split()
        return parts[-1] if parts else ''

    sorted_authors = sorted(authors, key=get_last_name)

    for author in sorted_authors:
        entry = {
            'id': name_to_id(author['name']),
            'name': author['name']
        }

        # Convert aliases set to sorted list
        if author['aliases']:
            # Remove the exact name from aliases
            aliases_list = sorted([a for a in author['aliases'] if a != author['name']])
            if aliases_list:
                entry['aliases'] = aliases_list

        if author.get('active') is not None:
            entry['active'] = author['active']

        if author.get('page_path'):
            entry['people_page'] = author['page_path']

        if author.get('orcid'):
            entry['orcid'] = author['orcid']

        output.append(entry)

    # Write to file
    with open(output_file, 'w', encoding='utf-8') as f:
        yaml.dump(output, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

def main():
    base_dir = Path(__file__).parent.parent

    # Extract from all sources
    print("Extracting from _data/people.yml...")
    people_authors = extract_from_people_yml(base_dir / '_data' / 'people.yml')
    print(f"  Found {len(people_authors)} current members")

    print("Extracting from _data/alumni.yml...")
    alumni_authors = extract_from_alumni_yml(base_dir / '_data' / 'alumni.yml')
    print(f"  Found {len(alumni_authors)} alumni")

    print("Extracting from peoplepages/*.md...")
    peoplepage_authors = extract_from_peoplepages(base_dir / 'peoplepages')
    print(f"  Found {len(peoplepage_authors)} people pages")

    print("Extracting bold names from papers.md...")
    bold_names = extract_bold_names_from_papers(base_dir / 'papers.md')
    print(f"  Found {len(bold_names)} unique bold-tagged names")

    print("\nMerging all sources...")
    merged_authors = merge_authors(people_authors, alumni_authors, peoplepage_authors, bold_names)
    print(f"  Total unique authors: {len(merged_authors)}")

    output_file = base_dir / '_data' / 'lab_authors.yml'
    print(f"\nWriting to {output_file}...")
    write_lab_authors_yml(merged_authors, output_file)

    print("Done!")

if __name__ == '__main__':
    main()
