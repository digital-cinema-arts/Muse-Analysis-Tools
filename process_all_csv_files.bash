#!/usr/bin/env bash

filter_order=8
CSV_FILES=*.csv
ZIP_FILES=*.zip
rm -f error_files.txt

for f in $CSV_FILES 
do
 	echo "Processing file: " 
 	echo $f

    	analyze_muse_data.py --batch -p -e -s -c -ag \
                --mellow_concentration --data_base --auto_reject_data -sm -sw 2 \
                --data_filtering --filter_type 1 --highcut 50.0 --lowcut 0.5 --filter_order 8  \
		-ep -eegc 50  \
                --verbose 1 --plot_style 3  --write_hdf5_file  -f './'$f

	case {$?} in
		0) 
		# true # ok
		;;
	 
		*) 
		# false # something went wrong
		echo $f >>  error_files.txt
	esac 

done


# ./analyze_muse_data.py -s -c -ag -mc -db -fd -ft 1  -hc 20 -lc 5 -o 8 -v 3 -hdf5 -r -f /Users/dperi/Documents/Muse_Dev/analyze_eeg/data-for-testing.csv

#usage: analyze_muse_data.py [-h] [--version] [-f CSV_FILE] [-v VERBOSE] [-d]
#                            [-b] [-dm] [-pm] [-e] [-p] [-ep] [-hdf5] [-ag]
#                            [-mc] [-s] [-c] [--plot_style PLOT_STYLE] [-sm]
#                            [-sw SMOOTH_WINDOW] [-r] [-eegc EEG_CLIP] [-fd]
#                            [-ft FILTER_TYPE] [-lc LOWCUT] [-hc HIGHCUT]
#                            [-o FILTER_ORDER] [-db]

#optional arguments:
#  -h, --help            show this help message and exit
#  --version             Print the current version number
#  -f CSV_FILE, --csv_file CSV_FILE
#                        CSV file to read)
#  -v VERBOSE, --verbose VERBOSE
#                        Increase output verbosity
#  -d, --display_plots   Display Plots
#  -b, --batch           Batch Mode
#  -dm, --data_markers   Add Data Markers
#  -pm, --plot_markers   Add Plot Markers
#  -e, --eeg             Plot EEG Data
#  -p, --power           Plot Power Bands
#  -ep, --eeg_power      Plot EEG & Power Data Combined
#  -hdf5, --write_hdf5_file
#                        Write output data into HDF5 file
#  -ag, --accel_gyro     Plot Acceleration and Gyro Data
#  -mc, --mellow_concentration
#                        Plot Mellow and Concentration Data (Only For Mind
#                        Monitor Data)
#  -s, --stats_plots     Plot Statistcal Data
#  -c, --coherence_plots
#                        Plot Coherence Data
#  --plot_style PLOT_STYLE
#                        Plot Syle: 1=seaborn, 2=seaborn-pastel, 3=seaborn-
#                        ticks, 4=fast, 5=bmh
#  -sm, --smooth_data    Smooth EEG Data
#  -sw SMOOTH_WINDOW, --smooth_window SMOOTH_WINDOW
#                        Smoothing Window (Seconds)
#  -r, --auto_reject_data
#                        Auto Reject EEG Data
#  -eegc EEG_CLIP, --eeg_clip EEG_CLIP
#                        Cliping for Auto Reject EEG Data
#  -fd, --data_filtering
#                        Filter EEG Data
#  -ft FILTER_TYPE, --filter_type FILTER_TYPE
#                        Filter Type 0=default 1=low pass, 2=bandpass
#  -lc LOWCUT, --lowcut LOWCUT
#                        Filter Low Cuttoff Frequency
#  -hc HIGHCUT, --highcut HIGHCUT
#                        Filter High Cuttoff Frequency
#  -o FILTER_ORDER, --filter_order FILTER_ORDER
#                        Filter Order
#  -db, --data_base      Send session data and statistics to database
#
