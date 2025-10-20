from grist_api import GristDocAPI
import os
from os.path import join, dirname
from dotenv import load_dotenv
import yaml
import logging

# API Reference : https://py-grist-api.readthedocs.io/en/latest/grist_api.html
# Sur Github https://github.com/gristlabs/py_grist_api
class GristAPI:

    def __init__(self, env):
        # Configurer le logger principal
        logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        # Créer un logger spécifique pour le module principal
        logger = logging.getLogger('main')
        logger.info("Démarrage de l'application")

        self.__get_env(env)
        self.api = GristDocAPI(self.base, server=self.server)
        self.records = {}

    def __get_env(self, file):
        path = join(dirname(__file__), file)
        if not os.path.exists(path):
            print("❌ Error: cannot find {path} file.".format(path=path))
            quit()

        # Récupérer les variables d'environnement
        # This should be read from .yml file ?
        load_dotenv(path)
        for param in ['GRIST_DOC_ID', 'GRIST_SERVER', 'GRIST_TABLE']:
            if not os.getenv(param):
                print("❌ Error: {param} missing in {file}.".format(param=param, file=file))
                quit()

        self.base = os.getenv('GRIST_DOC_ID')
        self.server = os.getenv('GRIST_SERVER')
        self.table = os.getenv('GRIST_TABLE')

        # TODO : this should probably be done in sync.py
        mapping_file = os.getenv("MAPPING_FILE")
        if mapping_file:
            conf = yaml.safe_load(open(mapping_file))
            self.mapping = conf["grist"]
        else:
            print("❌ Error: MAPPING_FILE missing in {file}.".format(file=file))


    def all(self):
        # Fetch data from Grist
        records = self.api.fetch_table(self.table)

        # Load result in a nice dict
        for r in records:
            d = dict()
            d["grist_id"] = r.id
            for(key) in self.mapping:
                grist_key = self.mapping[key]
                d[key] = getattr(r, grist_key) # I don't like this but r.key doesn't work since key is a string
            r_id = getattr(r, self.mapping["id"])
            self.records[r_id] = d

        return self.records

    def get(self, id):
        return self.records.get(id)

    def create(self, id, data):
        d = self._convertDataToGristDict(data)

        try:
            self.api.add_records(self.table, [d])
        except Exception as err:
            print("❌ Error: cannot add records {id}:".format(id=id))
            print(type(err))
            print(err.args)

    def update(self, id, data):
        d = self._convertDataToGristDict(id, data)

        try:
            # update_records(table_name, record_dicts, group_if_needed=False, chunk_size=None)
            self.api.update_records(self.table, [d])
        except Exception as err:
            print("❌ Error: cannot update record {id}:".format(id=id))
            print(type(err))
            print(err.args)

    def _convertDataToGristDict(self, id, data):
        grist_data = self.get(id)
        d = {'id': grist_data["grist_id"]}
        for key, grist_key in self.mapping.items():
            d[grist_key] = data[key]

        return d