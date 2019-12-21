# Muse-Analysis-Tools
 
## Algorithmic Biofeedback Control System - Chart Tools

#### NOTE: This project is still in active development! There may be bugs, there may be missing features, but will be released officially very soon.  Thank you for your patience.

This script will generate a number of charts from Muse headband EEG CSV data files created by the Mind Monitor app.  Future versions of these tools will support Muse Direct and Muse Lab files.


Install instructions:

1) Download the archive file, save in a temp directory
2) Unzip the file:   
```Tethys: $ unzip Muse-Analysis-Tools-master.zip```
3) Change diretory into the Muse-Analysis-Tools-master directory:   
```Tethys: $ cd Muse-Analysis-Tools-master```
4) Run the setup.py to install the application:   
```Tethys: $ python3 setup.py install```
<BR>
#### NOTE: This application requires Python version 3 installed on your computer. To check for which version of python you have installed enter this command:   

```
Tethys: $  python --version
Python 3.7.4
```

--------------------------------------------------------------------

Usage:
1) Change directory to where the Mind Monitor CSV files are located.  
2) Startup the application:  
```analyze_muse_data.py
3) Select the options and CSV file you want to process.
4) Make plots!

--------------------------------------------------------------------

Notes:
1) Output images and session data are created within the same directory that the CSV files live.  This will change in the future to allow the user to select the output directory.


--------------------------------------------------------------------

The ".ABCS_parms.rc" file.

```
{"First Name": "Debra", "Last Name": "Peri", "Data Dir": "/Volumes/Archive/muse_recordings/muse_monitor_recordings"}
```

--------------------------------------------------------------------

Options: 

~~~~

Tethys: $  analyze_muse_data.py -h 
 
usage: analyze_muse_data.py [-h] [-c CSV_FILE] [-v VERBOSE] [-d] [-b] [-p]
                            [-e] [--plot_3D] [-i] [-s STEP_SIZE] [-ps] [-f]
                            [-lc LOWCUT] [-hc HIGHCUT] [-o FILTER_ORDER]
                            [-l LOGGING_LEVEL]

optional arguments:
  -h, --help            show this help message and exit
  -c CSV_FILE, --csv_file CSV_FILE
                        CSV file to read)
  -v VERBOSE, --verbose VERBOSE
                        Increase output verbosity
  -d, --display_plots   Display Plots
  -b, --batch           Batch Mode
  -p, --power           Plot Power Bands
  -e, --eeg             Plot EEG Data
  --plot_3D             3D Display Plots
  -i, --integrate       Integrate EEG Data
  -s STEP_SIZE, --step_size STEP_SIZE
                        Integration Step Size
  -ps, --power_spectrum
                        Analyze Spectrum
  -f, --filter_data     Filter EEG Data
  -lc LOWCUT, --lowcut LOWCUT
                        Filter Low Cuttoff Frequency
  -hc HIGHCUT, --highcut HIGHCUT
                        Filter High Cuttoff Frequency
  -o FILTER_ORDER, --filter_order FILTER_ORDER
                        Filter Order
  -l LOGGING_LEVEL, --logging_level LOGGING_LEVEL
                        Logging verbosity: 1 = info, 2 = warning, 2 = debug

  ~~~~


---------------------------------------------------------------------


![picture alt](https://github.com/digital-cinema-arts/Muse-Analysis-Tools/blob/master/images/GUI.png "The GUI")

https://github.com/digital-cinema-arts/Muse-Analysis-Tools/wiki/Example-Plots


---------------------------------------------------------------------

*Important note on sampling rate:  Select "Continous" from the Mind Monitor recording interval option.


![picture alt](https://github.com/digital-cinema-arts/Muse-Analysis-Tools/blob/master/images/MM-recording-interval.png "Mind Monitor recording interval option")

---------------------------------------------------------------------
Donations

https://paypal.me/vinyasakramayoga?locale.x=en_US

If you would like to support this project, to help to contribute to disabled folks and to help youth gain access to yoga (in the Olympia, WA area) please send your kind donations to this paypal account.  We appreciate any and all help for this important work.

You can read more about our outreach program here:

https://xion.org/VinyasaKramaYogaOlympia/index.php/rainbow-goddess/





:droplet:


