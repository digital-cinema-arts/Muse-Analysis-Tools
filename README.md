# Muse-Analysis-Tools
 
# ABCS - Algorithmic Biofeedback Control System - Chart Tools


This script wil generate a number of charts from Muse headband EEG data. 

Options: 

   "-c", "--csv_file", help="CSV file to read)")
   "-v", "--verbose", help="Increase output verbosity", type=int)
   "-p", "--power", help="Plot Power Bands", action="store_true")
   "-e", "--eeg", help="Plot EEG Data", action="store_true")
   "-i", "--integrate", help="Integrate EEG Data", action="store_true")
   "-s", "--step_size", help="Integration Step Size", type=int)
   "-f", "--filter_data", help="Filter EEG Data", action="store_true")
   "-l", "--logging_level", help="Logging verbosity: 1 = info, 2 = warning, 2 = debug", type=int)    

 
Muse Monitor CSV file format

1) Remove the first line
2) Run the script
3) Observe the graphs
4) Relax and contemplate all things divine






