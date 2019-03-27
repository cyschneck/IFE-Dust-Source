########################################################################################################################################
# Dust and IFE interactions
# Objective: PRE-PROCESSING OF SMALL BODIES DATABASE DATA TYPES FOR FUTURE IDENTIFICATION
# Date: March 2019
########################################################################################################################################
import os
from datetime import datetime
import csv
import requests

## API CALLS FOR NEO
def neoApiByDate(api_key):
	# api call: Retrieve a list of Asteroids based on their closest approach date to Earth.
	# Parameters: Starting date for asteroid search (YYYY-MM-DD), Ending date for asteroid search (YYYY-MM-DD)
	''' Returns: Date, is_sentry_object, links, nasa_jpl_url, absolute_magnitude_h, 
		estimated_diameter (max, min): feet, miles, meters, kilometers,
		close_approach_data (list of all approaches): miss distance (astronmical, miles, lunar, kilometers),
		orbiting_body (i.e. Earth, Venus, etc...),
		epoch_date_close_approach, close_approach_date, relative_velocity (km/s, mph, km/hr),
		neo-reference_id, is_potentially_hazardous_asteriod, id, name
	'''
	http_link_by_date = "https://api.nasa.gov/neo/rest/v1/feed?start_date=2018-08-09&end_date=2018-08-09&api_key={0}".format(api_key)
	api_data = requests.get(http_link_by_date)
	print("status code by date = {0}".format(api_data.status_code))

	if api_data.status_code != 200:
		# 401 (Unauthorized), 402 (Forbidden), 403 (Forbidden), 404 (Not Found)
		print("API REQUEST NOT FOUND, exiting...")
		exit()

	start_limit = int(IsApiLimitReached(api_data, 1)) # x limit = 1000/hr (check that isn't reached)
	if api_data.status_code == 200:
		#print("api data encoding: {0}".format(api_data.encoding))
		api_neo_lst = api_data.json()["near_earth_objects"]

		# check how many calls to be made before making calls
		total_calls_to_make = 0 # total api calls to make (check that it doesn't exceeded allowed)
		for date, neo_found in api_neo_lst.iteritems():
			total_calls_to_make += len(neo_found)
		print("Total api calls to make = {0}".format(total_calls_to_make))
		IsApiLimitReached(api_data, total_calls_to_make)

		for date, neo_data_lst in api_neo_lst.iteritems():
			for neo_data_dict in neo_data_lst:
				#print("NEW OBJECT")
				#for k, v in neo_data_dict.iteritems():
				#	print(k)
				#	print("\t{0}".format(v))
				#	print("\n")
				neoApiByID(api_key, neo_data_dict['neo_reference_id'])
			print("\n")
			pass

	print("API LIMIT REMAINING: {0}".format(start_limit - total_calls_to_make)) # print api calls remaining at the end for reference

def neoApiByID(api_key, asteriod_id):
	# api call: Lookup a specific Asteroid based on its NASA JPL small body (SPK-ID) ID
	# Parameters: Asteroid ID (str)
	'''Returns: designation, nasa_jpl_url, links, neo_reference_id, is_potentially_hazardous_asteriod,
	is_sentry_object, id, name,
	orbital_data: last_observation_date, equinox, first_observation_date, orbit_uncertainty, alphelion_distance,
		data_arc_in_days, orbit_class (orbit_class_type, orbit_class_description, orbit_class_range),
		mean_anomaly, orbital_period, ascending_node_longitude, orbit_id, inclination, observations_used,
		epoch_osculation, mean_motion, jupiter_tisserand_invariant, orbit_determination_date, perihelion_time,
		eccentricity, perihelion_argument, minimum_orbit_intersection, semi_major_axis, perihelion_distance
	estimated_diameter (max, min): feet, miles, meters, kilometers,
	close_approach_data (list of all approaches): miss distance (astronmical, miles, lunar, kilometers),
	'''
	http_link_by_id = "https://api.nasa.gov/neo/rest/v1/neo/{0}?api_key={1}".format(asteriod_id, api_key)
	api_data = requests.get(http_link_by_id)
	#print("status code by id = {0}".format(api_data.status_code))

	if api_data.status_code != 200:
		# 401 (Unauthorized), 402 (Forbidden), 404 (Not Found)
		print("API REQUEST NOT FOUND, exiting...")
		exit()

	if api_data.status_code == 200:
		print("\tNEO BY ID")
		neo_id_dict = api_data.json()
		#for k, v in neo_id_dict.iteritems():
		#	print(k)
		#	print(v)
		#	print("\n")

## SAVE DATA TO CSV
def saveNEOData(api_data):
	# save data from api call to csv"
	#eccentricity, Semi-major axis, inclination,  perihelion argument, perihelion time
	csv_filename = 'neo_asteriod_features.csv'
	with open(csv_filename, mode='w') as csv_file:
		api_fields = ["name",
						"neo_reference_id",
						"designation",
						"eccentricity",
						"Semi-major axis",
						"inclination",
						"perihelion argument",
						"perihelion time"]
		writer = csv.DictWriter(csv_file, fieldnames=api_fields)
		writer.writeheader()

	print("\nSAVED: {0}".format(csv_filename))
	return csv_filename

## TRACK API USAGE
def IsApiLimitReached(api_data, api_call_request_cnt):
	# check that api limit isn't reached before attempting
	# NASA API X-Ratelimit 100 api calls per hour (on a rolling basis when an hour has passed since the call was made)
	api_calls_remaining = int(api_data.headers['X-RateLimit-Remaining'])
	#print("{0} < {1} = {2}".format(api_calls_remaining, api_call_request_cnt, api_calls_remaining < api_call_request_cnt))
	
	if api_calls_remaining < api_call_request_cnt:
		print("API LIMIT REACHED, Cannot make {0} calls. Wait an hour to allow limit to fully reset".format(api_call_request_cnt))
		exit()
	print("API CALLS REMAINING: {0}".format(api_calls_remaining))
	return api_calls_remaining

if __name__ == '__main__':
	start_time = datetime.now()

	import argparse
	# file run: python pre_processing.py -A DEMO_KEY
	parser = argparse.ArgumentParser(description="flag format given as: -A <api_key>")
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

	print("\n")
	neoApiByDate(api_key)
	saveNEOData("")

	# TODO: handle error condition: https://ssd.jpl.nasa.gov/sbdb.cgi?sstr=433%eros

	print("\nran for for {0}\n".format(datetime.now() - start_time))
