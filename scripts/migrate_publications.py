#!/usr/bin/env python3
"""
Migrate publications from papers.md to _data/publications.yml
"""

import yaml
import re
from pathlib import Path
from collections import defaultdict
import html

def load_lab_authors(file_path):
    """Load lab_authors.yml and build alias lookup"""
    with open(file_path) as f:
        authors_data = yaml.safe_load(f)

    # Build reverse lookup: alias -> member_id
    alias_to_id = {}
    for author in authors_data:
        member_id = author['id']
        # Add main name
        alias_to_id[author['name']] = member_id
        # Add all aliases
        for alias in author.get('aliases', []):
            alias_to_id[alias] = member_id

    return alias_to_id

def normalize_author_name(name):
    """Normalize author name for matching"""
    # Remove extra whitespace
    name = ' '.join(name.split())
    return name

def extract_bold_authors(text):
    """Extract all bold-tagged author names from text"""
    # Pattern for **Author Name** (Markdown)
    markdown_bold = re.compile(r'\*\*([^*]+?)\*\*')
    markdown_matches = markdown_bold.findall(text)

    # Pattern for <b>Author Name</b> (HTML)
    html_bold = re.compile(r'<b>([^<]+?)</b>')
    html_matches = html_bold.findall(text)

    return markdown_matches + html_matches

def parse_author_list(author_string, alias_to_id):
    """Parse author string and return list of author objects and optional author_note"""
    authors = []
    author_note = None

    # Remove year patterns like (2025) from author string
    author_string = re.sub(r'\(\d{4}\)', '', author_string)

    # Check for truncated author list pattern like "(48th of 56 authors)" or "(31 of 44 authors)"
    position_match = re.search(r'\((\d+)(?:st|nd|rd|th)?\s+of\s+(\d+)\s+authors\)', author_string)
    if position_match:
        position = position_match.group(1)
        total = position_match.group(2)
        # Find which author has this position marker (should be bold)
        # Look for the pattern: **Author** (position)
        author_with_pos = re.search(r'(\*\*[^*]+\*\*|<b>[^<]+</b>)\s*\(' + position + r'(?:st|nd|rd|th)?\s+of', author_string)
        if author_with_pos:
            author_name_raw = author_with_pos.group(1)
            # Clean the bold markers to get name
            author_name = re.sub(r'\*\*|<b>|</b>', '', author_name_raw).strip()
            author_note = f"{author_name} is {position} of {total} authors"

        # Remove the position pattern from string
        author_string = re.sub(r'\(\d+(?:st|nd|rd|th)\s+of\s+\d+\s+authors\)', '', author_string)

    # Normalize bold tags - move commas outside bold tags
    # <b>Name,</b> -> <b>Name</b>,
    author_string = re.sub(r'<b>([^<]+?),\s*</b>', r'<b>\1</b>, ', author_string)
    # **Name,** -> **Name**,
    author_string = re.sub(r'\*\*([^*]+?),\s*\*\*', r'**\1**, ', author_string)

    # Split by "..." to find truncated sections
    parts = re.split(r'\s*\.\.\.\s*', author_string)

    for i, section in enumerate(parts):
        section = section.strip()
        if not section:
            continue

        # Parse authors in this section
        section_authors = []
        author_parts = re.split(r',\s+', section)

        for part in author_parts:
            part = part.strip()
            if not part:
                continue

            # Check for 'and' separator
            if ' and ' in part:
                sub_parts = part.split(' and ')
                for sub in sub_parts:
                    sub = sub.strip()
                    if sub:
                        section_authors.append(_process_single_author(sub, alias_to_id))
            else:
                section_authors.append(_process_single_author(part, alias_to_id))

        # Add the authors from this section
        authors.extend([a for a in section_authors if a is not None])

        # If there are more sections, add a truncation marker
        if i < len(parts) - 1:
            authors.append({'truncated': True})

    return authors, author_note

