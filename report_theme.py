"""Shared visual primitives for standalone reports; no external assets."""
from html import escape
STYLE = '''*{box-sizing:border-box}body{margin:0;font:14px system-ui,sans-serif;color:#23394b;background:#f1f4f8}.wrap{max-width:1150px;margin:auto;padding:32px}.brand{font-size:12px;letter-spacing:2px;font-weight:800;color:#557887;display:flex;justify-content:space-between;border-bottom:1px solid #d7e0e9;padding-bottom:22px}.hero{background:#112b3e;color:white;border-radius:16px;padding:42px;margin:30px 0}.hero small{color:#a0ddcc;font-size:10px;letter-spacing:2px}.hero h1{font-size:44px;line-height:1.08;letter-spacing:-1.5px;margin:18px 0}.hero p{color:#b2c7d6;line-height:1.8}.metrics{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin-bottom:24px}.metric{background:white;border:1px solid #dfe7ee;border-radius:12px;padding:24px}.metric small{color:#718697}.metric strong{display:block;font-size:35px;letter-spacing:-1px;margin-top:12px}.metric:nth-child(2) strong{color:#147864}.metric:nth-child(3) strong{color:#a75529}.grid{display:grid;grid-template-columns:1fr 1fr;gap:20px}.panel{background:white;border:1px solid #dfe7ee;padding:25px;border-radius:12px;margin-bottom:22px;min-width:0;overflow:auto}h2{font-size:17px;margin:0 0 18px}.table-wrap{overflow:auto}table{border-collapse:collapse;width:100%;text-align:left;font-size:12px}th{font-size:10px;color:#687f91;text-transform:uppercase;letter-spacing:.8px;background:#f5f8fa}td,th{padding:14px 12px;border-bottom:1px solid #e6ecf2}td{overflow-wrap:anywhere}td:first-child{font-weight:600}.note{font-size:12px;line-height:1.8;color:#6a8292}.bar-row{display:grid;grid-template-columns:minmax(90px,1fr) 2fr 40px;gap:14px;align-items:center;font-size:12px;margin:16px 0}.track{height:9px;border-radius:8px;background:#edf3f6;overflow:hidden}.fill{height:100%;background:#439f8c;border-radius:8px}.count{text-align:right;color:#6f8697}footer{font-size:10px;color:#6b8193;border-top:1px solid #d7e0e9;padding:25px 0;margin-top:20px}.tag{background:#e5f3ed;color:#287b65;padding:6px 10px;border-radius:20px;font-size:10px}@media(max-width:650px){.wrap{padding:18px}.hero{padding:27px}.hero h1{font-size:34px}.metrics{gap:10px;grid-template-columns:1fr}.metric{display:flex;justify-content:space-between;align-items:center}.metric strong{margin:0;font-size:28px}.grid{grid-template-columns:1fr}.panel{padding:18px}.brand{font-size:10px;gap:15px}.bar-row{gap:9px;font-size:11px}.hero p{font-size:12px}}@media print{body{background:white}.hero{background:#edf3f8;color:#122d40}.hero p{color:#486479}.panel,.metric{break-inside:avoid}}
/* 2026-11 cross-device reports: keep charts readable and tables inside panels. */
:where(.wrap,.grid,.panel,.metric){min-width:0}
.table-wrap{max-width:100%;overflow-x:auto;overscroll-behavior-x:contain;-webkit-overflow-scrolling:touch}
@media(max-width:820px){.grid{grid-template-columns:minmax(0,1fr)}}
@media(max-width:520px){
 .wrap{padding:14px}
 .brand{flex-wrap:wrap;align-items:center;gap:8px;line-height:1.5}
 .hero{padding:26px 19px;margin:18px 0}
 .hero h1{font-size:clamp(27px,8vw,36px);overflow-wrap:anywhere}
 .metric{gap:12px;min-width:0;padding:18px}
 .metric strong{font-size:clamp(19px,7vw,28px);overflow-wrap:anywhere;text-align:right}
 .bar-row{grid-template-columns:minmax(64px,1fr) minmax(50px,1.5fr) 28px;gap:7px}
 .bar-row>span:first-child{min-width:0;overflow-wrap:anywhere}
 .panel{padding:16px}
 .table-wrap table{min-width:500px}
 td,th{padding:11px 9px}
}
'''

def table(headers, rows):
    head = ''.join(f'<th scope="col">{escape(str(x))}</th>' for x in headers)
    body = ''.join('<tr>' + ''.join(f'<td>{escape(str(x))}</td>' for x in row) + '</tr>' for row in rows)
    return f'<div class="table-wrap"><table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>'

def bars(items):
    items = list(items)
    max_value = max((value for _, value in items), default=1) or 1
    return ''.join(f'<div class="bar-row"><span>{escape(str(label))}</span><div class="track"><div class="fill" style="width:{100*value/max_value:.2f}%"></div></div><span class="count">{value}</span></div>' for label, value in items)

def page(title, subtitle, metrics, body, label):
    cards = ''.join(f'<div class="metric"><small>{escape(str(name))}</small><strong>{escape(str(value))}</strong></div>' for name, value in metrics)
    return f'<!doctype html><html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{escape(title)}</title><style>{STYLE}</style></head><body><main class="wrap"><header class="brand"><span>◇ CIEL / {escape(label)}</span><span>RAPPORT LOCAL</span></header><section class="hero"><small>OBSERVER · COMPRENDRE · DOCUMENTER</small><h1>{escape(title)}</h1><p>{escape(subtitle)}</p></section><section class="metrics" aria-label="Indicateurs">{cards}</section>{body}<footer>Mehdi Hmaiss · Projet pédagogique avec assistance IA · Rapport autonome, sans service externe</footer></main></body></html>'
