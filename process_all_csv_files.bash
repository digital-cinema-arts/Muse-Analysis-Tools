#!/usr/bin/env bash


filter_order=8

CSV_FILES=*.csv
rm -f error_files.txt

for f in $CSV_FILES 
do

 	echo "Processing file: " 
 	echo $f

#   -ft FILTER_TYPE, --filter_type FILTER_TYPE
#                         Filter Type 0=default 1=low pass, 2=bandpass

# ./analyze_muse_data.py -s -c -ag -mc -db -fd -ft 1  -hc 20 -lc 5 -o 8 -v 3 -hdf5 -r -f /Users/dperi/Documents/Muse_Dev/analyze_eeg/data-for-testing.csv

    analyze_muse_data.py --batch --power --eeg --stats_plots --coherence_plots --accel_gyro \
                --mellow_concentration --data_base --auto_reject_data \
                --filter_data --filter_typ 1 --highcut 20.0 --lowcut 0.5 --filter_order 8  \
                --verbose 3  --write_hdf5_file  -f $f

	case {$?} in
		0) 
		# true # ok
		;;
	 
		*) 
		# false # something went wrong
		echo $f >>  error_files.txt
		
	esac 

done