def _process_single_author(author_str, alias_to_id):
    """Process a single author entry, detecting bold and matching to lab members"""
    if not author_str or author_str == '...':
        return None

    # Remove any position information like (31 of 44 authors) from individual author
    author_str = re.sub(r'\s*\(\d+(?:st|nd|rd|th)?\s+of\s+\d+\s+authors\)', '', author_str)

    # Check if author is bold (lab member)
    # Markdown format: **Author Name**
    markdown_bold = re.match(r'^\*\*([^*]+)\*\*$', author_str)
    # HTML format: <b>Author Name</b>
    html_bold = re.match(r'^<b>([^<]+)</b>$', author_str)

    if markdown_bold:
        author_name = markdown_bold.group(1).strip()
        is_bold = True
    elif html_bold:
        author_name = html_bold.group(1).strip()
        is_bold = True
    else:
        # Not bold - clean up any remaining HTML tags
        author_name = re.sub(r'<[^>]+>', '', author_str).strip()
        author_name = re.sub(r'\*\*?', '', author_name).strip()  # Remove any stray asterisks
        is_bold = False

    if not author_name:
        return None

    # Strip whitespace first
    author_name = author_name.strip()

    # Remove leading "and"
    author_name = re.sub(r'^and\s+', '', author_name, flags=re.IGNORECASE).strip()

    # Clean up any trailing punctuation and whitespace
    author_name = re.sub(r'[,."\'\s]+$', '', author_name)

    # For bold authors, try to find member_id
    member_id = None
    if is_bold:
        normalized = normalize_author_name(author_name)
        member_id = alias_to_id.get(normalized)

        # Try fuzzy matching if not found
        if not member_id:
            for alias, mid in alias_to_id.items():
                if alias.replace(',', '').replace('.', '').replace(' ', '').lower() == \
                   normalized.replace(',', '').replace('.', '').replace(' ', '').lower():
                    member_id = mid
                    break

    author_obj = {'name': author_name}
    if member_id:
        author_obj['member_id'] = member_id

    return author_obj

def extract_year_from_line(line):
    """Extract year from publication line"""
    # Look for (YYYY) pattern
    year_match = re.search(r'\((\d{4})\)', line)
    if year_match:
        return int(year_match.group(1))
    return None

def extract_title_and_url(line):
    """Extract title and URL from markdown link or HTML link"""
    # Pattern: [Title text](URL) (Markdown)
    markdown_match = re.search(r'\[(.+?)\]\((.+?)\)', line)
    if markdown_match:
        title = markdown_match.group(1).strip()
        url = markdown_match.group(2).strip()
        # Clean up title - remove formatting
        title = re.sub(r'\*([^*]+)\*', r'\1', title)  # Remove italics
        return title, url

    # Pattern: <a href="URL">Title text</a> (HTML)
    html_match = re.search(r'<a href=["\']([^"\']+)["\']>(.+?)</a>', line)
    if html_match:
        url = html_match.group(1).strip()
        title = html_match.group(2).strip()
        # Clean up HTML entities and tags
        title = html.unescape(title)
        title = re.sub(r'<[^>]+>', '', title)  # Remove any remaining tags
        return title, url

    return None, None

def extract_journal(line):
    """Extract journal name from line"""
    # Journal is typically in italics: *Journal Name* (Markdown) or <i>Journal Name</i> (HTML)

    # Remove all bold markers first to avoid confusion (both formats)
    temp_line = re.sub(r'\*\*[^*]+?\*\*', '', line)
    temp_line = re.sub(r'<b>[^<]+?</b>', '', temp_line)

    # Try Markdown italics first
    matches = re.findall(r'\*([^*]+?)\*', temp_line)
    for match in matches:
        match = match.strip()
        # Skip if it's part of doi or biorxiv
        if 'doi:' in match.lower() or 'biorxiv' in match.lower() or 'agrirxiv' in match.lower():
            continue
        # Skip empty or very short matches
        if len(match) < 3:
            continue
        # This is likely the journal
        return match

    # Try HTML italics
    html_matches = re.findall(r'<i>([^<]+?)</i>', temp_line)
    for match in html_matches:
        match = match.strip()
        if 'doi:' in match.lower() or 'biorxiv' in match.lower() or 'agrirxiv' in match.lower():
            continue
        if len(match) < 3:
            continue
        return match

    return None

def extract_doi(line):
    """Extract primary DOI from line"""
    # Look for doi: pattern
    match = re.search(r'doi:\s*(10\.\S+)', line)
    if match:
        doi = match.group(1).strip()
        # Remove trailing period or other punctuation
        doi = doi.rstrip('.,;')
        return doi
    return None

def extract_notes(line):
    """Extract additional notes like bioRxiv DOIs"""
    notes = []

    # Look for bioRxiv/agriRxiv DOIs
    biorxiv_match = re.search(r'\*bioRxiv\*\s*doi:\s*(10\.\S+)', line)
    if biorxiv_match:
        notes.append({'bioRxiv': biorxiv_match.group(1).strip().rstrip('.,;')})

    agrirxiv_match = re.search(r'\*agriRxiv\*\s*doi:\s*(10\.\S+)', line)
    if agrirxiv_match:
        notes.append({'agriRxiv': agrirxiv_match.group(1).strip().rstrip('.,;')})

    return notes if notes else None

