# CIEL Asset Audit

[**Voir le rapport de démonstration · données fictives**](https://itztov4r.github.io/ciel-asset-audit/)

**Contrôler la qualité d’un inventaire informatique CSV et générer un rapport HTML lisible.**

Projet Python pédagogique pour le Bac pro CIEL, sans dépendance externe. Toutes les données de démonstration sont fictives.

## Démarrage

Python 3.10 ou plus récent.

```bash
python audit.py examples/inventory.csv --output report.html --json report.json
```

Ouvrez `report.html` dans votre navigateur. Un rapport d’exemple est déjà disponible dans [`examples/report.html`](examples/report.html).

```bash
python audit.py examples/inventory.csv --min-ram 16 --fail-on-findings
python -m unittest discover -s tests -v
```

Sous Windows, `py` peut remplacer `python`.

## Règles de contrôle

| Contrôle | Résultat |
| --- | --- |
| Colonne obligatoire absente / ligne mal formée | Erreur explicite, code de sortie 2 |
| Champ obligatoire vide | Observation avec numéro de ligne CSV |
| Identifiant matériel ou adresse IP en doublon | Observation |
| Adresse IPv4 / IPv6 invalide | Observation |
| RAM non entière, non positive ou sous le seuil | Observation |

Les adresses IPv6 sont normalisées avant la comparaison. Les valeurs CSV sont échappées dans le HTML. Les sorties ne peuvent pas écraser le fichier d’entrée. Le seuil RAM par défaut est 8 Go : c’est un choix pédagogique configurable, pas une exigence universelle.

## Format d’entrée

CSV UTF-8 (BOM accepté), séparateur virgule, avec les colonnes :

```csv
asset_id,hostname,ip_address,os,ram_gb,location
PC-001,accueil,192.0.2.10,Windows 11,16,Accueil
```

Colonnes supplémentaires acceptées. Sans `--fail-on-findings`, un rapport avec observations retourne 0. Avec cette option : 1 si observations, 0 sinon. Les erreurs d’entrée/sortie retournent 2.

## Structure et validation

- `audit.py` : lecture CSV, règles, génération HTML et interface CLI.
- `examples/` : inventaire et rapports reproductibles (4 équipements, 5 observations).
- `tests/test_audit.py` : 7 tests couvrant doublons, IPv6, données invalides, seuil, HTML, CSV et inventaire vide.
- `.github/workflows/tests.yml` : exécution des tests sur GitHub Actions.

## Ce que ce projet permet de présenter

Manipulation de fichiers, validation des données, fonctions Python, exceptions, arguments CLI, rapports et tests unitaires. Pour l’entretien : ajouter une règle de contrôle, modifier le seuil et expliquer les codes de sortie.

## Limites et évolutions

Cet outil analyse uniquement le contenu fourni dans le CSV. Il ne découvre aucun appareil et ne vérifie ni le réseau, ni les mises à jour, ni les vulnérabilités. Évolutions possibles : prise en charge des CSV à point-virgule, inventaire SQLite et comparaison de deux inventaires.

Projet préparé pour le portfolio de **Mehdi Hmaiss**, avec assistance IA pour le code, la documentation et les tests. Projet d’apprentissage, sans revendication d’utilisation en entreprise.

Licence MIT — voir [LICENSE](LICENSE).

Le rapport utilise un thème responsive embarqué dans `report_theme.py` ; `index.html` présente uniquement les données fictives de l’exemple.
