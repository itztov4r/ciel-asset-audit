"""Validate an IT inventory CSV and produce a readable, escaped HTML report."""
import argparse
import csv
import html
import ipaddress
import json
from collections import Counter
from pathlib import Path

REQUIRED = {'asset_id', 'hostname', 'ip_address', 'os', 'ram_gb', 'location'}


def audit_rows(rows, min_ram=8):
    """Return data-quality findings; this is not a vulnerability scanner."""
    rows = list(rows)
    findings = []
    seen_ids, seen_ips = set(), set()
    for line, row in enumerate(rows, start=2):
        asset = (row.get('asset_id') or '').strip()
        def add(message):
            findings.append({'line': line, 'asset_id': asset or '(vide)', 'message': message})
        for key in sorted(REQUIRED):
            if not (row.get(key) or '').strip():
                add(f'Champ obligatoire vide : {key}')
        if asset:
            if asset in seen_ids:
                add('Identifiant matériel en doublon')
            seen_ids.add(asset)
        address = (row.get('ip_address') or '').strip()
        if address:
            try:
                normalized = str(ipaddress.ip_address(address))
                if normalized in seen_ips:
                    add('Adresse IP en doublon')
                seen_ips.add(normalized)
            except ValueError:
                add('Adresse IP invalide')
        memory = (row.get('ram_gb') or '').strip()
        if memory:
            try:
                ram = int(memory)
                if ram <= 0:
                    add('La RAM doit être un entier positif')
                elif ram < min_ram:
                    add(f'RAM inférieure au seuil configuré ({min_ram} Go)')
            except ValueError:
                add('RAM invalide : entier attendu')
    return {'assets': len(rows), 'findings': findings,
            'os_distribution': dict(Counter((r.get('os') or '').strip() or '(vide)' for r in rows))}


def read_inventory(path):
    with Path(path).open(encoding='utf-8-sig', newline='') as stream:
        reader = csv.DictReader(stream, strict=True)
        if not reader.fieldnames or len(reader.fieldnames) != len(set(reader.fieldnames)):
            raise ValueError('En-têtes CSV absents ou dupliqués')
        missing = REQUIRED - set(reader.fieldnames)
        if missing:
            raise ValueError('Colonnes manquantes : ' + ', '.join(sorted(missing)))
        rows = []
        for line, row in enumerate(reader, start=2):
            if None in row or any(value is None for value in row.values()):
                raise ValueError(f'Ligne {line} : nombre de colonnes incorrect')
            rows.append(row)
        return rows


def render_html(report):
    from report_theme import page, table, bars
    finding_rows = [(f['line'], f['asset_id'], f['message']) for f in report['findings']]
    affected = len({f['line'] for f in report['findings']})
    body = '<div class="grid"><section class="panel"><h2>Répartition des systèmes</h2>'
    body += bars(report['os_distribution'].items()) + '</section>'
    body += '<section class="panel"><h2>Lecture du rapport</h2><p class="note">Chaque observation correspond à une règle de qualité : champ manquant, doublon, adresse IP ou RAM invalide, capacité mémoire sous le seuil configuré.</p><span class="tag">Analyse locale · CSV</span></section></div>'
    body += '<section class="panel"><h2>Points à vérifier</h2>' + table(['Ligne CSV', 'Équipement', 'Observation'], finding_rows)
    if not finding_rows:
        body += '<p class="note">Aucune anomalie détectée par les règles configurées.</p>'
    body += '</section><p class="note">Contrôle de qualité des données uniquement. Aucun scan réseau, diagnostic matériel ni audit de vulnérabilités. Le seuil RAM est une règle pédagogique configurable.</p>'
    return page('Un inventaire plus clair.', 'Vue synthétique des équipements et des points à vérifier dans le fichier CSV fourni.', [('Équipements analysés', report['assets']), ('Lignes sans observation', report['assets'] - affected), ('Observations', len(report['findings']))], body, 'ASSET AUDIT')


def positive(value):
    number = int(value)
    if number < 1:
        raise argparse.ArgumentTypeError('Le seuil doit être positif')
    return number


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('inventory', type=Path)
    parser.add_argument('--min-ram', type=positive, default=8)
    parser.add_argument('--output', type=Path, default=Path('report.html'))
    parser.add_argument('--json', type=Path, dest='json_output')
    parser.add_argument('--fail-on-findings', action='store_true')
    args = parser.parse_args()
    try:
        outputs = [args.output] + ([args.json_output] if args.json_output else [])
        resolved = [p.resolve() for p in outputs]
        if args.inventory.resolve() in resolved or len(set(resolved)) != len(resolved):
            raise ValueError('Les fichiers d’entrée et de sortie doivent être distincts')
        report = audit_rows(read_inventory(args.inventory), args.min_ram)
        args.output.write_text(render_html(report), encoding='utf-8')
        if args.json_output:
            args.json_output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    except (OSError, ValueError, csv.Error) as error:
        parser.exit(2, f'Erreur : {error}\n')
    print(f"{report['assets']} équipements, {len(report['findings'])} observations. Rapport : {args.output}")
    return 1 if args.fail_on_findings and report['findings'] else 0


if __name__ == '__main__':
    raise SystemExit(main())

