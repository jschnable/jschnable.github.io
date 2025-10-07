#!/usr/bin/env python3
"""
Helper script to review lab_authors.yml and identify potential issues.
"""

import yaml
import re
from pathlib import Path
from collections import defaultdict

def load_lab_authors(file_path):
    """Load lab_authors.yml"""
    with open(file_path) as f:
        return yaml.safe_load(f)

def check_for_issues(authors):
    """Check for common issues in the authors list"""
    issues = []

    # Check for missing middle initials issue
    # Group by last name
    by_last_name = defaultdict(list)
    for author in authors:
        parts = author['name'].split()
        if len(parts) >= 2:
            last_name = parts[-1]
            by_last_name[last_name].append(author)

    # Check each author's aliases for middle initial variants
    for author in authors:
        name = author['name']
        aliases = author.get('aliases', [])

        # Look for potential middle initial issues
        # e.g., if we have "Schnable JC" and "Schnable J" as separate aliases
        initials_variants = []
        for alias in aliases:
            # Pattern: LastName Initial(s)
            match = re.match(r'^(\w+)\s+([A-Z]+)\.?$', alias)
            if match:
                # Store last name and normalized initials (without punctuation)
                last_name = match.group(1)
                initials = match.group(2)
                initials_variants.append((last_name, initials, alias))

        # Check if there are different initial patterns (ignoring punctuation)
        if len(initials_variants) > 1:
            # Group by last name and normalize initials
            by_lastname = defaultdict(set)
            for last_name, initials, alias in initials_variants:
                by_lastname[last_name].add(initials)

            # Check if we have different initials for same last name
            for last_name, initials_set in by_lastname.items():
                if len(initials_set) > 1:
                    # We have different initials - this is a real issue
                    variant_aliases = [alias for ln, init, alias in initials_variants if ln == last_name]
                    issues.append({
                        'type': 'middle_initial_variants',
                        'author': name,
                        'variants': variant_aliases,
                        'initials': sorted(initials_set),
                        'message': f"Different initial patterns: {', '.join(sorted(initials_set))} in variants: {', '.join(variant_aliases)}"
                    })

    # Check for duplicate IDs
    id_counts = defaultdict(int)
    for author in authors:
        id_counts[author['id']] += 1

    for author_id, count in id_counts.items():
        if count > 1:
            issues.append({
                'type': 'duplicate_id',
                'id': author_id,
                'count': count,
                'message': f"ID '{author_id}' appears {count} times"
            })

    # Check for authors without aliases
    for author in authors:
        if not author.get('aliases'):
            issues.append({
                'type': 'no_aliases',
                'author': author['name'],
                'message': f"{author['name']} has no aliases"
            })

    return issues

def cross_reference_with_papers(authors, papers_file):
    """Check which bold names from papers.md are matched"""
    # Extract bold names from papers
    with open(papers_file, 'r', encoding='utf-8') as f:
        content = f.read()

    bold_pattern = re.compile(r'\*\*([A-Za-z][^*]+?)\*\*')
    bold_names = set(bold_pattern.findall(content))

    # Filter out non-authors
    non_authors = {
        'BMC Research Notes', 'Preprints', 'Cover Article', 'Research Highlight',
        'Ge Y', 'Yang J'
    }
    bold_names = {n.strip() for n in bold_names if n not in non_authors and not n.endswith('Article')}

    # Build reverse lookup: alias -> author
    alias_to_author = {}
    for author in authors:
        for alias in author.get('aliases', []):
            alias_to_author[alias] = author['name']
        # Also include the main name
        alias_to_author[author['name']] = author['name']

    # Check which bold names are matched
    unmatched = []
    matched = []

    for bold_name in sorted(bold_names):
        if bold_name in alias_to_author:
            matched.append((bold_name, alias_to_author[bold_name]))
        else:
            unmatched.append(bold_name)

    return matched, unmatched

