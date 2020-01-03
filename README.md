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

--------------------------------------------------------------------

#### NOTE: This application requires Python version 3. To check which version of python you have installed enter this command:   
```
$ python --version
Python 3.7.4
```

--------------------------------------------------------------------

#### Usage:
1) Change directory to where the Mind Monitor CSV files are located.  
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

The ".ABCS_parms.rc" file.

```
{"First Name": "Debra", "Last Name": "Peri", "Data Dir": "/Volumes/Archive/muse_recordings/muse_monitor_recordings"}
```

--------------------------------------------------------------------

#### Options: 

~~~~

$ analyze_muse_data.py -h 
 
usage: analyze_muse_data.py [-h] [-f CSV_FILE] [-v VERBOSE] [-d] [-b] [-p]
                            [-e] [-hdf5] [-ag] [-mc] [-s] [-c] [-r] [-fd]
                            [-ft FILTER_TYPE] [-lc LOWCUT] [-hc HIGHCUT]
                            [-o FILTER_ORDER] [-db]

optional arguments:
  -h, --help            show this help message and exit
  -f CSV_FILE, --csv_file CSV_FILE
                        CSV file to read)
  -v VERBOSE, --verbose VERBOSE
                        Increase output verbosity
  -d, --display_plots   Display Plots
  -b, --batch           Batch Mode
  -p, --power           Plot Power Bands
  -e, --eeg             Plot EEG Data
  -hdf5, --write_hdf5_file
                        Write output data into HDF5 file
  -ag, --accel_gyro     Plot Acceleration and Gyro Data
  -mc, --mellow_concentration
                        Plot Mellow and Concentratio Data (Only For Mind
                        Monitor Data)
  -s, --stats_plots     Plot Statistcal Data
  -c, --coherence_plots
                        Plot Coherence Data
  -r, --auto_reject_data
                        Auto Reject EEG Data
  -fd, --filter_data    Filter EEG Data
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

----------------------------------------------------------

To fix an error with pandas on Linux that occasionally happens, force a reinstall with this command:

```
pip install --upgrade --force-reinstall pandas
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

#### Session/EEG data in HDF5 format.

![picture alt](https://github.com/digital-cinema-arts/Muse-Analysis-Tools/blob/master/images/HDF5_data_1.png "HDF5 data")

![picture alt](https://github.com/digital-cinema-arts/Muse-Analysis-Tools/blob/master/images/HDF5_data_2.png "HDF5 data")


---------------------------------------------------------------------

#### Donations

https://paypal.me/vinyasakramayoga?locale.x=en_US

If you would like to support this project, to help to contribute to disabled folks and to help youth gain access to yoga (in the Olympia, WA area) please send your kind donations to this paypal account.  We appreciate any and all help for this important work.

You can read more about our outreach program here:

https://xion.org/VinyasaKramaYogaOlympia/index.php/rainbow-goddess/


:droplet:


