#!/usr/bin/env bash


filter_order=8

CSV_FILES=*.csv
rm -f error_files.txt

for f in $CSV_FILES 
do

 	echo "Processing file: " 
 	echo $f


# ./analyze_muse_data.py -hdf5 -db -f -ft 1  -hc 20 -lc 5 -o 8 -v 3 -c /Users/dperi/Documents/Muse_Dev/analyze_eeg/data-for-testing.csv

 	analyze_meditation_data.py -f -lc 1. -hc 70.0 -o $filter_order -p -e -l 2 -c $f
# 	analyze_meditation_data.py -f -lc 1. -hc 70.0 -o $filter_order -p -e -l 2 -i -s 4 -c $f

	case {$?} in
		0) 
		# true # ok
		;;
	 
		*) 
		# false # something went wrong
		echo $f >>  error_files.txt
		
	esac 

done

