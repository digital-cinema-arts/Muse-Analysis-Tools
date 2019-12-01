# Muse-Analysis-Tools
 
# Algorithmic Biofeedback Control System - Chart Tools


This script wil generate a number of charts from Muse headband EEG CSV data files created by the Mind Monitor app.  Future versions of these tools will support Muse DIrect and Muse Lab files.


Install instructions:

1) Download the archive file, unzip in a temp directory
2) Copy the Python script (analyze_mind_monitor_data.py) to a directory that's in your $PATH, for example:  cp analyze_mind_monitor_data.py ~/bin.  (This makes it easier to execute the script from any locaiton in your filesystem)
3) Change directory to where the Mind Monitor CSV files are located.  
4) Startup the application: analyze_mind_monitor_data.py
5) Select the options and CSV file you want to process.



Notes:
1) Output images and session data are created within the same directory that the CSV files live.  This will change in the future to allow the user to select the output directory.







Options: 

analyze_muse_monitor_data.py -h

usage: analyze_muse_monitor_data.py [-h] [-c CSV_FILE] [-v VERBOSE] [-d]

optional arguments:
  -h, --help            show this help message and exit
  -c CSV_FILE, --csv_file CSV_FILE
                        CSV file to read)
  -v VERBOSE, --verbose VERBOSE
                        Increase output verbosity
  -d, --display_plots   Display Plots


 







