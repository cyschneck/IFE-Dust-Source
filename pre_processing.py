########################################################################################################################################
# Dust and IFE interactions
# Objective: PRE-PROCESSING OF SMALL BODIES DATABASE DATA TYPES FOR FUTURE IDENTIFICATION
# Date Started: March 2019
########################################################################################################################################
import os
from datetime import datetime
from datetime import datetime
from dateutil.relativedelta import relativedelta
import csv
import requests
from subprocess import check_output
import progressbar as pb

## GET DATE RANGE FROM DATA CSV
def dateRange(date_range_file):
	# date range from file and returns a list of date ranges increments 
	# Returns list of date ranges (incremented one day): [['04/01/2011', '04/02/2011'], ['12/31/2011', '01/01/2012']]
	date_range_lst = []
	with open(date_range_file) as csv_file:
		csv_reader = csv.reader(csv_file, delimiter=',')
		row_num = 0
		for row in csv_reader:
			if row[0] != '': # ignore empty rows
				row_num += 1
				if row_num == 2 and row[0] == 'Date': # row for date values
					for start_date in row[1:]:
						start_date = datetime.strptime(start_date,"%m/%d/%Y")
						end_date = start_date + relativedelta(days=1) # increment date counter by one day
						date_range_lst.append([start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')])
	#date_range_lst = [['1983-06-19', '1983-06-21']] # oljato example
	return date_range_lst

## API CALLS FOR NEO
def neoApiByDate(api_key, start_date, end_date, to_print):
	# api call: Retrieve a list of Asteroids based on their closest approach date to Earth
	# Parameters: Starting date for asteroid search (YYYY-MM-DD), Ending date for asteroid search (YYYY-MM-DD)
	''' Returns: Date, is_sentry_object, links, nasa_jpl_url, absolute_magnitude_h,
		estimated_diameter (max, min): feet, miles, meters, kilometers,
		close_approach_data (list of all approaches): miss distance (astronmical, miles, lunar, kilometers),
		orbiting_body (i.e. Earth, Venus, etc...),
		epoch_date_close_approach, close_approach_date, relative_velocity (km/s, mph, km/hr),
		neo-reference_id, is_potentially_hazardous_asteriod, id, name
	'''
	http_link_by_date = "https://api.nasa.gov/neo/rest/v1/feed?start_date={0}&end_date={1}&api_key={2}".format(start_date, end_date, api_key)
	api_data = requests.get(http_link_by_date)
	if to_print: print("Date Range: {0} - {1}".format(start_date, end_date))
	if to_print: print("status code by date = {0}".format(api_data.status_code))

	if api_data.status_code != 200:
		# 401 (Unauthorized), 402 (Forbidden), 403 (Forbidden), 404 (Not Found)
		print("API REQUEST NOT FOUND, exiting...")
		exit()

	start_limit = int(IsApiLimitReached(api_data, 1, to_print)) # x limit = 1000/hr (check that isn't reached)
	if api_data.status_code == 200:
		#print("api data encoding: {0}".format(api_data.encoding))
		api_neo_lst = api_data.json()["near_earth_objects"]

		# check how many calls to be made before making calls
		total_calls_to_make = 0 # total api calls to make (check that it doesn't exceeded allowed)
		for date, neo_found in api_neo_lst.iteritems():
			total_calls_to_make += len(neo_found)
		if to_print: print("Total api calls to make = {0}".format(total_calls_to_make))
		IsApiLimitReached(api_data, total_calls_to_make, to_print)

		neo_data_by_id = {}
		for date, neo_data_lst in api_neo_lst.iteritems():
			if to_print: print(date)
			for neo_data_dict in neo_data_lst:
				neo_data_by_id[neo_data_dict['neo_reference_id']] = neoApiByID(api_key, neo_data_dict['neo_reference_id'])

	if to_print: print("API LIMIT REMAINING: {0}".format(start_limit - total_calls_to_make)) # print api calls remaining at the end for reference
	return neo_data_by_id

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
	#if to_print: print("status code by id = {0}".format(api_data.status_code))

	if api_data.status_code != 200:
		# 401 (Unauthorized), 402 (Forbidden), 404 (Not Found)
		print("API REQUEST NOT FOUND, exiting...")
		exit()

	if api_data.status_code == 200:
		if to_print: print("\tNEO BY ID = {0}".format(asteriod_id))
		neo_id_dict = api_data.json()
		#if to_print:
		#	for k, v in neo_id_dict.iteritems():
		#		print(k)
		#		print(v)
		#		print("\n")
	return neo_id_dict

## TRACK API USAGE
def IsApiLimitReached(api_data, api_call_request_cnt, to_print):
	# check that api limit isn't reached before attempting
	# NASA API X-Ratelimit 100 api calls per hour (on a rolling basis when an hour has passed since the call was made)
	api_calls_remaining = int(api_data.headers['X-RateLimit-Remaining'])
	#print("{0} < {1} = {2}".format(api_calls_remaining, api_call_request_cnt, api_calls_remaining < api_call_request_cnt))

	if api_calls_remaining < api_call_request_cnt:
		print("API LIMIT REACHED, Cannot make {0} calls. Wait an hour to allow limit to fully reset".format(api_call_request_cnt))
		exit()
	if to_print: print("API CALLS REMAINING: {0}".format(api_calls_remaining))
	return api_calls_remaining

## CONVERT TO J200 (ECI Frame)
def convertToGSE():
	# Convert orbital dynamics for small bodies into GSE
	# Strip position vectors from cdaweb for ACE and Horizon for Small Bodies
	# Compare with the position of low-Earth orbit satellites detecting IFEs
	return None

## SAVE DATA TO CSV
def saveNEOData(api_asteriod_id_dict, start_date, end_date):
	# save data from api call to csv"
	csv_filename = 'neo_asteriod_features_from_{0}_to_{1}.csv'.format(start_date.replace('-', '_'), end_date.replace('-', '_'))
	with open("{0}/{1}".format("csv_neo_features", csv_filename), mode='w') as csv_file:
		api_fields = ["Name",
						"neo_reference_id",
						"Eccentricity",
						"Semi-Major Axis",
						"Inclination",
						"Perihelion Argument",
						"Perihelion Time",
						"Perihelion Distance",
						"Alphelion Distance",
						'Close-Approach Date',
						'Nominal Miss Distance (AU)',
						'GSE (AU)',
						'Orbiting Body for Close-Approach',
						]

		writer = csv.DictWriter(csv_file, fieldnames=api_fields)
		writer.writeheader()

		for asteriod_id, asteriod_data_dict in api_asteriod_id_dict.iteritems():
			for neo_close_approach_event in asteriod_data_dict['close_approach_data']:
				if float(neo_close_approach_event["miss_distance"]["astronomical"]) <= 0.1: # filter on neo approaches for Nominal Miss Distance <= 1/10 (0.1) AU
					if neo_close_approach_event["orbiting_body"] == "Earth": # filter on neo approaches for Earth
						writer.writerow({'Name': asteriod_data_dict['name'],
										'neo_reference_id': asteriod_data_dict['id'],
										'Eccentricity': asteriod_data_dict['orbital_data']['eccentricity'],
										'Semi-Major Axis': asteriod_data_dict['orbital_data']['semi_major_axis'],
										'Inclination': asteriod_data_dict['orbital_data']['inclination'],
										'Perihelion Argument': asteriod_data_dict['orbital_data']['perihelion_argument'],
										'Perihelion Distance': asteriod_data_dict['orbital_data']['perihelion_distance'],
										'Perihelion Time': asteriod_data_dict['orbital_data']['perihelion_time'],
										'Alphelion Distance': asteriod_data_dict['orbital_data']['aphelion_distance'],
										'Close-Approach Date': neo_close_approach_event["close_approach_date"],
										'Nominal Miss Distance (AU)': neo_close_approach_event["miss_distance"]["astronomical"],
										'GSE (AU)': convertToGSE(), #TODO
										'Orbiting Body for Close-Approach': neo_close_approach_event["orbiting_body"],
										})

	print("\nSAVED: {0}".format(csv_filename))

if __name__ == '__main__':
	start_time = datetime.now()

	import argparse
	# file run: python pre_processing.py -A DEMO_KEY -P True -D ACE_IFEs_example.csv
	parser = argparse.ArgumentParser(description="flag format given as: -A <api_key>")
	parser.add_argument('-A', '-api-key', help="api key for dataset")
	parser.add_argument('-P', '-verbose_sentences', choices=("True", "False"), default="False", help="print sentences")
	parser.add_argument('-D', '-date-file', help="file of dates")
	args = parser.parse_args()

	if args.A is None:
		print("ERROR: Include api key to read\n")
		exit()
	else:
		api_key = args.A

	# get range of dates from file to run and produce multiple files
	if args.D is None:
		print("ERROR: Include date file for date ranges\n")
		exit()
	else:
		date_range_file = args.D

	# argument to print details for the command prompt
	to_print = args.P
	to_print = True if args.P == 'True' else False # cast as true/false from input string

	# creating directories if they do not already exist
	if to_print:
		if not os.path.isdir('csv_neo_features'):
			print("creating csv_neo_features directory")
			os.makedirs('csv_neo_features')

	if to_print: print("\n")

	# run API calls for each date range in file (with progress bar)
	date_range = dateRange(date_range_file)

	widgets = ['API Calls for Dates: ', pb.Percentage(), ' ',
				pb.Bar(marker=pb.RotatingMarker()), ' ', pb.ETA()]

	timer = pb.ProgressBar(widgets=widgets, maxval=len(date_range)).start()
	for i in range(len(date_range)):
		timer.update(i)
		start_date = date_range[i][0]
		end_date = date_range[i][1]
		asteriod_id_data_dict = neoApiByDate(api_key, start_date, end_date, to_print) # returns the neo by id
		saveNEOData(asteriod_id_data_dict, start_date, end_date) # save neo asteriod data to csv
	timer.finish()

	print("\nran for for {0}\n".format(datetime.now() - start_time))