def create_pub_id(year, authors_list, title):
    """Generate a unique publication ID"""
    # Use year and first author's last name (skip truncation markers)
    first_real_author = next((a for a in authors_list if 'truncated' not in a), None) if authors_list else None
    first_author = first_real_author['name'] if first_real_author else 'unknown'
    # Extract last name
    parts = first_author.split()
    last_name = parts[-1] if parts else 'unknown'

    # Clean last name
    last_name = re.sub(r'[^a-z]', '', last_name.lower())

    # Get first few words of title
    title_words = re.sub(r'[^a-zA-Z\s]', '', title.lower()).split()[:3]
    title_slug = '-'.join(title_words)

    return f"{year}-{last_name}-{title_slug}"

def parse_papers_md(papers_file, alias_to_id):
    """Parse papers.md and extract publications"""
    with open(papers_file, 'r', encoding='utf-8') as f:
        content = f.read()

    publications = []
    current_year = None
    current_status = 'published'

    lines = content.split('\n')
    i = 0

    while i < len(lines):
        line = lines[i].strip()

        # Check for year heading
        year_heading = re.match(r'^\*\*(\d{4})\*\*$', line)
        if year_heading:
            current_year = int(year_heading.group(1))
            current_status = 'published'
            i += 1
            continue

        # Check for Preprints heading
        if re.match(r'^\*\*Preprints\*\*$', line):
            current_year = None
            current_status = 'preprint'
            i += 1
            continue

        # Skip altmetric badges and other HTML
        if line.startswith('<div') or line.startswith('</div>'):
            i += 1
            continue

        # Check for publication bullet point
        if line.startswith('*') and not line.startswith('**'):
            # This is a publication entry
            pub_line = line[1:].strip()  # Remove leading *

            # Sometimes publications span multiple lines
            # Look ahead to see if next lines continue this entry
            full_line = pub_line
            j = i + 1
            while j < len(lines):
                next_line = lines[j].strip()
                if next_line and not next_line.startswith('*') and not next_line.startswith('<div') and not next_line.startswith('**'):
                    full_line += ' ' + next_line
                    j += 1
                else:
                    break

            # Extract publication data
            year = extract_year_from_line(full_line)
            if not year and current_year:
                year = current_year

            # If still no year, try to infer from DOI (for preprints)
            if not year:
                doi = extract_doi(full_line)
                if doi:
                    # Try to extract year from bioRxiv/agriRxiv DOI format (e.g., 10.31220/agriRxiv.2025.00339)
                    year_match = re.search(r'(20\d{2})\.\d+', doi)
                    if year_match:
                        year = int(year_match.group(1))

            # Fallback: if preprint and still no year, use current year (2025)
            if not year and current_status == 'preprint':
                year = 2025

            title, url = extract_title_and_url(full_line)

            if title and url:  # Valid publication
                # Extract journal from part after the title link to avoid italics in titles
                # For Markdown: after ](url)
                # For HTML: after </a>
                if '[' in full_line and '](' in full_line:
                    after_title = full_line.split(')', 1)[1] if ')' in full_line else full_line
                elif '</a>' in full_line:
                    after_title = full_line.split('</a>', 1)[1] if '</a>' in full_line else full_line
                else:
                    after_title = full_line

                journal = extract_journal(after_title)
                doi = extract_doi(full_line)
                notes = extract_notes(full_line)

                # Ensure title ends with a period
                if title and not title.endswith('.'):
                    title = title + '.'

                # Extract authors from the part before the title
                # Handle both Markdown links [Title](url) and HTML links <a href="url">Title</a>
                if '[' in full_line:
                    before_title = full_line.split('[')[0]
                elif '<a ' in full_line or '<a\t' in full_line:
                    # Split on <a href or <a\t to get text before link
                    before_title = re.split(r'<a\s+', full_line, maxsplit=1)[0]
                else:
                    before_title = ''
                authors_list, author_note = parse_author_list(before_title, alias_to_id)

                # Determine publication type
                pub_type = 'article'
                if journal:
                    journal_lower = journal.lower()
                    if 'biorxiv' in journal_lower or 'arxiv' in journal_lower:
                        pub_type = 'preprint'
                    elif 'conference' in journal_lower or 'proceedings' in journal_lower:
                        pub_type = 'conference'

                # Create publication object
                pub = {
                    'id': create_pub_id(year, authors_list, title),
                    'year': year,
                    'title': title,
                    'authors': authors_list,
                    'status': current_status,
                    'type': pub_type,
                }

                if journal:
                    pub['journal'] = journal
                if doi:
                    pub['doi'] = doi
                if url:
                    pub['url'] = url
                if notes:
                    pub['notes'] = notes
                if author_note:
                    pub['author_note'] = author_note

                # Add computed fields for sorting
                # Check if first author is a lab member (skip truncated markers)
                first_author_is_lab = False
                if authors_list and len(authors_list) > 0:
                    first_real_author = next((a for a in authors_list if 'truncated' not in a), None)
                    if first_real_author:
                        first_author_is_lab = 'member_id' in first_real_author and first_real_author['member_id'] is not None
                pub['first_author_is_lab_member'] = first_author_is_lab

                # Count lab authors (excluding truncation markers)
                lab_author_count = sum(1 for author in authors_list if 'member_id' in author and author.get('member_id') is not None)
                pub['lab_author_count'] = lab_author_count

                publications.append(pub)

            i = j
            continue

        i += 1

    return publications

def write_publications_yml(publications, output_file):
    """Write publications to YAML file with complex sorting"""

    def sort_key(pub):
        """
        Multi-key sort function:
        1. Year (descending)
        2. Status: "accepted" first (within each year)
        3. First author is lab member (True before False)
        4. Lab author count (descending)
        5. Title (alphabetically)
        """
        year = -pub['year'] if pub['year'] else -9999

        # Status: accepted = 0, others = 1 (so accepted comes first)
        status_priority = 0 if pub.get('status') == 'accepted' else 1

        # First author lab member: True = 0, False = 1 (so True comes first)
        first_lab_priority = 0 if pub.get('first_author_is_lab_member') else 1

        # Lab author count (negative for descending order)
        lab_count = -pub.get('lab_author_count', 0)

        # Title (alphabetically)
        title = pub.get('title', '').lower()

        return (year, status_priority, first_lab_priority, lab_count, title)

    sorted_pubs = sorted(publications, key=sort_key)

    # Clean up author entries - remove None member_ids
    for pub in sorted_pubs:
        for author in pub['authors']:
            if 'member_id' in author and author['member_id'] is None:
                del author['member_id']

    with open(output_file, 'w', encoding='utf-8') as f:
        yaml.dump(sorted_pubs, f, default_flow_style=False, allow_unicode=True,
                  sort_keys=False, width=120)

def main():
    base_dir = Path(__file__).parent.parent

    print("Loading lab authors...")
    alias_to_id = load_lab_authors(base_dir / '_data' / 'lab_authors.yml')
    print(f"  Loaded {len(alias_to_id)} author aliases")

    print("\nParsing papers.md...")
    # Use papers_original.md if it exists, otherwise papers.md
    papers_file = base_dir / 'papers_original.md'
    if not papers_file.exists():
        papers_file = base_dir / 'papers.md'
    publications = parse_papers_md(papers_file, alias_to_id)
    print(f"  Found {len(publications)} publications")

    # Count by year
    by_year = defaultdict(int)
    by_status = defaultdict(int)
    for pub in publications:
        by_year[pub['year']] += 1
        by_status[pub['status']] += 1

    print("\nPublications by year:")
    for year in sorted([y for y in by_year.keys() if y is not None], reverse=True):
        print(f"  {year}: {by_year[year]}")
    if None in by_year:
        print(f"  (no year): {by_year[None]}")

    print("\nPublications by status:")
    for status, count in sorted(by_status.items()):
        print(f"  {status}: {count}")

    # Count lab member matches
    total_authors = sum(len(pub['authors']) for pub in publications)
    matched_authors = sum(1 for pub in publications for author in pub['authors'] if author.get('member_id'))
    print(f"\nAuthor matching:")
    print(f"  Total author entries: {total_authors}")
    print(f"  Matched to lab members: {matched_authors} ({100*matched_authors/total_authors:.1f}%)")

    output_file = base_dir / '_data' / 'publications.yml'
    print(f"\nWriting to {output_file}...")
    write_publications_yml(publications, output_file)

    print("\nDone!")
    print("\nNext steps:")
    print("1. Review _data/publications.yml")
    print("2. Check for any author matching issues")
    print("3. Verify publication counts match papers.md")

if __name__ == '__main__':
    main()
