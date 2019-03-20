########################################################################################################################################
# Dust and IFE interactions
# Objective: PRE-PROCESSING OF SMALL BODIES DATABASE DATA TYPES FOR FUTURE IDENTIFICATION
# Date: March 2019
########################################################################################################################################
import os
from datetime import datetime
import csv
import requests

## SAVE ASTERIOD TO CSV
def neoApiByDate(api_key):
	# api call: Retieve a paginated list of Near Earth Objects
	# Parameters: Page (int) and Query Size (int)
	http_link_by_date = "https://api.nasa.gov/neo/rest/v1/feed?start_date=2015-09-07&end_date=2015-09-07&api_key={0}".format(api_key)
	api_data = requests.get(http_link_by_date)
	print("status code = {0}".format(api_data.status_code))

	if api_data.status_code != 200:
		# 401 (Unauthorized), 402 (Forbidden), 404 (Not Found)
		print("not found")

	if api_data.status_code == 200:
		print("found")
		print("api data encoding: {0}".format(api_data.encoding))
		api_neo_lst = api_data.json()["near_earth_objects"]
		for date, neo_data_lst in api_neo_lst.iteritems():
			print(date)
			for neo_data_dict in neo_data_lst:
				print("NEW OBJECT")
				for k, v in neo_data_dict.iteritems():
					print(k)
					print("\t{0}".format(v))
					print("\n")
			print("\n")

def neoApiByID(api_key, asteriod_id):
	# Lookup a specific Asteroid based on its NASA JPL small body (SPK-ID) ID
	# Parameters: Asteroid (str)
	http_link_by_id = "https://api.nasa.gov/neo/rest/v1/neo/{0}?api_key={1}".format(asteriod_id, api_key)

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
	neoApiByDate(api_key)
	saveNEOData("")

	print("\nran for for {0}\n".format(datetime.now() - start_time))
