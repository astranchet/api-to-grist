import json
import requests
import os
from os.path import join, dirname
from dotenv import load_dotenv
import yaml

class BetaGouvAPI:

    def __init__(self, env):
        self.__get_env(env)
        # TODO : read from env file
        self.url = "https://beta.gouv.fr/api/v2.1/startups.json"
        self.incubators = {}
        self.startups = {}

    def __get_env(self, file):
        path = join(dirname(__file__), file)
        if not os.path.exists(path):
            print("❌ Error: cannot find {path} file.".format(path=path))
            quit()

        # Récupérer les variables d'environnement
        # TODO : this should probably be done in sync.py
        mapping_file = os.getenv("MAPPING_FILE")
        if mapping_file:
            conf = yaml.safe_load(open(mapping_file))
            self.mapping = conf["beta_gouv"]
        else:
            print("❌ Error: MAPPING_FILE missing in {file}.".format(file=file))


    def all(self):
        # Récupérer les données de l'API
        startups = json.loads(requests.get(self.url).text)

        self.incubators = {i.get('id'): i.get("attributes").get("title") for i in startups.get("included")}

        # Load result in a nice dict
        for se in startups.get('data'):

            # Read from mapping file
            d = dict()
            for(key) in self.mapping:
                beta_key = self.mapping[key]
                d[key] = se.get('attributes').get(beta_key)

            # Some column are a bit too specific to be configured in mapping file
            d["id"] = se.get("id")
            d["incubator_id"] = se.get('relationships').get('incubator').get('data').get('id')
            d["incubator"] = self.incubators.get(d["incubator_id"])
            d["phase"] = se.get('attributes').get('phases')[-1].get('name')
            self.startups[se.get("id")] = d

        return self.startups

    def get(self, id):
        return self.startups.get(id)