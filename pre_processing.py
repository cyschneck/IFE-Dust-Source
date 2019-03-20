###########################################################################
# Dust and IFE interactions

# Date: March 2019
###########################################################################
import os
from datetime import datetime
import csv
import requests

## SAVE ASTERIOD TO CSV
def neoApiBrowseAll(api_key):
	# api call: Retieve a paginated list of Near Earth Objects
	# Parameters: Page (int) and Query Size (int)
	http_link = "https://api.nasa.gov/neo/rest/v1/neo/browse?api_key={0}".format(api_key)
	api_data = requests.get(http_link)
	print("status code = {0}".format(api_data.status_code))
	if api_data.status_code == 200:
		print("found")
		print(api_data.content)
	if api_data.status_code != 200:
		# 401 (Unauthorized), 402 (Forbidden), 404 (Not Found)
		print("not found")

def saveNEOData(api_data):
	# save data from api call to csv"
	csv_filename = 'neo_asteriod_api.csv'
	with open(csv_filename, mode='w') as csv_file:
		api_fields = ["neo_reference_id",
						"name",
						"designation",
						"absolute_magnitude_h",
						"estimated_diameter km (max)",
						"estimated_diameter km (min)",
						"orbiting_body"]
						
		writer = csv.DictWriter(csv_file, fieldnames=api_fields)
		writer.writeheader()

	print("\nSAVED: {0}".format(csv_filename))
	return csv_filename

if __name__ == '__main__':
	start_time = datetime.now()

	import argparse
	# file run: 
	parser = argparse.ArgumentParser(description="flag format given as: -F <tsv_file>")
	parser.add_argument('-A', '-api-key', help="api key for dataset")
	parser.add_argument('-P', '-verbose_sentences', choices=("True", "False"), default="False", help="print sentences")
	args = parser.parse_args()
	if args.A is None:
		print("ERROR: Include api key to read\n")
		exit()
	else:
		api_key = args.A

	to_print = args.P
	to_print = True if args.P == 'True' else False # cast as true/false from input string

	# creating directories if they do not already exist
	if not os.path.isdir('csv_features'):
		print("creating csv_features directory")
		os.makedirs('csv_features')

	# error condition: https://ssd.jpl.nasa.gov/sbdb.cgi?sstr=433%eros

	print("\n")
	neoApiBrowseAll(api_key)
	saveNEOData("")

	print("\nran for for {0}\n".format(datetime.now() - start_time))
