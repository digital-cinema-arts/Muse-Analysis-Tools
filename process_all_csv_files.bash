#!/usr/bin/env bash


filter_order=3
low_cut=0.5
high_cut=70.0

CSV_FILES=*.csv
rm -f error_files.txt

for f in $CSV_FILES 
do

 	echo "Processing file: " 
 	echo $f

# ./analyze_muse_data.py -hdf5 -db -fd -ft 1  -hc 20 -lc 5 -o 8 -v 3 -c /Users/dperi/Documents/Muse_Dev/analyze_eeg/data-for-testing.csv
	
	# Analyze and plot: save hdf5 file, filter with type 1, create coherence plots, send data to database
	analyze_muse_data.py -hdf5 -db -fd -ft 1 -hc $high_cut -lc $low_cut -o $filter_order -v 3 -c 

	case {$?} in
		0) 
		# true # ok
		;;
	 
		*) 
		# false # something went wrong
		echo $f >>  error_files.txt
		
	esac 

done

