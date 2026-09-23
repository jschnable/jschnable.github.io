
from pathlib import Path
import re

p = Path('_data/publications.yml')
text = p.read_text(encoding='utf-8')
old_size = p.stat().st_size
old = "  - name: Arora S\n  - name: Cuellar-Perez KM\n"
new = "  - name: Arora S\n    member_id: arora-sofiya\n  - name: Cuellar-Perez KM\n    member_id: cullar-karla\n"
assert old in text and text.count(old) == 1
text = text.replace(old, new, 1)
m = re.search(r'(id: 2026-jm-embeddings-sorghum-leaf-disease.*?lab_author_count: )4(\n)', text, re.S)
assert m
text = text[:m.start(1)] + m.group(1) + '6' + m.group(2) + text[m.end(2):]
assert 'member_id: arora-sofiya' in text and 'member_id: cullar-karla' in text
p.write_text(text, encoding='utf-8')
print('publications.yml', old_size, '->', p.stat().st_size)
assert p.stat().st_size > 100000

la_path = Path('_data/lab_authors.yml')
la = la_path.read_text(encoding='utf-8')
comment = (
    "# Exhaustive list of current and former Schnable lab authors for publication\n"
    "# member_id linking (lab site) and CV author bolding. Include alumni; active or not,\n"
    "# anyone listed here is a lab author. Add new lab people (and aliases) here first.\n"
)
if not la.lstrip().startswith('# Exhaustive list'):
    la = comment + la

e = "\u00e9"

def replace_id_block(text, entry_id, new_block):
    pat = rf'- id: {re.escape(entry_id)}\n.*?(?=\n- id: |\Z)'
    m = re.search(pat, text, re.S)
    assert m, f'missing {entry_id}'
    return text[:m.start()] + new_block.rstrip() + '\n' + text[m.end():]

arora_new = """- id: arora-sofiya
  name: Sofiya Arora
  aliases:
  - Arora S
  - Arora S.
  - Arora, S
  - Arora, S.
  - Arora, Sofiya
  - S. Arora
  - Sofiya Arora
  active: false
  people_page: peoplepages/Sofiya.md
  orcid: 0009-0004-5357-6094
"""
karla_new = f"""- id: cullar-karla
  name: Karla Cu{e}llar
  aliases:
  - Cu{e}llar K
  - Cu{e}llar K.
  - Cu{e}llar, K
  - Cu{e}llar, K.
  - Cu{e}llar, Karla
  - K. Cu{e}llar
  - Cu{e}llar-Perez KM
  - Cuellar-Perez KM
  - Cu{e}llar-Perez K
  - Cuellar-Perez K
  - Cu{e}llar KM
  - Cuellar KM
  - Cu{e}llar-Perez, KM
  - Cuellar-Perez, KM
  - Cu{e}llar-Perez, K
  - Cuellar-Perez, K
  - K. Cu{e}llar-Perez
  - K. Cuellar-Perez
  - Karla Cu{e}llar
  - Karla Cuellar
  - Karla Cu{e}llar-Perez
  - Karla Cuellar-Perez
  active: true
  people_page: peoplepages/KarlaC2.md
  orcid: 0009-0001-2851-6370
"""
la = replace_id_block(la, 'arora-sofiya', arora_new)
la = replace_id_block(la, 'cullar-karla', karla_new)
assert la.count('- id:') >= 130
assert 'Cuellar-Perez KM' in la
la_path.write_text(la, encoding='utf-8')
print('lab_authors.yml size', la_path.stat().st_size)

agents = Path('AGENTS.md')
site = agents.read_text(encoding='utf-8')
rule = """
### Bold / `member_id` rule (lab authors)
- `_data/lab_authors.yml` is the **exhaustive** list of current **and former** Schnable lab authors used for publication linking and CV bolding.
- Anyone listed there (`active: true` or `active: false`) is a lab author: attach `member_id` on their `authors` row in `_data/publications.yml`, and bold them on the CV.
- Alumni remain lab authors for bolding; do not omit `member_id` just because `active` is false.
- When a new lab person appears on a paper, add them (with publication/CV name aliases) to `_data/lab_authors.yml` **first**, then set `member_id` and bump `lab_author_count`.
- Cross-ref: CV repo `jschnable/schnable-cv` uses the same roster for `\\textbf{}` in `sections/publications.tex`.
"""
insert_after = '- Start with `docs/publications-reference.md` for the current, implemented data model and rendering flow. `docs/publications-data-spec.md` is historical migration/design context.\n'
assert insert_after in site
if 'Bold / `member_id` rule' not in site:
    site = site.replace(insert_after, insert_after + rule, 1)
agents.write_text(site, encoding='utf-8')
print('AGENTS.md size', agents.stat().st_size)
assert 'Bold / `member_id` rule' in agents.read_text(encoding='utf-8')
print('OK')
