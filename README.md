# Muse-Analysis-Tools
 
## Algorithmic Biofeedback Control System - Chart Tools

This script will generate a number of charts from Muse headband EEG CSV data files created by the Mind Monitor app.  Future versions of these tools will support Muse Direct and Muse Lab files.

--------------------------------------------------------------------
### Install instructions:
#### Download and Install
1) Download the archive file, save in a temp directory
2) Unzip the file:   
```$ unzip Muse-Analysis-Tools-master.zip```
3) Change diretory into the Muse-Analysis-Tools-master directory:   
```$ cd Muse-Analysis-Tools-master```
4) Run the setup.py to install the application:   
```$ python3 setup.py install```
 
#### Clone using Git and Install
1) Clone the project using git in a temp directory.  
```$ git clone https://github.com/digital-cinema-arts/Muse-Analysis-Tools.git```
2) Change diretory into the Muse-Analysis-Tools-master directory:   
```$ cd Muse-Analysis-Tools-master``` 
3) Run the setup.py to install the application:   
```$ python3 setup.py install```

#### Install from the Python Package Index
The project can be view here:
https://pypi.org/project/Muse-Analysis-Tools/

Using the 'pip' command:  
```$ pip install Muse-Analysis-Tools```

Using the 'pip3' command to ensure you're installing the Python 3 packages:  
```$ pip3 install Muse-Analysis-Tools```

--------------------------------------------------------------------

##### NOTE: This application requires Python version 3. To check which version of python you have installed enter this command:   
```
$ python --version
Python 3.7.4
```

--------------------------------------------------------------------

To fix an error with pandas on Linux that occasionally happens, force a reinstall with this command:

```
pip install --upgrade --force-reinstall pandas
```

--------------------------------------------------------------------

#### Usage:
1) Change directory to where the data files are located (sometimes this makes it easier to locate files).  
```
$ cd /Volumes/Archive/muse_recordings/muse_monitor_recordings/   
```
2) Startup the application:  
```$ analyze_muse_data.py```
3) Select the options and CSV file you want to process.  
4) Make plots!  

--------------------------------------------------------------------

#### Notes:
1) Output images and session data are created within the same directory that the CSV files live.  This will change in the future to allow the user to select the output directory.

--------------------------------------------------------------------

For more information about the graphs interface (from matplotlib) please refer to this link:
https://matplotlib.org/3.1.1/users/navigation_toolbar.html

--------------------------------------------------------------------

#### Options: 

~~~~

$ analyze_muse_data.py -h 
 
usage: analyze_muse_data.py [-h] [--version] [-f CSV_FILE] [-v VERBOSE] [-d]
                            [-b] [-dm] [-pm] [-e] [-p] [-ep] [-hdf5] [-ag]
                            [-mc] [-s] [-c] [--plot_style PLOT_STYLE] [-sm]
                            [-sw SMOOTH_WINDOW] [-r] [-eegc EEG_CLIP] [-fd]
                            [-ft FILTER_TYPE] [-lc LOWCUT] [-hc HIGHCUT]
                            [-o FILTER_ORDER] [-db]

optional arguments:
  -h, --help            show this help message and exit
  --version             Print the current version number
  -f CSV_FILE, --csv_file CSV_FILE
                        CSV file to read)
  -v VERBOSE, --verbose VERBOSE
                        Increase output verbosity
  -d, --display_plots   Display Plots
  -b, --batch           Batch Mode
  -dm, --data_markers   Add Data Markers
  -pm, --plot_markers   Add Plot Markers
  -e, --eeg             Plot EEG Data
  -p, --power           Plot Power Bands
  -ep, --eeg_power      Plot EEG & Power Data Combined
  -hdf5, --write_hdf5_file
                        Write output data into HDF5 file
  -ag, --accel_gyro     Plot Acceleration and Gyro Data
  -mc, --mellow_concentration
                        Plot Mellow and Concentratio Data (Only For Mind
                        Monitor Data)
  -s, --stats_plots     Plot Statistcal Data
  -c, --coherence_plots
                        Plot Coherence Data
  --plot_style PLOT_STYLE
                        Plot Syle: 1=seaborn, 2=seaborn-pastel, 3=seaborn-
                        ticks, 4=fast, 5=bmh
  -sm, --smooth_data    Smooth EEG Data
  -sw SMOOTH_WINDOW, --smooth_window SMOOTH_WINDOW
                        Smoothing Window (Seconds)
  -r, --auto_reject_data
                        Auto Reject EEG Data
  -eegc EEG_CLIP, --eeg_clip EEG_CLIP
                        Cliping for Auto Reject EEG Data
  -fd, --data_filtering
                        Filter EEG Data
  -ft FILTER_TYPE, --filter_type FILTER_TYPE
                        Filter Type 0=default 1=low pass, 2=bandpass
  -lc LOWCUT, --lowcut LOWCUT
                        Filter Low Cuttoff Frequency
  -hc HIGHCUT, --highcut HIGHCUT
                        Filter High Cuttoff Frequency
  -o FILTER_ORDER, --filter_order FILTER_ORDER
                        Filter Order
  -db, --data_base      Send session data and statistics to database
  
  ~~~~

To find the current version of the application:  
```$ analyze_muse_data.py --version
Current version:  1.1.23
```

----------------------------------------------------------

The ".ABCS_parms.rc" runtime configuration file can be configured to define often used parameters or for batch processing.

```
{"First Name": "Debra", "Last Name": "Peri", "Data Dir": "/Volumes/Archive/muse_recordings/muse_monitor_recordings",
"Data Base Location": "/Volumes/Archive/muse_recordings/muse_monitor_recordings", "Filter Data": 1, "Filter Type": 1, "Filter LowCut": 0.5, "Filter HighCut": 70.0}
```

---------------------------------------------------------------------

![picture alt](https://github.com/digital-cinema-arts/Muse-Analysis-Tools/blob/master/images/GUI.png "The analyze_muse_data GUI")

https://github.com/digital-cinema-arts/Muse-Analysis-Tools/wiki/Example-Plots

---------------------------------------------------------------------

#### Important note on sampling rate:  Select "Constant" from the Mind Monitor recording interval option.

![picture alt](https://github.com/digital-cinema-arts/Muse-Analysis-Tools/blob/master/images/MM-recording-interval.png "Mind Monitor recording interval option")

---------------------------------------------------------------------

#### Session data in JSON format.

![picture alt](https://github.com/digital-cinema-arts/Muse-Analysis-Tools/blob/master/images/session_JSON-1.png "JSON session data")

---------------------------------------------------------------------

#### Session data in SQL (SQLite) Database.

![picture alt](https://github.com/digital-cinema-arts/Muse-Analysis-Tools/blob/master/images/ABCS-DB.png "Database session data")

---------------------------------------------------------------------

#### Session/EEG data in HDF5 format.

![picture alt](https://github.com/digital-cinema-arts/Muse-Analysis-Tools/blob/master/images/HDF5_data_1.png "HDF5 data")

![picture alt](https://github.com/digital-cinema-arts/Muse-Analysis-Tools/blob/master/images/HDF5_data_2.png "HDF5 data")


---------------------------------------------------------------------

#### Donations

https://paypal.me/vinyasakramayoga?locale.x=en_US

If you would like to support this project, to help to contribute to disabled folks and to help youth gain access to yoga (in the Olympia, WA area) please send your kind donations to this paypal account


:droplet:


