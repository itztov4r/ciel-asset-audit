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
        asset = row.get('asset_id', '').strip()
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
        reader = csv.DictReader(stream)
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
    escape = lambda value: html.escape(str(value), quote=True)
    findings = ''.join('<tr>' + ''.join(f'<td>{escape(f[k])}</td>' for k in ['line', 'asset_id', 'message']) + '</tr>' for f in report['findings'])
    systems = ''.join(f'<li>{escape(os)} : {count}</li>' for os, count in report['os_distribution'].items())
    return f'''<!doctype html><html lang="fr"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>CIEL Asset Audit</title><style>body{{font:16px system-ui;background:#f3f6fa;color:#18384a;max-width:1000px;margin:50px auto;padding:24px}}h1{{font-size:42px}}section{{background:white;padding:24px;border-radius:14px;margin:24px 0;overflow:auto}}table{{border-collapse:collapse;width:100%}}td,th{{text-align:left;padding:14px;border-bottom:1px solid #dde5ee}}small{{color:#62788a}}</style><small>CIEL / INVENTAIRE INFORMATIQUE</small><h1>État de l’inventaire.</h1><p>{report['assets']} équipements · {len(report['findings'])} observations</p><section><h2>Répartition des systèmes</h2><ul>{systems}</ul></section><section><h2>Points à vérifier</h2><table><tr><th>Ligne CSV</th><th>Équipement</th><th>Observation</th></tr>{findings}</table>{'<p>Aucune anomalie détectée par ces règles.</p>' if not findings else ''}</section><small>Contrôle de qualité des données et seuil RAM configurable. Aucun scan réseau ni diagnostic de sécurité.</small></html>'''


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
