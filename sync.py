"""Sync Grist doc from API

Usage:
	sync.py
	sync.py [-e ENV] [-w|--write]
	sync.py -h|--help
	sync.py -v|--version

Options:
	-h --help           Show this screen
	-v --version        Show version
	-e ENV --env=ENV  	Use given file for sync configuration [default: .env]
	-w --write          Sync outdated data
"""

# coding: utf-8
from docopt import docopt
from GristAPI import GristAPI
from BetaGouvAPI import BetaGouvAPI
from deepdiff import DeepDiff
from pprint import pprint
import logging
import re
import pdb

class SyncApi:

	def __init__(self, env):
		print("🔃 Init")

		# Configurer le logger principal
		logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

		# Créer un logger spécifique pour le module principal
		self.logger = logging.getLogger('sync')

		# Load GRIST data
		self.grist = GristAPI(env)
		self.grist_data = self.grist.all()

		# Load API data
		self.api = BetaGouvAPI(env)
		# Dictionnary (id => dict)
		self.api_data = self.api.all()


	def showDiff(self, write):
		added, removed, updated = self._compareDict(self.api_data, self.grist_data)

		print("\n🆕 New lines:")
		print("👉 {count} new lines".format(count=len(added)))
		print(added)
		if(write):
			if(len(added) > 0):
				for id in added:
					self.grist.create(id, data=self.api.get(id))
				print("✅ {count} new lines".format(count=len(added)))

		print("\n🆕 Updated lines:")
		print("👉 {count} modified lines".format(count=len(updated)))
		print(updated)
		if(write):
			if(len(updated) > 0):
				for id in updated:
					self.grist.update(id, data=self.api.get(id))
				print("✅ {count} modified lines".format(count=len(updated)))

		print("\n🆕 Removed lines:")
		print("👉 {count} removed lines".format(count=len(removed)))
		print(removed)



	def _compareDict(self, d1, d2):
		d1_keys = set(d1.keys())
		d2_keys = set(d2.keys())
		added = d1_keys - d2_keys
		removed = d2_keys - d1_keys

		updated = set()
		shared_records = d1_keys.intersection(d2_keys)
		# Compare dict content
		for record_id in shared_records:
			r1 = d1[record_id]
			r2 = d2[record_id]

			for key in r1:
				# TODO avoid hard coded exception
				if key in ["incubator_id", "incubator", "contact"]:
					continue
				if key not in r2.keys() or r1[key] != r2[key]:
					self.logger.debug("{record} updated - {key}: {old_value} > {new_value}".format(record=record_id, key=key, old_value=r1[key], new_value=r2[key]))
					updated.add(record_id)
					break

		return added, removed, updated


if __name__ == '__main__':
	arguments = docopt(__doc__, version='1.0')
	env = arguments['ENV'] or ".env"
	write = arguments['-w'] or arguments['--write']

	sync = SyncApi(env)

	sync.showDiff(write)

