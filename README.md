# Synchronisation d'une API vers Grist

## Mettre à jour les dépendances
```
pip3 install pipreqs
pipreqs . --force
```

ou bien

```
pip3 install dotenv
pip3 install deepdiff
pip3 install pprint
```

## Configurer le script

Créer un fichier `.env`
```
GRIST_DOC_ID=<identifiant du doc Grist>
GRIST_TABLE=<nom de la table>
GRIST_SERVER=https://grist.numerique.gouv.fr/
GRIST_API_KEY=<clé API>

MAPPING_FILE=mapping.yml
```

Et modifiez le fichier de mapping si besoin

## Lancer le programme

```
# Voir les changements entre API et Grist
python3 sync.py

# Mettre à jour le Grist depuis l'API
python3 startup.py -w

# Mettre à jour les SE avec un fichier d'environnement
python3 startup.py -w -e .myenv
```