def generate_review_report(output_file):
    """Generate a comprehensive review report"""
    base_dir = Path(__file__).parent.parent
    authors_file = base_dir / '_data' / 'lab_authors.yml'
    papers_file = base_dir / 'papers.md'

    print("Loading lab_authors.yml...")
    authors = load_lab_authors(authors_file)
    print(f"Loaded {len(authors)} authors\n")

    print("=" * 80)
    print("CHECKING FOR ISSUES")
    print("=" * 80)

    issues = check_for_issues(authors)

    if issues:
        print(f"\nFound {len(issues)} potential issues:\n")

        # Group by type
        by_type = defaultdict(list)
        for issue in issues:
            by_type[issue['type']].append(issue)

        for issue_type, issue_list in by_type.items():
            print(f"\n{issue_type.upper().replace('_', ' ')} ({len(issue_list)}):")
            print("-" * 80)
            for issue in issue_list:
                print(f"  • {issue['message']}")
    else:
        print("\n✓ No issues found!")

    print("\n" + "=" * 80)
    print("CROSS-REFERENCE WITH PAPERS.MD")
    print("=" * 80)

    matched, unmatched = cross_reference_with_papers(authors, papers_file)

    print(f"\n✓ Matched {len(matched)} bold-tagged names")

    if unmatched:
        print(f"\n⚠ UNMATCHED bold-tagged names ({len(unmatched)}):")
        print("-" * 80)
        for name in unmatched:
            print(f"  • {name}")
        print("\nThese names appear in papers.md but have no matching alias.")
        print("They may be typos, non-lab collaborators, or need aliases added.")

    print("\n" + "=" * 80)
    print("STATISTICS")
    print("=" * 80)

    active_count = sum(1 for a in authors if a.get('active') == True)
    inactive_count = sum(1 for a in authors if a.get('active') == False)
    unknown_count = len(authors) - active_count - inactive_count

    print(f"\nTotal authors: {len(authors)}")
    print(f"  - Active members: {active_count}")
    print(f"  - Alumni: {inactive_count}")
    print(f"  - Status unknown: {unknown_count}")

    with_pages = sum(1 for a in authors if a.get('people_page'))
    with_orcid = sum(1 for a in authors if a.get('orcid'))

    print(f"\nWith people pages: {with_pages}")
    print(f"With ORCID: {with_orcid}")

    # Calculate average aliases per author
    avg_aliases = sum(len(a.get('aliases', [])) for a in authors) / len(authors)
    print(f"\nAverage aliases per author: {avg_aliases:.1f}")

    print("\n" + "=" * 80)

    # Write detailed output to file
    with open(output_file, 'w') as f:
        f.write("LAB AUTHORS REVIEW REPORT\n")
        f.write("=" * 80 + "\n\n")

        # Write full author list with all aliases
        f.write("FULL AUTHOR LIST\n")
        f.write("=" * 80 + "\n\n")

        for author in authors:
            f.write(f"ID: {author['id']}\n")
            f.write(f"Name: {author['name']}\n")
            if author.get('active') is not None:
                f.write(f"Active: {author['active']}\n")
            if author.get('people_page'):
                f.write(f"Page: {author['people_page']}\n")
            if author.get('orcid'):
                f.write(f"ORCID: {author['orcid']}\n")
            f.write("Aliases:\n")
            for alias in author.get('aliases', []):
                f.write(f"  - {alias}\n")
            f.write("\n")

        # Write unmatched names
        if unmatched:
            f.write("\n" + "=" * 80 + "\n")
            f.write("UNMATCHED BOLD NAMES FROM PAPERS.MD\n")
            f.write("=" * 80 + "\n\n")
            for name in sorted(unmatched):
                f.write(f"  - {name}\n")

        # Write issues
        if issues:
            f.write("\n" + "=" * 80 + "\n")
            f.write("POTENTIAL ISSUES\n")
            f.write("=" * 80 + "\n\n")
            for issue in issues:
                f.write(f"[{issue['type']}] {issue['message']}\n")

    print(f"\nDetailed report written to: {output_file}")

def main():
    base_dir = Path(__file__).parent.parent
    output_file = base_dir / 'docs' / 'lab_authors_review.txt'

    generate_review_report(output_file)

if __name__ == '__main__':
    main()
