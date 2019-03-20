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
	''' Returns: Date, is_sentry_object, links, nasa_jpl_url, absolute_magnitude_h, 
		estimated_diameter (max, min): feet, miles, meters, kilometers,
		close_approach_data (list): miss distance (astronmical, miles, lunar, kilometers),
		orbiting_body (i.e. Earth, Venus, etc...),
		epoch_date_close_approach, close_approach_date, relative_velocity (km/s, mph, km/hr),
		neo-reference_id, is_potentially_hazardous_asteriod, id, name
	'''
	http_link_by_date = "https://api.nasa.gov/neo/rest/v1/feed?start_date=2015-09-07&end_date=2015-09-07&api_key={0}".format(api_key)
	api_data = requests.get(http_link_by_date)
	print("status code = {0}".format(api_data.status_code))

	if api_data.status_code != 200:
		# 401 (Unauthorized), 402 (Forbidden), 404 (Not Found)
		print("not found")

	if api_data.status_code == 200:
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
				neoApiByID(api_key, neo_data_dict['neo_reference_id'])
			print("\n")

def neoApiByID(api_key, asteriod_id):
	# api call: Lookup a specific Asteroid based on its NASA JPL small body (SPK-ID) ID
	# Parameters: Asteroid (str)
	'''Returns: designation, nasa_jpl_url, links, neo_reference_id, is_potentially_hazardous_asteriod,
	is_sentry_object, id, name,
	orbital_data: last_observation_date, equinox, first_observation_date, orbit_uncertainty, alphelion_distance,
		data_arc_in_days, orbit_class (orbit_class_type, orbit_class_description, orbit_class_range),
		mean_anomaly, orbital_period, ascending_node_longitude, orbit_id, inclination, observations_used,
		epoch_osculation, mean_motion, jupiter_tisserand_invariant, orbit_determination_date, perihelion_time,
		eccentricity, perihelion_argument, minimum_orbit_intersection, semi_major_axis, perihelion_distance
	estimated_diameter (max, min): feet, miles, meters, kilometers,
	close_approach_data (list): miss distance (astronmical, miles, lunar, kilometers),
	'''
	http_link_by_id = "https://api.nasa.gov/neo/rest/v1/neo/{0}?api_key={1}".format(asteriod_id, api_key)
	api_data = requests.get(http_link_by_id)
	print("status code = {0}".format(api_data.status_code))

	if api_data.status_code != 200:
		# 401 (Unauthorized), 402 (Forbidden), 404 (Not Found)
		print("not found")

	if api_data.status_code == 200:
		print("api data encoding: {0}".format(api_data.encoding))
		print("NEO BY ID")
		neo_id_dict = api_data.json()
		for k, v in neo_id_dict.iteritems():
			print(k)
			print(v)
			print("\n")

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
