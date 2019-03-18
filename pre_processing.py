########################################################################################################################################
# Dust and IFE interactions
# Objective: PRE-PROCESSING OF SMALL BODIES DATABASE DATA TYPES FOR FUTURE IDENTIFICATION
# Date: March 2019
########################################################################################################################################
import os
from datetime import datetime

if __name__ == '__main__':
	start_time = datetime.now()

	import argparse
	# file run: 
	parser = argparse.ArgumentParser(description="flag format given as: -F <tsv_file>")
	parser.add_argument('-F', '-dust_file', help="dust file for pre-processing")
	parser.add_argument('-P', '-verbose_sentences', choices=("True", "False"), default="False", help="print sentences")
	args = parser.parse_args()
	if args.F is None:
		print("ERROR: Include a file to read\n")
		exit()
	else:
		dust_file = args.F

	to_print = args.P
	to_print = True if args.P == 'True' else False # cast as true/false from input string

	# creating directories if they do not already exist
	if not os.path.isdir('csv_features'):
		print("creating csv_features directory")
		os.makedirs('csv_features')

	print("File: {0}".format(dust_file))
	print("\nran for for {0}\n".format(datetime.now() - start_time))
