#!/usr/bin/env python3

''' 

This code will analyze Mind Monitor CSV files and plot the results.


'''

from time import time, sleep
import datetime as dt

import numpy as np
from scipy import fftpack
import scipy.signal as signal
import math
import bitstring
import pandas as pd
import os
# from sys import platform
from time import time, sleep, strftime, gmtime
import sys
import csv
import argparse
import math
# import logging
# from binascii import hexlify
# import timeit
# import io
from progress.bar import Bar, IncrementalBar
import json
from pathlib import Path
from scipy import integrate, signal
from scipy.signal import butter, lfilter

from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()

# from mpl_toolkits.mplot3d import Axes3D
# import matplotlib.patches as mpatches
import matplotlib
# matplotlib.use('Agg')
import matplotlib.pyplot as plt
# from matplotlib import cm
import matplotlib.dates as md
import matplotlib.ticker as ticker

    # from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QPushButton, QVBoxLayout
from PyQt5.QtWidgets import *
# from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPalette, QIcon, QPixmap
# from PyQt5.QtWidgets import QApplication, QPushButton

from PyQt5.QtCore import QDateTime, Qt, QTimer
from PyQt5.QtWidgets import (QApplication, QCheckBox, QComboBox, QDateTimeEdit,
        QDial, QDialog, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit,
        QProgressBar, QPushButton, QRadioButton, QScrollBar, QSizePolicy,
        QSlider, QSpinBox, QStyleFactory, QTableWidget, QTabWidget, QTextEdit,
        QVBoxLayout, QWidget)


# Globals
# Integrate_Step_Size = 4
muse_EEG_data = []
EEG_Dict ={}
eeg_stats = []
MM_CVS_fname = ""
out_dirname = ""
Filter_Lowcut  = 2.0
Filter_Highcut  = 60.0
Filter_Order = 3
NOTCH_B, NOTCH_A = butter(4, np.array([55, 65]) / (256 / 2), btype='bandstop')

session_dict = {}
gui_dict = {}
first_name = ""
last_name = ""
data_dir = ""

# Constants
SAMPLING_RATE = 250.0
FIGURE_SIZE = (8, 6)
PLOT_DPI = 100

# Muse Monitor Colors

MM_Colors = {
'RawTP9': '#cc0000',
'RawAF7': '#cc98e5',
'RawAF8': '#7fcce5',
'RawTP10': '#b2cc7f',
'Delta': '#d42727',
'Theta': '#9933cc',
'Alpha': '#0d90cc',
'Beta':  '#669900',
'Gamma': '#ff900c'
}


# matplotlib.colors
# b : blue.
# g : green.
# r : red.
# c : cyan.
# m : magenta.
# y : yellow.
# k : black.
# w : white.


# Value	Description
# 'on'	Turn on axis lines and labels. Same as True.
# 'off'	Turn off axis lines and labels. Same as False.
# 'equal'	Set equal scaling (i.e., make circles circular) by changing axis limits.
# 'scaled'	Set equal scaling (i.e., make circles circular) by changing dimensions of the plot box.
# 'tight'	Set limits just large enough to show all data.
# 'auto'	Automatic scaling (fill plot box with data).
# 'normal'	Same as 'auto'; deprecated.
# 'image'	'scaled' with axis limits equal to data limits.
# 'square'	Square plot; similar to 'scaled', but initially forcing xmax-xmin = ymax-ymin.



class The_GUI(QDialog):
    def __init__(self, parent=None):
        super(The_GUI, self).__init__(parent)

        self.originalPalette = QApplication.palette()

#         print("keys: ", QStyleFactory.keys())
        
        self.createTopLeftGroupBox()
        self.createTopRightGroupBox()
        self.createBottomLeftTabWidget()
        self.createBottomRightGroupBox()
#         self.createProgressBar()

#         self.openFileNameDialog()

        topLayout = QHBoxLayout()
        topLayout.addStretch(1)

        mainLayout = QGridLayout()
        mainLayout.addLayout(topLayout, 0, 0, 1, 2)
        mainLayout.addWidget(self.topLeftGroupBox, 1, 0)
        mainLayout.addWidget(self.topRightGroupBox, 1, 1)
        mainLayout.addWidget(self.bottomRightTabWidget, 2, 1)
        mainLayout.addWidget(self.bottomLeftGroupBox, 2, 0)
        mainLayout.addWidget(self.progressBar, 3, 0, 1, 2)
        mainLayout.setRowStretch(1, 1)
        mainLayout.setRowStretch(2, 1)
        mainLayout.setColumnStretch(0, 1)
        mainLayout.setColumnStretch(1, 1)
        self.setLayout(mainLayout)

#         self.lineFirstNameEdit = QLineEdit(self)
#         self.lineLastNameEdit = QLineEdit(self)

#         self.lineFirstNameEdit = QLineEdit('First Name')
#         self.lineLastNameEdit = QLineEdit('Last Name')


        self.left = 40
        self.top = 100
        self.width = 640
        self.height = 480
        self.setGeometry(self.left, self.top, self.width, self.height)
        
        global first_name
        global last_name
        
        self.first_name = first_name
        self.last_name = last_name
        
#         print("The_GUI(): first_name ", first_name)
#         print("The_GUI(): last_name ", last_name)
# 
#         print("The_GUI(): self.first_name ", self.first_name)
#         print("The_GUI(): self.last_name ", self.last_name)

               
        self.setWindowTitle("Meditation Session Details")
#         self.changeStyle('macintosh')

        QApplication.setStyle(QStyleFactory.create('macintosh'))

        
        
        
    def advanceProgressBar(self):
        curVal = self.progressBar.value()
        maxVal = self.progressBar.maximum()
        self.progressBar.setValue(curVal + (maxVal - curVal) / 100)


#     def on_click(self):
#         textboxValue = self.textbox.text()
#         QMessageBox.question(self, 'Message - pythonspot.com', "You typed: " + 
#             textboxValue, QMessageBox.Ok, QMessageBox.Ok)
#         self.textbox.setText("")
        

    def file_button_clicked(self):
        self.openFileNameDialog()
    

# 	
#     def hovered():
#        print ("hovering")
# 
# 
#     def clicked():
#        print ("clicked")
# 	
	
	
         
    def plot_button_clicked(self):

        alert = QMessageBox()
        alert.setText('Plotting!')
#     
#         alert.setIcon(QMessageBox.Warning)
#         alert.setText("Plotting Data!")

    #     btnCancel =  alert.addButton( "Cancel", QMessageBox.RejectRole )
    #     alert.setAttribute(Qt.WA_DeleteOnClose)
    
#         alert.setModal(True)

    #     session_dict.update(parms_dict)
        session_json = json.dumps(session_dict, sort_keys=True)
    #     print(session_json)

        first_name = self.lineFirstNameEdit.text()
#         print("plot_button_clicked(): ", self.lineFirstNameEdit.text())
#         print("plot_button_clicked(): first_name ", first_name)

        last_name = self.lineLastNameEdit.text()
#         print("plot_button_clicked(): ", self.lineLastNameEdit.text())
#         print("plot_button_clicked(): last_name ", last_name)

#         textboxValue = self.textbox.text()
#         print("plot_button_clicked(): textboxValue ", textboxValue)

        interative_GUI = self.checkBoxInteractive.isChecked()
#         if interative_GUI:
#             print("plot_button_clicked(): checkBoxInteractive CHECKED")

        coherence = self.checkBoxCoherence.isChecked()
#         if coherence:
#             print("plot_button_clicked(): checkBoxCoherence CHECKED")


        power_bands = self.checkBoxPowerBands.isChecked()
        mellow_concentrate = self.checkBoxMellowConcentration.isChecked()
        accel_gyro = self.checkBoxAccelGyro.isChecked()
        plot_3D = self.checkBox3D.isChecked()
        filter = self.checkBoxFilter.isChecked()
        integrate = self.checkBoxIntegrate.isChecked()
        DB = self.checkBoxDB.isChecked()
        HDF5 = self.checkBoxHFDF5.isChecked()

        mood = self.moodComboBox.currentText()
#         print("plot_button_clicked() - mood: ", mood)

        
        global gui_dict      
        gui_dict.update({'firstName': first_name,'lastName': last_name})

        gui_dict.update({'firstName': first_name,'lastName': last_name,
                "checkBoxInteractive": interative_GUI, 
                "checkBoxCoherence": coherence,
                "checkBoxPowerBands": power_bands,
                "checkBoxMellowConcentration": mellow_concentrate,
                "checkBoxAccelGyro": accel_gyro,
                "checkBox3D": plot_3D,
                "checkBoxFilter": filter,
                "checkBoxIntegrate": integrate,
                "checkBoxDB": DB,
                "checkBoxHFDF5": HDF5,
                "Mood": mood})

        print("plot_button_clicked(): gui_dict ", gui_dict)

#         self.accept()
        self.close()

#         alert.show()
#         alert.exec_()

         
         

    def createTopLeftGroupBox(self):
        self.topLeftGroupBox = QGroupBox("Select Options")

        self.checkBoxInteractive = QCheckBox("Display Interactive Plots")
        self.checkBoxInteractive.setChecked(True)
        self.checkBoxInteractive.setEnabled(True)

        self.checkBoxCoherence = QCheckBox("Create Coherance Plots")
        self.checkBoxCoherence.setChecked(False)
        self.checkBoxCoherence.setEnabled(True)
        
        self.checkBoxPowerBands = QCheckBox("Create Power Bands Plots")
        self.checkBoxPowerBands.setChecked(True)
        self.checkBoxPowerBands.setEnabled(True)
        
        self.checkBoxMellowConcentration = QCheckBox("Create Mellow/Concentration Plots")
        self.checkBoxMellowConcentration.setChecked(False)
        self.checkBoxMellowConcentration.setEnabled(True)

        self.checkBoxAccelGyro = QCheckBox("Create Accleration/Gyro Plots")
        self.checkBoxAccelGyro.setChecked(False)
        self.checkBoxAccelGyro.setEnabled(True)

        self.checkBox3D = QCheckBox("Create 3D Plots")
        self.checkBox3D.setChecked(False)
        self.checkBox3D.setEnabled(False)

        self.checkBoxFilter = QCheckBox("Filter Data")
        self.checkBoxFilter.setChecked(False)
        self.checkBoxFilter.setEnabled(False)

        self.checkBoxIntegrate = QCheckBox("Integrate Data")
        self.checkBoxIntegrate.setChecked(False)
        self.checkBoxIntegrate.setEnabled(False)

        self.checkBoxDB = QCheckBox("Send Results to Database")
        self.checkBoxDB.setChecked(False)
        self.checkBoxDB.setEnabled(False)

        self.checkBoxHFDF5 = QCheckBox("Write HDF5 File")
        self.checkBoxHFDF5.setChecked(False)
        self.checkBoxHFDF5.setEnabled(False)
 
     
        layout = QVBoxLayout()
        layout.addWidget(self.checkBoxInteractive)
        layout.addWidget(self.checkBoxCoherence)
        layout.addWidget(self.checkBoxPowerBands)
        layout.addWidget(self.checkBoxMellowConcentration)
        layout.addWidget(self.checkBoxAccelGyro)
        layout.addWidget(self.checkBox3D)
        layout.addWidget(self.checkBoxFilter)
        layout.addWidget(self.checkBoxIntegrate)
        layout.addWidget(self.checkBoxDB)
        layout.addWidget(self.checkBoxHFDF5)
        
        self.moodComboBox = QComboBox()
        self.moodComboBox.addItems(['Calm', 'Awake', 'Excited', 'Stressed', 'Sleepy'])

        moodLabel = QLabel("Mood")
        moodLabel.setBuddy(self.moodComboBox)
        layout.addWidget(self.moodComboBox)

        layout.addStretch(1)
        self.topLeftGroupBox.setLayout(layout)    



    def createTopRightGroupBox(self):
        self.topRightGroupBox = QGroupBox("Meditation Session Details")

#         linePasswordEdit = QLineEdit('Enter a Password')
#         linePasswordEdit.setEchoMode(QLineEdit.Password)

        self.lineFirstNameEdit = QLineEdit(first_name)
#         self.lineFirstNameEdit = QLineEdit('First Name')
        self.lineFirstNameEdit.setEchoMode(QLineEdit.Normal)
        self.lineLastNameEdit = QLineEdit(last_name)
#         self.lineLastNameEdit = QLineEdit('Last Name')
        self.lineLastNameEdit.setEchoMode(QLineEdit.Normal)

        self.dateTimeEdit = QDateTimeEdit(self.topRightGroupBox)
        self.dateTimeEdit.setDateTime(QDateTime.currentDateTime())

        layout = QGridLayout()
        layout.addWidget(self.lineFirstNameEdit, 1, 0, 1, 2)
        layout.addWidget(self.lineLastNameEdit, 2, 0, 1, 2)

#         layout.addWidget(linePasswordEdit, 3, 0, 1, 2)
                
#         layout.addWidget(spinBox, 1, 0, 1, 2)
        layout.addWidget(self.dateTimeEdit, 0, 0, 1, 2)
#         layout.addWidget(slider, 3, 0)
#         layout.addWidget(scrollBar, 4, 0)
#         layout.addWidget(dial, 3, 1, 2, 1)
        layout.setRowStretch(5, 1)
        
    
        self.topRightGroupBox.setLayout(layout)



    def createBottomLeftTabWidget(self):
        self.bottomRightTabWidget = QTabWidget()
        self.bottomRightTabWidget.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Ignored)

        tab1 = QWidget()
        tableWidget = QTableWidget(10, 10)

        tab1hbox = QHBoxLayout()
        tab1hbox.setContentsMargins(5, 5, 5, 5)
        tab1hbox.addWidget(tableWidget)
        tab1.setLayout(tab1hbox)

        tab2 = QWidget()
        textEdit = QTextEdit()

        textEdit.setPlainText("Add any details about your meditation session.  "
                              "For example, mood, place, music,\n" 
                              "have recently eaten, etc.\n")

        tab2hbox = QHBoxLayout()
        tab2hbox.setContentsMargins(5, 5, 5, 5)
        tab2hbox.addWidget(textEdit)
        tab2.setLayout(tab2hbox)

        self.bottomRightTabWidget.addTab(tab2, "Session Notes")




    def createBottomRightGroupBox(self):

        filePushButton = QPushButton("Select CSV File")
        filePushButton.clicked.connect(self.file_button_clicked)
#         filePushButton.setDefault(False)

        plotPushButton = QPushButton("Create Plots")
#         defaultPushButton.setDefault(True)
        plotPushButton.clicked.connect(self.plot_button_clicked)

        self.bottomLeftGroupBox = QGroupBox("Create Plots")

        l1 = QLabel(self)
#         l2 = QLabel(self)
#         l3 = QLabel(self)
# 
#         l1.setText("Equal Ground Wellness Coop")
#         l2.setText("Make Plots with you EEG data")
        l1.setText("Choose File:")
        l1.setAlignment(Qt.AlignCenter)

#         l3.setAlignment(Qt.AlignCenter)

#         l2.setPixmap(QPixmap("full-moon-3.jpg"))

#         pixmap = QPixmap("full-moon-3.jpg") 
#         pixmap = pixmap.scaled(128, 128, Qt.KeepAspectRatio)
# #         pixmap = QPixmap("full-moon-3.jpg")
#         l3.setPixmap(pixmap)
    
#         l1.setOpenExternalLinks(True)
#         l2.linkHovered.connect(self.hovered)
#         l1.setTextInteractionFlags(Qt.TextSelectableByMouse)

#         self.bottomLeftGroupBox.setCheckable(True)
#         self.bottomLeftGroupBox.setChecked(True)


        layout = QVBoxLayout()
        layout.addWidget(l1)
        layout.addWidget(filePushButton)
        layout.addWidget(plotPushButton)
#         layout.addWidget(l2)
#         layout.addWidget(l3)
      
#         layout.addWidget(togglePushButton)
#         layout.addWidget(flatPushButton)

        layout.addStretch(1)
        self.bottomLeftGroupBox.setLayout(layout)



    def createProgressBar(self):
        self.progressBar = QProgressBar()
        self.progressBar.setRange(0, 10000)
        self.progressBar.setValue(0)

        timer = QTimer(self)
        timer.timeout.connect(self.advanceProgressBar)
        timer.start(1000)



    def openFileNameDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self,
        "Select Muse Monitor CSV File", "","MM CSV files (*.csv)", options=options)
#         "Select Muse Monitor CSV File", "","All Files (*);;MM CSV files (*.csv)", options=options)
#         "QFileDialog.getOpenFileName()", "","All Files (*);;Python Files (*.py)", options=options)
        if fileName:
            print(fileName)
            
        global gui_dict    
        global MM_CVS_fname 
        MM_CVS_fname = fileName
    
        gui_dict = {'fileName': MM_CVS_fname}
    
#     def openFileNamesDialog(self):
#         options = QFileDialog.Options()
#         options |= QFileDialog.DontUseNativeDialog
#         files, _ = QFileDialog.getOpenFileNames(self,
#         "Select Muse Monitor CSV Files", "","All Files (*);;Python Files (*.py)", options=options)
#         if files:
#             print(files)
    
    def saveFileDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getSaveFileName(self,
        "Select Output file","","All Files (*);;JPG Files (*.jpg)", options=options)
        if fileName:
            print(fileName)
            
            
            

def manage_session_data(session_dict, EEG_Dict):

    session_dict = {
        'Session_Data':{
        'date': date_time_now,
        'data_file_fname': 'foo',
        'mood': 'calm',
        'location': 'home',
        'activity': "sitting",
        'misc': 'This field is for misc. data to be stored in the database'
        },
        'Participants':{ 
            'Meditators':{
                0:{
                    'name': 'Debra',
                    'age': 63,
                    'gender': 'female'
                    },          
                1:{
                    'name': 'Savahn',
                    'age': 38,
                    'gender': 'female'
                    }     
                },
            'Coordinators':{
                0:{
                    'name': 'Patti',
                    'age': 32,
                    'gender': 'female'
                    }
                },
            'Helpers':{
                0:{
                    'name': 'Oni',
                    'age': 23,
                    'gender': 'male'
                    }
                },
            'Participants':{
                0:{
                    'name': 'Shiloh',
                    'age': 34,
                    'gender': 'male'
                    }
                }
            }
        }


    session_dict.update(EEG_Dict)

    return(session_dict)
 
 

   

def read_eeg_data(fname, date_time_now):
   
    print("read_eeg_data(): Reading EEG data ...")

    global session_dict

# Muse Monitor CSV format:
# TimeStamp,
# Delta_TP9,Delta_AF7,Delta_AF8,Delta_TP10,
# Theta_TP9,Theta_AF7,Theta_AF8,Theta_TP10,
# Alpha_TP9,Alpha_AF7,Alpha_AF8,Alpha_TP10,
# Beta_TP9,Beta_AF7,Beta_AF8,Beta_TP10,
# Gamma_TP9,Gamma_AF7,Gamma_AF8,Gamma_TP10,
# RAW_TP9,RAW_AF7,RAW_AF8,RAW_TP10,AUX_RIGHT,
# Mellow,Concentration,
# Accelerometer_X,Accelerometer_Y,Accelerometer_Z,
# Gyro_X,Gyro_Y,Gyro_Z,
# HeadBandOn,
# HSI_TP9,HSI_AF7,HSI_AF8,HSI_TP10,
# Battery,
# Elements


#     dateparse = lambda x: pd.datetime.strptime(x, '%Y-%m-%d %H:%M:%S')
# df = pd.read_csv(infile, parse_dates=['datetime'], date_parser=dateparse)


    muse_EEG_data = pd.read_csv(fname)


    time_df = pd.DataFrame(muse_EEG_data, columns=['TimeStamp'])    
    print("read_eeg_data(): Session Date: ", time_df['TimeStamp'][0])

    raw_df = pd.DataFrame(muse_EEG_data, 
            columns=['RAW_TP9', 'RAW_AF7', 'RAW_AF8', 'RAW_TP10'])    
    delta_df = pd.DataFrame(muse_EEG_data, 
            columns=['Delta_TP9', 'Delta_AF7', 'Delta_AF8', 'Delta_TP10'])    
    theta_df = pd.DataFrame(muse_EEG_data, 
            columns=['Theta_TP9', 'Theta_AF7', 'Theta_AF8', 'Theta_TP10'])    
    alpha_df = pd.DataFrame(muse_EEG_data, 
            columns=['Alpha_TP9', 'Alpha_AF7', 'Alpha_AF8', 'Alpha_TP10'])    
    beta_df = pd.DataFrame(muse_EEG_data, 
            columns=['Beta_TP9', 'Beta_AF7', 'Beta_AF8', 'Beta_TP10'])    
    gamma_df = pd.DataFrame(muse_EEG_data, 
            columns=['Gamma_TP9', 'Gamma_AF7', 'Gamma_AF8', 'Gamma_TP10'])
    

    global EEG_Dict
#     EEG_Dict = {}

    for temp_df in (raw_df, delta_df, theta_df, alpha_df, beta_df, gamma_df):
        if args.verbose:
            print("verbose turned on")

        print("read_eeg_data(): Sensor data description", temp_df.describe())
#         data_str = temp_df.mean()
        data_str = temp_df.describe()
#         print("type", type(data_str))
#         print("data_str.index", data_str.index)
        EEG_Dict.update(data_str.to_dict())
#         print("EEG_Dict: ", EEG_Dict)
#         print("data_str.to_dict()", data_str.to_dict())
    
                      
#     print("SAMPLING_RATE: ", SAMPLING_RATE)
#     print("Filter_Lowcut: ", Filter_Lowcut)
#     print("Filter_Highcut: ", Filter_Highcut)
#     print("filter_order: ", Filter_Order)


    sample_length = len(raw_df['RAW_AF7'])
    sample_time_sec = (sample_length/SAMPLING_RATE)
    sample_time_min = sample_time_sec/60.0

    parms_dict = {
            'Analysis Parameters':{
            "lowcut":Filter_Lowcut, "highcut": Filter_Highcut, "filter_order":Filter_Order, 
                        "sample_length":sample_length, "sample_time_sec":sample_time_sec, 
                        "sample_time_min":sample_time_min}
            }
            
    session_dict = {
        'Session_Data':{
        'session_date': str(time_df['TimeStamp'][0]),
        'date': date_time_now,
        'data_file_fname': fname,
        'mood': 'calm',
        'location': 'home',
        'activity': "sitting",
        'misc': 'This field is for misc. data to be stored in the database'
        },
        'Participants':{ 
            'Meditators':{
                0:{
                    'name': 'Debra',
                    'age': 63,
                    'gender': 'female'
                    },          
                1:{
                    'name': 'Savahn',
                    'age': 38,
                    'gender': 'female'
                    }     
                },
            'Coordinators':{
                0:{
                    'name': 'Patti',
                    'age': 32,
                    'gender': 'female'
                    }
                },
            'Helpers':{
                0:{
                    'name': 'Oni',
                    'age': 23,
                    'gender': 'male'
                    }
                },
            'Participants':{
                0:{
                    'name': 'Shiloh',
                    'age': 34,
                    'gender': 'male'
                    }
                }
            }
        }



#     print('***********  session_dict *****************')
#     print('session_dict:', session_dict)
#     sleep(3)
    
    session_dict.update(EEG_Dict)

#     print('*********** updated EEG_Dict *****************')
#     print('session_dict:', session_dict)
#     sleep(3)


    session_dict.update(parms_dict)

#     print('************* updated parms_dict ***************')
#     print('session_dict:', session_dict)
#     sleep(3)


    session_json = json.dumps(session_dict, sort_keys=True)
#     print(session_json)

    global out_dirname
# Save the session data to a JSON file
    session_data_fname = out_dirname + "/session_data/EEG_session_data-" + date_time_now + ".json"
    
    ensure_dir(out_dirname + "/session_data/")
    data_file=open(session_data_fname,"w+")
#     pwr_data_file=open("EEG_power_data.txt","w+")

    data_file.write(session_json)
    data_file.close()
    

    return(muse_EEG_data, EEG_Dict)




def scale(x, out_range=(-1, 1), axis=None):
    domain = np.min(x, axis), np.max(x, axis)
    y = (x - (domain[1] + domain[0]) / 2) / (domain[1] - domain[0])
    return y * (out_range[1] - out_range[0]) + (out_range[1] + out_range[0]) / 2


def smooth_data(data_in, win):
    # Tail-rolling average transform
    rolling = data_in.rolling(window=win)
    smoothed_data = rolling.mean()

    return smoothed_data



def filter_data(data_in, win):
    N  = 3    # Filter order
    Wn = 0.5 # Cutoff frequency
    B, A = signal.butter(N, Wn, output='ba')
    smoothed_data = signal.filtfilt(B,A, data_in)

    return smoothed_data


def butter_bandpass(lowcut, highcut, fs, order=5):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
#     print("butter_bandpass: ", low, high, nyq)
    b, a = butter(order, [low, high], btype='band')
    return b, a

def butter_bandpass_filter(data, lowcut, highcut, fs, order=5):
#     print("butter_bandpass_filter: ", lowcut, highcut, fs, order)
    b, a = butter_bandpass(lowcut, highcut, fs, order=order)
    y = lfilter(b, a, data)
    return y



#  *************************************

def plot_coherence(x, y, a, b, title, data_fname, plot_fname, date_time_now, analysis_parms):

    print('plot_coherence() called')

    fig = plt.figure(num=41, figsize=(FIGURE_SIZE), dpi=PLOT_DPI, facecolor='w', edgecolor='k')

    params = {
        'axes.titlesize' : 12,
        'axes.labelsize' : 8,
        'lines.linewidth' : 1,
        'lines.markersize' : 8,
        'xtick.labelsize' : 8,
        'ytick.labelsize' : 8,
        'legend.fontsize': 7,
        'legend.handlelength': 2}
    plt.rcParams.update(params)


#     plt.axis([0, len(af7), 0, len(af8)])

#     x1 = np.linspace(0.0, 50.0)
#     y1 = np.linspace(0.0, 20.0)

#     plt.axis(xlim=(-50, 50), ylim=(-50, 50), option='scaled')
#     plt.axis(xlim=(-x1, x1), ylim=(-y1, y1), option='scaled')

#     plt.axis(option='auto')
    
#     ax.set(xlim=(xmin, xmax), ylim=(ymin, ymax))
    plt_axes = plt.gca()
#     plt_axes.set_xlim([0, len(x)])
#     plt_axes.set_ylim([-1000, 1000])

#     print("plt_axes ", plt_axes)
    
    plt.scatter(x, y, s=1, color='r', alpha=0.7, label='AF7/AF8')
    plt.scatter(a, b, s=1, color='g', alpha=0.7, label='TP9/TP10')
#     plt.plot(x, s=1, color='r', label='AF7')
#     plt.plot(y, s=1, color='g', label='AF8')
    
#     plt.plot(x, color='c', alpha=0.3, label='1')
#     plt.plot(y, color='b', alpha=0.3, label='2')

    
    plt.xlabel('Amp uV')
    plt.ylabel('Amp uV')
    # plt.hlines([-a, a], 0, T, linestyles='--')
    plt.grid(True)
    plt.axis('auto')
    plt.suptitle('Algorithmic Biofeedback Control System', fontsize=12, fontweight='bold')
    plt.title(title)
    plt.legend(loc='upper left')

    plt.text(0.15, 1.03, 'Session Date: ' + session_dict['Session_Data']['session_date'], 
            transform=plt_axes.transAxes, style='italic', fontsize=6, horizontalalignment='right',
            bbox={'facecolor':'blue', 'alpha':0.1, 'pad':4})

    create_analysis_parms_text(0.76, 1.01, plt_axes, analysis_parms)    
    basename = os.path.basename(data_fname)
#     create_file_date_text(-0.12, -0.11, 0.9, -0.11, plt_axes, basename, date_time_now)
    create_file_date_text(-0.1, -0.055, -0.1, -0.15, plt_axes, basename, date_time_now)
         
#     plt.text(-0.12, -0.11, "file: " + data_fname, 
#         transform=plt_axes.transAxes, fontsize=5, style='italic',
#         bbox={'facecolor':'blue', 'alpha':0.1, 'pad':4})
# 
#     plt.text(0.9, -0.11, "Date: " + date_time_now, 
#         transform=plt_axes.transAxes, fontsize=5, style='italic',
#         bbox={'facecolor':'blue', 'alpha':0.1, 'pad':4})
         

# ax.text(left, bottom, 'left top',
# horizontalalignment='left',
# verticalalignment='top',
# transform=ax.transAxes)

        
    plt.savefig(plot_fname, dpi=300)

#     if (args.display_plots or gui_dict['checkBoxInteractive']):
#     if (args.display_plots):
    if (gui_dict['checkBoxInteractive']):
        plt.show()

    plt.close()
    print("Finished writing EEG EF7 & EF8 Integrated Data - Coherance plot")
    print(plot_fname)
    print





#  *************************************

def plot_sensor_data(timestamps, tp9, af7, af8, tp10, data_fname, plot_fname, date_time_now, 
                        title, data_stats, analysis_parms):

    global session_dict
    
    print('plot_sensor_data() called')
#     print('plot_sensor_data() data_stats: ', data_stats)

    t_len = len(timestamps)

#     print('plot_sensor_data() t_len: ', t_len)
    
    period = (1.0/SAMPLING_RATE)
    x_series = np.arange(0, t_len * period, period)
 
#     print('plot_sensor_data() x_series: ', x_series)

    fig, axs = plt.subplots(nrows=5, num=11, figsize=FIGURE_SIZE, 
                    dpi=PLOT_DPI, facecolor='w', edgecolor='k', sharex=True, sharey=True, 
                        gridspec_kw={'hspace': 0.25}, tight_layout=False)
    
    
    plt.suptitle('Algorithmic Biofeedback Control System', fontsize=12, fontweight='bold')
    params = {
        'axes.titlesize' : 12,
        'axes.labelsize' : 8,
        'lines.linewidth' : 1,
        'lines.markersize' : 8,
        'xtick.labelsize' : 8,
        'ytick.labelsize' : 8,
        'legend.fontsize': 7,
        'legend.handlelength': 2}
    plt.rcParams.update(params)

#     plt.title("EEG Data")
                
    plt_axes = plt.gca()


#     data_stats = (EEG_Dict['RAW_AF7']['25%'], EEG_Dict['RAW_AF7']['75%'],
#                 EEG_Dict['RAW_AF8']['25%'], EEG_Dict['RAW_AF8']['75%'],
#                 EEG_Dict['RAW_TP9']['25%'], EEG_Dict['RAW_TP9']['75%'],
#                 EEG_Dict['RAW_TP10']['25%'], EEG_Dict['RAW_TP10']['75%'])
 
#     plt_axes.set_ylim([data_stats[0], data_stats[1]])

    data_min = np.min((data_stats[0], data_stats[2], data_stats[4], data_stats[6]))
    data_max = np.max((data_stats[1], data_stats[3], data_stats[5], data_stats[7]))
    
    print('plot_sensor_data() data_stats: ', data_stats)
    print('plot_sensor_data() data_min: ', data_min)
    print('plot_sensor_data() data_max: ', data_max)


    plt_axes.set_ylim(data_min - 100, data_max + 100)
 
    pt_size = 2

#     axs[0].scatter(x_series, tp9, alpha=0.7, s=pt_size, color=MM_Colors['RawTP9'], label='TP9')
#     axs[0].scatter(x_series, af7, alpha=0.7, s=pt_size, color=MM_Colors['RawAF7'], label='AF7')
#     axs[0].scatter(x_series, af8, alpha=0.7, s=pt_size, color=MM_Colors['RawAF8'], label='AF8')
#     axs[0].scatter(x_series, tp10, alpha=0.7, s=pt_size, color=MM_Colors['RawTP10'], label='TP10')

    axs[0].plot(x_series, tp9, alpha=0.8, ms=pt_size, color=MM_Colors['RawTP9'], label='TP9')
    axs[0].plot(x_series, af7, alpha=0.8, ms=pt_size, color=MM_Colors['RawAF7'], label='AF7')
    axs[0].plot(x_series, af8, alpha=0.8, ms=pt_size, color=MM_Colors['RawAF8'], label='AF8')
    axs[0].plot(x_series, tp10, alpha=0.8, ms=pt_size, color=MM_Colors['RawTP10'], label='TP10')
  
    axs[0].xaxis.set_major_locator(ticker.MultipleLocator(SAMPLING_RATE))
    axs[0].xaxis.set_minor_locator(ticker.MultipleLocator(SAMPLING_RATE/10))
#     axs[0].text(0.0, 0.1, "MultipleLocator(0.5)", fontsize=6,
#             transform=axs[0].transAxes)
        
#     plt.xlabel('Time (Seconds)')
#     plt.ylabel('Amp uv')

    axs[0].set(title=title, ylabel="Amp uV") 

#     axs[0].axis('auto')
#     axs[0].grid(True)
      
    axs[0].text(0.95, 0.025, '(All Sensor Data Combined)',
        verticalalignment='bottom', horizontalalignment='right',
        transform=axs[0].transAxes, color='green', fontsize=5) 
       
    axs[0].text(0.2, 1.1, 'Session Date: ' + session_dict['Session_Data']['session_date'], 
            transform=axs[0].transAxes, style='italic', fontsize=6, horizontalalignment='right',
            bbox={'facecolor':'blue', 'alpha':0.1, 'pad':4})

    create_analysis_parms_text(0.75, 1.1, axs[0], analysis_parms)    
            
#     axs[0].annotate('Notable Data Point', xy=([data_stats[0], data_stats[1]]), 
#                             xytext=([data_stats[2], data_stats[3]]),
#             arrowprops=dict(facecolor='black', shrink=0.01))
            

    axs[1].plot(x_series, tp9, alpha=1.0, ms=pt_size, color=MM_Colors['RawTP9'], label='TP9')
    axs[1].set(ylabel="Amp uV") 
    axs[2].plot(x_series, af7, alpha=1.0, ms=pt_size, color=MM_Colors['RawAF7'], label='AF7')
    axs[2].set(ylabel="Amp uV") 
    axs[3].plot(x_series, af8, alpha=1.0, ms=pt_size, color=MM_Colors['RawAF8'], label='AF8')
    axs[3].set(ylabel="Amp uV") 
    axs[4].plot(x_series, tp10, alpha=1.0, ms=pt_size, color=MM_Colors['RawTP10'], label='TP10')
    axs[4].set(xlabel="Time (Seconds)", ylabel="Amp uV") 

       
    for tmp_ax in axs:
            tmp_ax.grid(True)
            tmp_ax.legend(loc='upper left')

    basename = os.path.basename(data_fname)
    create_file_date_text(-0.1, -0.7, -0.1, -0.4, axs[4], basename, date_time_now)
    
#     plt.axis('tight')

    plt.savefig(plot_fname, dpi=300)
   
    if (args.display_plots or gui_dict['checkBoxInteractive']):
#     if args.display_plots:
        plt.show()
  
    plt.close()
    print("Finished writing sensor data plot ")
    print(plot_fname)
    print




  




def plot_all_power_bands(delta, theta, alpha, beta, gamma,
                lowcut, highcut, fs, point_sz, title, 
                data_fname, plot_fname, date_time_now, analysis_parms):


# TODO:  Make multiple windows

    plot_alpha = 0.8

    print('plot_all_power_bands() called')

#     x1 = np.arange(0.0, len(delta))
#     x2 = np.arange(0.0, len(theta))
#     x3 = np.arange(0.0, len(alpha))
#     x4 = np.arange(0.0, len(beta))
#     x5 = np.arange(0.0, len(gamma))

    gamma_mean = np.mean(np.nan_to_num(gamma))
    gamma_std = np.std(np.nan_to_num(gamma))
    gamma_max = np.max(np.nan_to_num(gamma))
    gamma_min = np.min(np.nan_to_num(gamma))

    print("gamma_mean: ", gamma_mean)
    print("gamma_std: ", gamma_std)
    print("gamma_max: ", gamma_max)
    print("gamma_min: ", gamma_min)
    
    beta_mean = np.mean(np.nan_to_num(beta))
    beta_std = np.std(np.nan_to_num(beta))
    beta_max = np.max(np.nan_to_num(beta))
    beta_min = np.min(np.nan_to_num(beta))

    print("beta_mean: ", beta_mean)
    print("beta_std: ", beta_std)
    print("beta_max: ", beta_max)
    print("beta_min: ", beta_min)

    alpha_mean = np.mean(np.nan_to_num(alpha))
    alpha_std = np.std(np.nan_to_num(alpha))
    alpha_max = np.max(np.nan_to_num(alpha))
    alpha_min = np.min(np.nan_to_num(alpha))

    print("alpha_mean: ", alpha_mean)
    print("alpha_std: ", alpha_std)
    print("alpha_max: ", alpha_max)
    print("alpha_min: ", alpha_min)

    theta_mean = np.mean(np.nan_to_num(theta))
    theta_std = np.std(np.nan_to_num(theta))
    theta_max = np.max(np.nan_to_num(theta))
    theta_min = np.min(np.nan_to_num(theta))

    print("theta_mean: ", theta_mean)
    print("theta_std: ", theta_std)
    print("theta_max: ", theta_max)
    print("theta_min: ", theta_min)

    delta_mean = np.mean(np.nan_to_num(delta))
    delta_std = np.std(np.nan_to_num(delta))
    delta_max = np.max(np.nan_to_num(delta))
    delta_min = np.min(np.nan_to_num(delta))

    print("delta_mean: ", delta_mean)
    print("delta_std: ", delta_std)
    print("delta_max: ", delta_max)
    print("delta_min: ", delta_min)


    fig, axs = plt.subplots(num=27, nrows=5, figsize=(FIGURE_SIZE), 
                            sharex=True, sharey=True, gridspec_kw={'hspace': 0})

#     fig.subplots_adjust(top=0.85)

    plt_axes = plt.gca()
#     plt.axis('auto')

    xmin, xmax, ymin, ymax = plt.axis()

    print("xmin: ", xmin)
    print("xmax: ", xmax)
    print("ymin: ", ymin)
    print("ymax: ", ymax)

    t_len = len(delta)
    period = (1.0/SAMPLING_RATE)
    x_series = np.arange(0, t_len * period, period)



# MM_Colors = {
# 'RawTP9': '#cc0000',
# 'RawAF7': '#cc98e5',
# 'RawAF8': '#7fcce5',
# 'RawTP10': '#b2cc7f',
# 'Delta': '#d42727',
# 'Theta': '#9933cc',
# 'Alpha': '#0d90cc',
# 'Beta':  '#669900',
# 'Gamma': '#ff900c'
# }



    l0 = axs[0].plot(x_series, gamma,  ms=1, color=MM_Colors['Gamma'], alpha=plot_alpha
 , label='Gamma')
    axs[0].legend(loc='upper right', prop={'size': 6})     
    axs[0].grid(True)
#     axs[0].hlines([-a, a], 0, T, linestyles='--')

    l1 = axs[1].plot(x_series, beta,  ms=1, color=MM_Colors['Beta'], alpha=plot_alpha
 , label='Beta')
    axs[1].legend(loc='upper right', prop={'size': 6})
    axs[1].grid(True)
#     axs[1].hlines([-a, a], 0, T, linestyles='--')

    l2 = axs[2].plot(x_series, alpha,  ms=1, color=MM_Colors['Alpha'], alpha=plot_alpha
 , label='Alpha')
    axs[2].legend(loc='upper right', prop={'size': 6})
    axs[2].grid(True)
#     axs[2].hlines([-a, a], 0, T, linestyles='--')

    l3 = axs[3].plot(x_series, theta,  ms=1, color=MM_Colors['Theta'], alpha=plot_alpha
 , label='Theta')
    axs[3].legend(loc='upper right', prop={'size': 6})
    axs[3].grid(True)
#     axs[3].hlines([-a, a], 0, T, linestyles='--')

    l4 = axs[4].plot(x_series, delta,  ms=1, color=MM_Colors['Delta'], alpha=plot_alpha
 , label='Delta')
    axs[4].legend(loc='upper right', prop={'size': 6})
    axs[4].grid(True)
#     axs[4].hlines([-a, a], 0, T, linestyles='--')

#     fig.legend((l0, l1, l2, l3, l4), ('gamma', 'beta', 'alpha', 'theta', 'delta'), 'upper left')
#     fig.legend((l0, l1), ('gamma', 'beta'), 'upper left')
#     fig.legend((l2, l3), ('alpha', 'theta'), 'upper right')

    fig.suptitle('Algorithmic Biofeedback Control System', fontsize=12, fontweight='bold')


    # Hide x labels and tick labels for all but bottom plot.
#     for ax in axs:
#         ax.label_outer()

#     plt.title(title)

    plt.text(0.3, 5.15, title, 
        transform=plt_axes.transAxes, fontsize=8, style='italic',
        bbox={'facecolor':'blue', 'alpha':0.1, 'pad':4})

     
    plt.text(0.01, 4.75, 
        'Mean: ' + "{:.3f}".format(gamma_mean) + 
        ' Std: ' + "{:.3f}".format(gamma_std) + 
        '\nMin: ' + "{:.3f}".format(gamma_min) +
        ' Max: ' + "{:.3f}".format(gamma_max), style='italic', 
        transform=plt_axes.transAxes, fontsize=5, 
        bbox={'facecolor': 'blue', 'alpha': 0.05, 'pad': 2})

    plt.text(0.01, 3.75, 
        'Mean: ' + "{:.3f}".format(beta_mean) + 
        ' Std: ' + "{:.3f}".format(beta_std) +
        '\nMin: ' + "{:.3f}".format(beta_min) +
        ' Max: ' + "{:.3f}".format(beta_max), style='italic', 
        transform=plt_axes.transAxes, fontsize=5, 
        bbox={'facecolor': 'blue', 'alpha': 0.05, 'pad': 2})
        
    plt.text(0.01, 2.75, 
        'Mean: ' + "{:.3f}".format(alpha_mean) + 
        ' Std: ' + "{:.3f}".format(alpha_std) +
        '\nMin: ' + "{:.3f}".format(alpha_min) +
        ' Max: ' + "{:.3f}".format(alpha_max), style='italic', 
        
        transform=plt_axes.transAxes, fontsize=5, 
        bbox={'facecolor': 'blue', 'alpha': 0.05, 'pad': 2})
        
    plt.text(0.01, 1.75, 
        'Mean: ' + "{:.3f}".format(theta_mean) + 
        ' Std: ' + "{:.3f}".format(theta_std) +
        '\nMin: ' + "{:.3f}".format(theta_min) +
        ' Max: ' + "{:.3f}".format(theta_max), style='italic', 
        transform=plt_axes.transAxes, fontsize=5, 
        bbox={'facecolor': 'blue', 'alpha': 0.05, 'pad': 2})
        
    plt.text(0.01, 0.75, 
        'Mean: ' + "{:.3f}".format(delta_mean) + 
        ' Std: ' + "{:.3f}".format(delta_std) + 
        '\nMin: ' + "{:.3f}".format(delta_min) +
        ' Max: ' + "{:.3f}".format(delta_max), style='italic', 
        transform=plt_axes.transAxes, fontsize=5, 
        bbox={'facecolor': 'blue', 'alpha': 0.05, 'pad': 2})

    create_analysis_parms_text(0.7, 5.07, plt_axes, analysis_parms)    
    basename = os.path.basename(data_fname)
    create_file_date_text(-0.12, -0.5, 0.9, -0.5, plt_axes, basename, date_time_now)

    
#     plt.legend(loc='upper left')

    plt.savefig(plot_fname, dpi=300)

    if (args.display_plots or gui_dict['checkBoxInteractive']):
#     if args.display_plots:
        plt.show()

    plt.close()

    print("Finished writing " + title + " data plot ")
    print(plot_fname)
    print




# *****************************************

def plot_combined_power_bands(delta_raw, theta_raw, alpha_raw, beta_raw, gamma_raw,
                delta, theta, alpha, beta, gamma,
                lowcut, highcut, fs, point_sz, title, 
                data_fname, plot_fname, date_time_now, analysis_parms):


# TODO:  Make multiple windows correctly

    print('plot_combined_power_bands() called')

    plot_alpha = 0.8

#     x1 = np.arange(0.0, len(delta))
#     x2 = np.arange(0.0, len(theta))
#     x3 = np.arange(0.0, len(alpha))
#     x4 = np.arange(0.0, len(beta))
#     x5 = np.arange(0.0, len(gamma))

    gamma_mean = np.mean(np.nan_to_num(gamma))
    gamma_std = np.std(np.nan_to_num(gamma))
    gamma_max = np.max(np.nan_to_num(gamma))
    gamma_min = np.min(np.nan_to_num(gamma))
    
    beta_mean = np.mean(np.nan_to_num(beta))
    beta_std = np.std(np.nan_to_num(beta))
    beta_max = np.max(np.nan_to_num(beta))
    beta_min = np.min(np.nan_to_num(beta))

    alpha_mean = np.mean(np.nan_to_num(alpha))
    alpha_std = np.std(np.nan_to_num(alpha))
    alpha_max = np.max(np.nan_to_num(alpha))
    alpha_min = np.min(np.nan_to_num(alpha))

    theta_mean = np.mean(np.nan_to_num(theta))
    theta_std = np.std(np.nan_to_num(theta))
    theta_max = np.max(np.nan_to_num(theta))
    theta_min = np.min(np.nan_to_num(theta))

    delta_mean = np.mean(np.nan_to_num(delta))
    delta_std = np.std(np.nan_to_num(delta))
    delta_max = np.max(np.nan_to_num(delta))
    delta_min = np.min(np.nan_to_num(delta))

    
    fig, axs = plt.subplots(5, num=11, figsize=(FIGURE_SIZE), 
                sharex=True, sharey=True, gridspec_kw={'hspace': 0})

#     fig.subplots_adjust(top=0.85)

#     plt.hlines([-a, a], 0, T, linestyles='--')
#     plt.grid(True)

    plt_axes = plt.gca()
    plt.axis('auto')
#     xmin, xmax, ymin, ymax = plt.axis()

#     print("xmin: ", xmin)
#     print("xmax: ", xmax)
#     print("ymin: ", ymin)
#     print("ymax: ", ymax)


    y_limits = [gamma_min, gamma_max]
  
      
#     plt.xlabel('X Axis', axes=ax)
#     plt.ylabel('Y Axis', axes=ax)

#     plt.plot(tp10_delta_int, color='c', alpha=0.3, label='TP10 ')
#     plt.scatter(x_axis, tp9_delta_int, s=point_sz, color='b', alpha=1.0)


# MM_Colors = {
# 'RawTP9': '#cc0000',
# 'RawAF7': '#cc98e5',
# 'RawAF8': '#7fcce5',
# 'RawTP10': '#b2cc7f',
# 'Delta': '#d42727',
# 'Theta': '#9933cc',
# 'Alpha': '#0d90cc',
# 'Beta':  '#669900',
# 'Gamma': '#ff900c'
# }


    t_len = len(delta)
    period = (1.0/SAMPLING_RATE)
    x_series = np.arange(0, t_len * period, period)


    l0 = axs[0].plot(x_series, gamma_raw, ms=1, color=MM_Colors['Gamma'], 
                alpha=plot_alpha, label='Gamma Raw')
    l00 = axs[0].scatter(x_series, gamma, s=1, color=MM_Colors['Gamma'], 
                alpha=plot_alpha, label='Gamma')
    axs[0].legend(loc='upper right', prop={'size': 6})     
    axs[0].grid(True)
#     axs[0].set_xlim([0,2])
    axs[0].set_ylim(y_limits)
    
#     axs[0].hlines([-a, a], 0, T, linestyles='--')

    l1 = axs[1].plot(x_series, beta_raw, ms=1, color=MM_Colors['Beta'], 
        alpha=plot_alpha, label='Beta Raw')
    l11 = axs[1].scatter(x_series, beta, s=1, color=MM_Colors['Beta'], 
        alpha=plot_alpha, label='Beta')
    axs[1].legend(loc='upper right', prop={'size': 6})
    axs[1].grid(True)
    axs[1].set_ylim(y_limits)
#     axs[1].hlines([-a, a], 0, T, linestyles='--')

    l2 = axs[2].plot(x_series, alpha_raw, ms=1, color=MM_Colors['Alpha'], 
        alpha=plot_alpha, label='Alpha Raw')
    l22 = axs[2].scatter(x_series, alpha, s=1, color=MM_Colors['Alpha'], 
        alpha=plot_alpha, label='Alpha')
    axs[2].legend(loc='upper right', prop={'size': 6})
    axs[2].grid(True)
    axs[2].set_ylim(y_limits)    
#     axs[2].hlines([-a, a], 0, T, linestyles='--')

    l3 = axs[3].plot(x_series, theta_raw, ms=1, color=MM_Colors['Theta'], 
        alpha=plot_alpha, label='Theta Raw')
    l33 = axs[3].scatter(x_series, theta, s=1, color=MM_Colors['Theta'], 
        alpha=plot_alpha, label='Theta')
    axs[3].legend(loc='upper right', prop={'size': 6})
    axs[3].grid(True)
    axs[3].set_ylim(y_limits)
#     axs[3].hlines([-a, a], 0, T, linestyles='--')

    l4 = axs[4].plot(x_series, delta_raw, ms=1, color=MM_Colors['Delta'], 
        alpha=plot_alpha, label='Delta Raw')
    l44 = axs[4].scatter(x_series, delta, s=1, color=MM_Colors['Delta'], 
        alpha=plot_alpha, label='Delta')
    axs[4].legend(loc='upper right', prop={'size': 6})
    axs[4].grid(True)
    axs[4].set_ylim(y_limits)
#     axs[4].hlines([-a, a], 0, T, linestyles='--')


    fig.suptitle('Algorithmic Biofeedback Control System', fontsize=12, fontweight='bold')

    # Hide x labels and tick labels for all but bottom plot.
#     for ax in axs:
#         ax.label_outer()


#     plt.title(title)

    plt.text(0.3, 5.15, title, 
        transform=plt_axes.transAxes, fontsize=8, style='italic',
        bbox={'facecolor':'blue', 'alpha':0.1, 'pad':4})

     
    plt.text(0.01, 4.75, 
        'Mean: ' + "{:.3f}".format(gamma_mean) + 
        ' Std: ' + "{:.3f}".format(gamma_std) + 
        '\nMin: ' + "{:.3f}".format(gamma_min) +
        ' Max: ' + "{:.3f}".format(gamma_max), style='italic', 
        transform=plt_axes.transAxes, fontsize=5, 
        bbox={'facecolor': 'blue', 'alpha': 0.05, 'pad': 2})

    plt.text(0.01, 3.75, 
        'Mean: ' + "{:.3f}".format(beta_mean) + 
        ' Std: ' + "{:.3f}".format(beta_std) +
        '\nMin: ' + "{:.3f}".format(beta_min) +
        ' Max: ' + "{:.3f}".format(beta_max), style='italic', 
        transform=plt_axes.transAxes, fontsize=5, 
        bbox={'facecolor': 'blue', 'alpha': 0.05, 'pad': 2})
        
    plt.text(0.01, 2.75, 
        'Mean: ' + "{:.3f}".format(alpha_mean) + 
        ' Std: ' + "{:.3f}".format(alpha_std) +
        '\nMin: ' + "{:.3f}".format(alpha_min) +
        ' Max: ' + "{:.3f}".format(alpha_max), style='italic', 
        
        transform=plt_axes.transAxes, fontsize=5, 
        bbox={'facecolor': 'blue', 'alpha': 0.05, 'pad': 2})
        
    plt.text(0.01, 1.75, 
        'Mean: ' + "{:.3f}".format(theta_mean) + 
        ' Std: ' + "{:.3f}".format(theta_std) +
        '\nMin: ' + "{:.3f}".format(theta_min) +
        ' Max: ' + "{:.3f}".format(theta_max), style='italic', 
        transform=plt_axes.transAxes, fontsize=5, 
        bbox={'facecolor': 'blue', 'alpha': 0.05, 'pad': 2})
        
    plt.text(0.01, 0.75, 
        'Mean: ' + "{:.3f}".format(delta_mean) + 
        ' Std: ' + "{:.3f}".format(delta_std) + 
        '\nMin: ' + "{:.3f}".format(delta_min) +
        ' Max: ' + "{:.3f}".format(delta_max), style='italic', 
        transform=plt_axes.transAxes, fontsize=5, 
        bbox={'facecolor': 'blue', 'alpha': 0.05, 'pad': 2})

    plt.axis('auto')

    create_analysis_parms_text(0.75, 5.07, plt_axes, analysis_parms)
    basename = os.path.basename(data_fname)
    create_file_date_text(-0.12, -0.5, 0.9, -0.5, plt_axes, basename, date_time_now)


#     plt.legend(loc='upper left')
#     fname = 'eeg_semilog_bandpass_data.jpg'       

    plt.savefig(plot_fname, dpi=300)

    if (args.display_plots or gui_dict['checkBoxInteractive']):
#     if args.display_plots:
        plt.show()

    plt.close()

    print("Finished writing " + title + " data plot ")
    print(plot_fname)
    print





def plot_mellow_concentration(mellow, concentration,
                lowcut, highcut, fs, point_sz, title, 
                data_fname, plot_fname, date_time_now, analysis_parms):


    plot_alpha = 0.8

    print('plot_mellow_concentration() called')

#     x1 = np.arange(0.0, len(delta))
#     x2 = np.arange(0.0, len(theta))
#     x3 = np.arange(0.0, len(alpha))
#     x4 = np.arange(0.0, len(beta))
#     x5 = np.arange(0.0, len(gamma))

    mellow_mean = np.mean(np.nan_to_num(mellow))
    mellow_std = np.std(np.nan_to_num(mellow))
    mellow_max = np.max(np.nan_to_num(mellow))
    mellow_min = np.min(np.nan_to_num(mellow))

    print("mellow_mean: ", mellow_mean)
    print("mellow_std: ", mellow_std)
    print("mellow_max: ", mellow_max)
    print("mellow_min: ", mellow_min)
    
    concentration_mean = np.mean(np.nan_to_num(concentration))
    concentration_std = np.std(np.nan_to_num(concentration))
    concentration_max = np.max(np.nan_to_num(concentration))
    concentration_min = np.min(np.nan_to_num(concentration))

    print("concentration_mean: ", concentration_mean)
    print("concentration_std: ", concentration_std)
    print("concentration_max: ", concentration_max)
    print("concentration_min: ", concentration_min)

  
    fig, axs = plt.subplots(num=17, nrows=2, figsize=(FIGURE_SIZE), 
                            sharex=True, sharey=True, gridspec_kw={'hspace': 0})

#     fig.subplots_adjust(top=0.85)

    plt_axes = plt.gca()
#     plt.axis('auto')

    xmin, xmax, ymin, ymax = plt.axis()

#     print("xmin: ", xmin)
#     print("xmax: ", xmax)
#     print("ymin: ", ymin)
#     print("ymax: ", ymax)

    plt_axes.set_ylim(0, 100)

    t_len = len(mellow)
    period = (1.0/SAMPLING_RATE)
    x_series = np.arange(0, t_len * period, period)


# MM_Colors = {
# 'RawTP9': '#cc0000',
# 'RawAF7': '#cc98e5',
# 'RawAF8': '#7fcce5',
# 'RawTP10': '#b2cc7f',
# 'Delta': '#d42727',
# 'Theta': '#9933cc',
# 'Alpha': '#0d90cc',
# 'Beta':  '#669900',
# 'Gamma': '#ff900c'
# }


    l0 = axs[0].plot(x_series, mellow,  ms=1, color='b', alpha=plot_alpha, label='Mellow')
    axs[0].legend(loc='upper right', prop={'size': 6})     
    axs[0].grid(True)
#     axs[0].hlines([-a, a], 0, T, linestyles='--')

    l1 = axs[1].plot(x_series, concentration,  ms=1, color='g', alpha=plot_alpha, label='Concentration')
    axs[1].legend(loc='upper right', prop={'size': 6})
    axs[1].grid(True)

    fig.suptitle('Algorithmic Biofeedback Control System', fontsize=12, fontweight='bold')


    plt.text(0.3, 5.15, title, 
        transform=plt_axes.transAxes, fontsize=8, style='italic',
        bbox={'facecolor':'blue', 'alpha':0.1, 'pad':4})

     
    plt.text(0.01, 4.75, 
        'Mean: ' + "{:.3f}".format(mellow_mean) + 
        ' Std: ' + "{:.3f}".format(mellow_std) + 
        '\nMin: ' + "{:.3f}".format(mellow_min) +
        ' Max: ' + "{:.3f}".format(mellow_max), style='italic', 
        transform=plt_axes.transAxes, fontsize=5, 
        bbox={'facecolor': 'blue', 'alpha': 0.05, 'pad': 2})

    plt.text(0.01, 3.75, 
        'Mean: ' + "{:.3f}".format(concentration_mean) + 
        ' Std: ' + "{:.3f}".format(concentration_std) +
        '\nMin: ' + "{:.3f}".format(concentration_min) +
        ' Max: ' + "{:.3f}".format(concentration_max), style='italic', 
        transform=plt_axes.transAxes, fontsize=5, 
        bbox={'facecolor': 'blue', 'alpha': 0.05, 'pad': 2})
        
    create_analysis_parms_text(0.7, 5.07, plt_axes, analysis_parms)    
    basename = os.path.basename(data_fname)
    create_file_date_text(-0.12, -0.5, 0.9, -0.5, plt_axes, basename, date_time_now)

    
#     plt.legend(loc='upper left')

    plt.savefig(plot_fname, dpi=300)

    if (args.display_plots or gui_dict['checkBoxInteractive']):
#     if args.display_plots:
        plt.show()

    plt.close()

    print("Finished writing " + title + " data plot ")
    print(plot_fname)
    print












def create_file_date_text(x1, y1, x2, y2, plt_axes, data_fname, date_time_now):

    plt.text(x1, y1, "file: " + data_fname, 
        transform=plt_axes.transAxes, fontsize=5, style='italic',
        bbox={'facecolor':'blue', 'alpha':0.1, 'pad':4})

    plt.text(x2, y2, "Date: " + date_time_now, 
        transform=plt_axes.transAxes, fontsize=5, style='italic',
        bbox={'facecolor':'blue', 'alpha':0.1, 'pad':4})



def create_analysis_parms_text(x, y, plt_axes, analysis_parms):

    plt.text(x, y, 
        'Low Cut: ' + "{:.1f}".format(analysis_parms['lowcut']) + " HZ " + 
        ' High Cut: ' + "{:.1f}".format(analysis_parms['highcut']) + " HZ "+ 
        ' Filter Order: ' + "{:.1f}".format(analysis_parms['filter_order']) +
        '\nSample Time: ' + "{:.2f}".format(analysis_parms['sample_time_min']) +
        ' (minutes) ' + "{:.2f}".format(analysis_parms['sample_time_sec']) + " (seconds)" + 
        '\nSample Length: ' + "{:d}".format(analysis_parms['sample_length']),
        style='italic', transform=plt_axes.transAxes, fontsize=5, 
        bbox={'facecolor': 'blue', 'alpha': 0.05, 'pad': 2})






def plot_accel_gryo_data(acc_gyro_df, title, data_fname, plot_fname, date_time_now, analysis_parms):

    print('plot_accel_gryo_data() called')

# ['Accelerometer_X', 'Accelerometer_Y', 'Accelerometer_Z', 'Gyro_X', 'Gyro_Y', 'Gyro_Z']
               
    plot_alpha = 0.8
    
    x_axis = np.arange(len(acc_gyro_df['Accelerometer_X']))

#     plt.figure(num=16, figsize=(FIGURE_SIZE), dpi=PLOT_DPI, facecolor='w', edgecolor='k')

    fig, axs = plt.subplots(6, num=24, figsize=(FIGURE_SIZE), 
                    sharex=True, sharey=True, gridspec_kw={'hspace': 0})
#     fig.subplots_adjust(top=0.85)

    plt_axes = plt.gca()
#     plt.axis('auto')

    plt_axes.set_ylim(-10, 10)
 
    plt.ylabel('Accelerometer/Gyro')
            
    l0 = axs[0].plot(x_axis, acc_gyro_df['Accelerometer_X'], ms=1, color='#00AAFF', 
            alpha=plot_alpha, label='X')
    axs[0].legend(loc='upper right', prop={'size': 6})     
    axs[0].grid(True)

    l1 = axs[1].plot(x_axis, acc_gyro_df['Accelerometer_Y'], ms=1, color='#33FF33', 
            alpha=plot_alpha, label='Y')
    axs[1].legend(loc='upper right', prop={'size': 6})
    axs[1].grid(True)

    l2 = axs[2].plot(x_axis, acc_gyro_df['Accelerometer_Z'], ms=1, color='#FF8800', 
            alpha=plot_alpha, label='Z')
    axs[2].legend(loc='upper right', prop={'size': 6})
    axs[2].grid(True)

    l3 = axs[3].plot(x_axis, acc_gyro_df['Gyro_X'], ms=1, color='#00AAFF', 
            alpha=plot_alpha, label='X')
    axs[3].legend(loc='upper right', prop={'size': 6})     
    axs[3].grid(True)

    l4 = axs[4].plot(x_axis, acc_gyro_df['Gyro_Y'], ms=1, color='#33FF33',
            alpha=plot_alpha, label='Y')
    axs[4].legend(loc='upper right', prop={'size': 6})
    axs[4].grid(True)

    l5 = axs[5].plot(x_axis, acc_gyro_df['Gyro_Z'], ms=1, color='#FF8800', 
            alpha=plot_alpha, label='Z')
    axs[5].legend(loc='upper right', prop={'size': 6})
    axs[5].grid(True)

    plt.suptitle('Algorithmic Biofeedback Control System', fontsize=12, fontweight='bold')
#     plt.title(title)
       
    basename = os.path.basename(data_fname)
    create_file_date_text(-0.1, -0.5, 0.85, -0.5, plt_axes, basename, date_time_now)
    create_analysis_parms_text(0.7, 6.07, plt_axes, analysis_parms)

    plt.savefig(plot_fname, dpi=300)

    if (args.display_plots or gui_dict['checkBoxInteractive']):
#     if args.display_plots:
        plt.show()
 
    plt.close()

    print("Finished writing accel/gyro data plot ")
    print(plot_fname)
    print



   


def pause_and_prompt(pause_time, msg):

    print("Pausing ... " + msg)
    sleep(pause_time)


def ensure_dir(file_path):
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.makedirs(directory)



def generate_plots(muse_EEG_data, data_fname, date_time_now):

    print("Generating plots ", date_time_now)
    print

    ensure_dir(out_dirname + "/plots/")

    df = pd.DataFrame(muse_EEG_data, columns=['TimeStamp', 'RAW_TP9', 'RAW_AF7', 'RAW_AF8', 'RAW_TP10'])    
#     df = np.clip(df, -100.0, 100.0)

    print("SAMPLING_RATE: ", SAMPLING_RATE)
    print("Filter_Lowcut: ", Filter_Lowcut)
    print("Filter_Highcut: ", Filter_Highcut)
    print("Filter_Order: ", Filter_Order)


    sample_length = len(df['RAW_AF7'])
    sample_time_sec = (sample_length/SAMPLING_RATE)
    sample_time_min = sample_time_sec/60.0

    print("sample_length: ", sample_length)
    print("sample_time_sec: ", sample_time_sec)
    print("sample_time_min: ", sample_time_min)
    print

    
    analysis_parms = {"lowcut":Filter_Lowcut, 
                        "highcut": Filter_Highcut, "filter_order":Filter_Order, 
                        "sample_length":sample_length, "sample_time_sec":sample_time_sec, 
                        "sample_time_min":sample_time_min}


    point_sz = 1                    

    # Generate plots 

    print("generate_plots() - EEG_Dict['RAW_TP9']: ", EEG_Dict['RAW_TP9'])
    print("generate_plots() - EEG_Dict['RAW_TP9']: ", 
                EEG_Dict['RAW_TP9']['25%'], EEG_Dict['RAW_TP9']['75%'])


    data_stats = (EEG_Dict['RAW_AF7']['25%'], EEG_Dict['RAW_AF7']['75%'],
                EEG_Dict['RAW_AF8']['25%'], EEG_Dict['RAW_AF8']['75%'],
                EEG_Dict['RAW_TP9']['25%'], EEG_Dict['RAW_TP9']['75%'],
                EEG_Dict['RAW_TP10']['25%'], EEG_Dict['RAW_TP10']['75%'])
    
    
    plot_sensor_data(df['TimeStamp'], df['RAW_TP9'], df['RAW_AF7'], 
                        df['RAW_AF8'], df['RAW_TP10'], data_fname, 
         out_dirname + '/plots/2-ABCS_eeg_raw_' + date_time_now + '.jpg',
        date_time_now,  "Raw EEG", data_stats, analysis_parms)

    
    smooth_sz = 25

    plot_sensor_data(df['TimeStamp'], smooth_data(df['RAW_TP9'], smooth_sz), 
                        smooth_data(df['RAW_AF7'], smooth_sz), 
                        smooth_data(df['RAW_AF8'], smooth_sz), 
                        smooth_data(df['RAW_TP10'], smooth_sz), 
                        data_fname, 
         out_dirname + '/plots/2-ABCS_eeg_smoothed_' + date_time_now + '.jpg',
        date_time_now,  "Smoothed EEG", data_stats, analysis_parms)



# TODO fix filtering (Add resampling) 
    if False:
        plot_sensor_data(df['TimeStamp'], filter_data(df['RAW_TP9'], smooth_sz), 
                            filter_data(df['RAW_AF7'], smooth_sz), 
                            filter_data(df['RAW_AF8'], smooth_sz), 
                            filter_data(df['RAW_TP10'], smooth_sz), 
                            data_fname, 
             out_dirname + '/plots/2-ABCS_eeg_filtered_' + date_time_now + '.jpg',
            date_time_now,  "Filtered EEG", data_stats, analysis_parms)


    if False:
        plot_sensor_data(df['TimeStamp'], butter_bandpass_filter(df['RAW_TP9'], 
                            Filter_Lowcut, Filter_Highcut, SAMPLING_RATE, Filter_Order), 
                            butter_bandpass_filter(df['RAW_AF7'],
                            Filter_Lowcut, Filter_Highcut, SAMPLING_RATE, Filter_Order), 
                            butter_bandpass_filter(df['RAW_AF8'], 
                            Filter_Lowcut, Filter_Highcut, SAMPLING_RATE, Filter_Order), 
                            butter_bandpass_filter(df['RAW_TP10'], 
                            Filter_Lowcut, Filter_Highcut, SAMPLING_RATE, Filter_Order), 
                            data_fname, 
             out_dirname + '/plots/2-ABCS_eeg_bandpass_filtered_' + date_time_now + '.jpg',
            date_time_now,  "Filtered (Bandpass) EEG", data_stats, analysis_parms)




#    data_stats = (EEG_Dict['RAW_TP9']['25%'], EEG_Dict['RAW_TP9']['75%'])
#     plot_sensor_data(df['RAW_TP9'], df['RAW_TP10'], data_fname, 
#         out_dirname + '/plots/2-ABCS_eeg_TP9_TP10_time_series_data_' + date_time_now + '.jpg',
#         date_time_now,  "RAW_AF7 & RAW_AF8", data_stats, analysis_parms)
 
                
                
    if (gui_dict['checkBoxCoherence']):

        plot_coherence(df['RAW_AF7'], df['RAW_AF8'], df['RAW_TP9'], df['RAW_TP10'],
            "EF7 & EF8 Raw Data - Coherance", data_fname,
             out_dirname + '/plots/1-ABCS_eeg_raw_coherence_data_' + date_time_now + '.jpg', 
             date_time_now, analysis_parms)



    if False:
#         if args.plot_3D:

        filt_d = {'FILT_AF7': af7_filt_band, 'FILT_AF8': af8_filt_band, 
                    'FILT_TP9': tp9_filt_band, 'FILT_TP10': tp10_filt_band}

#         filt_df = DataFrame([data, index, columns, dtype, copy])
        filt_df = pd.DataFrame(filt_d, dtype=np.float64)

        pause_and_prompt(0.1, "Plotting 3D")

        plot_3D(muse_EEG_data, filt_df, data_fname,
             out_dirname + '/plots/77-ABCS_3D_' + date_time_now + '.jpg', 
             date_time_now, analysis_parms)

        
        

# Delta_TP9,Delta_AF7,Delta_AF8,Delta_TP10,
# Theta_TP9,Theta_AF7,Theta_AF8,Theta_TP10,
# Alpha_TP9,Alpha_AF7,Alpha_AF8,Alpha_TP10,
# Beta_TP9,Beta_AF7,Beta_AF8,Beta_TP10,
# Gamma_TP9,Gamma_AF7,Gamma_AF8,Gamma_TP10,
# RAW_TP9,RAW_AF7,RAW_AF8,RAW_TP10,AUX_RIGHT,
# Mellow,Concentration,


    if (gui_dict['checkBoxPowerBands']):

#         raw_df = pd.DataFrame(muse_EEG_data, 
#             columns=['RAW_TP9', 'RAW_AF7', 'RAW_AF8', 'RAW_TP10'])    
    #     df = np.clip(df, -1.0, 1.0)

    #     print("Data description\n", raw_df.describe())                    

        delta_df = pd.DataFrame(muse_EEG_data, 
            columns=['Delta_TP9', 'Delta_AF7', 'Delta_AF8', 'Delta_TP10'])    
    #     print("Data description\n", delta_df.describe())                    
        theta_df = pd.DataFrame(muse_EEG_data, 
            columns=['Theta_TP9', 'Theta_AF7', 'Theta_AF8', 'Theta_TP10'])    
    #     print("Data description\n", theta_df.describe())                    
        alpha_df = pd.DataFrame(muse_EEG_data, 
            columns=['Alpha_TP9', 'Alpha_AF7', 'Alpha_AF8', 'Alpha_TP10'])    
    #     print("Data description\n", alpha_df.describe())                    
        beta_df = pd.DataFrame(muse_EEG_data, 
            columns=['Beta_TP9', 'Beta_AF7', 'Beta_AF8', 'Beta_TP10'])    
    #     print("Data description\n", beta_df.describe())                    
        gamma_df = pd.DataFrame(muse_EEG_data, 
            columns=['Gamma_TP9', 'Gamma_AF7', 'Gamma_AF8', 'Gamma_TP10'])    
    #     print("Data description\n", gamma_df.describe())                    



    #     all_delta = (delta_df['Delta_TP9'] + delta_df['Delta_AF7'] + 
    #                 delta_df['Delta_AF8'] + delta_df['Delta_TP10']) / 4.0
    
        # Row mean of the dataframe
    #     print("***************************")
    #     print(delta_df.mean(axis=1))
    #     print("***************************")
    #     print(theta_df.mean(axis=1))
    #     print("***************************")
    #     print(alpha_df.mean(axis=1))
    #     print("***************************")
    #     print(beta_df.mean(axis=1))
    #     print("***************************")
    #     print(gamma_df.mean(axis=1))
    #     print("***************************")


        plot_all_power_bands(delta_df, theta_df, 
                    alpha_df, beta_df, gamma_df,
                    Filter_Lowcut, Filter_Highcut, SAMPLING_RATE, point_sz,
                    'Power Bands (All Sensors-Raw)', data_fname,
                     out_dirname + '/plots/50-ABCS_all_sensors_power_raw_' + date_time_now + '.jpg',
                     date_time_now, analysis_parms)


        plot_all_power_bands(delta_df.mean(axis=1), theta_df.mean(axis=1), 
                    alpha_df.mean(axis=1), beta_df.mean(axis=1), gamma_df.mean(axis=1),
                    Filter_Lowcut, Filter_Highcut, SAMPLING_RATE, point_sz,
                    'Power Bands (Mean Average)', data_fname,
                     out_dirname + '/plots/51-ABCS_power_mean_' + date_time_now + '.jpg',
                     date_time_now, analysis_parms)

    #     plot_all_power_bands(all_delta, all_theta, all_alpha, all_beta, all_gamma,
    #                 Filter_Lowcut, Filter_Highcut, SAMPLING_RATE, point_sz,
    #                 'Power Bands (Filtered)', data_fname,
    #                  out_dirname + '/plots/51-ABCS_power_flitered_' + date_time_now + '.jpg',
    #                  date_time_now, analysis_parms)



        plot_combined_power_bands(delta_df.mean(axis=1), theta_df.mean(axis=1), 
                    alpha_df.mean(axis=1), beta_df.mean(axis=1), gamma_df.mean(axis=1),
                    delta_df.median(axis=1), theta_df.median(axis=1), 
                    alpha_df.median(axis=1), beta_df.median(axis=1), gamma_df.median(axis=1),
                    Filter_Lowcut, Filter_Highcut, SAMPLING_RATE, 
                    point_sz,'Power Bands Mean & Median', data_fname,
                     out_dirname + '/plots/55-ABCS_power_bands_median_mean' + date_time_now + '.jpg', 
                     date_time_now, analysis_parms)


    #     plot_combined_power_bands(delta_df, theta_df, 
    #                 alpha_df, beta_df, gamma_df,
    #                 delta_df.mean(axis=1), theta_df.mean(axis=1), 
    #                 alpha_df.mean(axis=1), beta_df.mean(axis=1), gamma_df.mean(axis=1),
    #                 Filter_Lowcut, Filter_Highcut, SAMPLING_RATE, 
    #                 point_sz,'Power Bands Mean & Raw', data_fname,
    #                  out_dirname + '/plots/56-ABCS_power_bands_raw_mean' + date_time_now + '.jpg', 
    #                  date_time_now, analysis_parms)




    #     delta_avg = np.mean([tp9_delta_filtered, af7_delta_filtered, 
    #         af8_delta_filtered, tp10_delta_filtered], axis=0 )
    #     theta_avg = np.mean([tp9_theta_filtered, af7_theta_filtered, 
    #         af8_theta_filtered, tp10_theta_filtered], axis=0 )
    #     alpha_avg = np.mean([tp9_alpha_filtered, af7_alpha_filtered, 
    #         af8_alpha_filtered, tp10_alpha_filtered], axis=0 )
    #     beta_avg = np.mean([tp9_beta_filtered, af7_beta_filtered, 
    #         af8_beta_filtered, tp10_beta_filtered], axis=0 )
    #     gamma_avg = np.mean([tp9_gamma_filtered, af7_gamma_filtered, 
    #         af8_gamma_filtered, tp10_gamma_filtered], axis=0 )
    # 
    # 
    #     delta_avg = np.nan_to_num(delta_avg)
    #     theta_avg = np.nan_to_num(theta_avg)
    #     alpha_avg = np.nan_to_num(alpha_avg)
    #     beta_avg = np.nan_to_num(beta_avg)
    #     gamma_avg = np.nan_to_num(gamma_avg)


    if (gui_dict['checkBoxAccelGyro']):

        acc_gyro_df = pd.DataFrame(muse_EEG_data, 
            columns=['Accelerometer_X', 'Accelerometer_Y', 'Accelerometer_Z',
                      'Gyro_X', 'Gyro_Y', 'Gyro_Z'])    

        plot_accel_gryo_data(acc_gyro_df, "Accelerometer/Gyro", data_fname, 
                        out_dirname + '/plots/60-ABCS_accel_gyro_' + date_time_now + 
                        '.jpg', date_time_now, analysis_parms)


    if (gui_dict['checkBoxMellowConcentration']):
            
        mc_df = pd.DataFrame(muse_EEG_data, columns=['Mellow', 'Concentration'])    
        print("generate_plots() -  muse_EEG_data.keys(): ", muse_EEG_data.keys())
#         print("generate_plots() -  mc_df.keys(): ", mc_df.keys())


        if 'Mellow' in muse_EEG_data.keys(): 
            print("Mellow Present, ", end =" ") 
#             print("value =", muse_EEG_data['Mellow']) 
            
#         if len(mc_df['Mellow']) > 1:
        
            plot_mellow_concentration(mc_df['Mellow'], mc_df['Concentration'], 
                         Filter_Lowcut, Filter_Highcut, SAMPLING_RATE, point_sz,
                         'Mellow/Concentration', data_fname, 
                         out_dirname + '/plots/60-ABCS_accel_gyro_' + date_time_now + '.jpg', 
                         date_time_now, analysis_parms)

        else: 
#             print("Mellow  Not present") 
#         else:
            print("generate_plots() -  ********* ")
            print("generate_plots() -  Mellow/Concentration not in data file!!! ")
            print("generate_plots() -  ********* ")
        

    return(True)
            




def main(date_time_now):


#     global data_file
    global gui_dict
    global session_dict
    global out_dirname
    global first_name
    global last_name
    global data_dir

#     print("main() - Home path: ", Path.home())
    rc_filename = str(Path.home()) + "/.ABCS_parms.rc"           

    my_rc_file = Path(rc_filename)

    if my_rc_file.is_file():
        with open(rc_filename, 'r') as myfile:
            data=myfile.read()

        # parse file
        rc_obj = json.loads(data)
        print("main() - rc_obj: ", rc_obj)
        first_name = rc_obj['First Name']
        last_name = rc_obj['Last Name']
        data_dir = rc_obj['Data Dir']

#     print("main() - first_name: ", first_name)
#     print("main() - last_name: ", last_name)
#     print("main() - data_dir: ", data_dir)



    app = QApplication(sys.argv)
    gui = The_GUI()
    gui.show()

    GUI_status = app.exec_() 
#     print("main() - GUI_status: ", GUI_status)

    app.closeAllWindows()
    app.exit()

#     sleep(3)
    
#     print("main() - gui_dict: ", gui_dict)

#     print("main() - MM_CVS_fname: ", MM_CVS_fname)
#     print("main() - MM_CVS_fname: ", MM_CVS_fname)

    head_tail = os.path.split(MM_CVS_fname) 
  

    if len(MM_CVS_fname) != 0:
        print("main() - Processing file: ", MM_CVS_fname)
        out_dirname = head_tail[0] + "/output/" + head_tail[1][:len( head_tail[1]) - 4] 
        print("main() - Output directory: ", out_dirname)
        
    else:
        print("main() - Filename not specified, exiting ...")
        sys.exit(1)
    
          
    (muse_EEG_data, EEG_Dict) = read_eeg_data(MM_CVS_fname, date_time_now)
#     print("main() - EEG_Dict: ", EEG_Dict)
#     print("\n")
#     print("main() - EEG_Dict['RAW_TP9']: ", EEG_Dict['RAW_TP9'])
#     print("main() - EEG_Dict['RAW_TP9']: ", EEG_Dict['RAW_TP9']['25%'], EEG_Dict['RAW_TP9']['75%'])

#     sys.exit(0)
    
    
    generate_plots(muse_EEG_data, MM_CVS_fname, date_time_now)

    session_dict = manage_session_data(session_dict, EEG_Dict)
    
#     print(session_dict)
    
#     app = QApplication(sys.argv)
#     gui = The_GUI()
#     gui.show()
#     sys.exit(app.exec_()) 
    






if __name__ == '__main__':


    import pkg_resources
    import sys

if sys.platform in ['darwin', 'linux', 'linux2']:
#     liblo_path = pkg_resources.resource_filename('liblo', 'liblo.so')
#     dso_path = [(liblo_path, '.')]
#     print("DSO path:", dso_path)    
#     print("LIBLO path:", liblo_path)    
    print("Platform: ", sys.platform)
    
    date_time_now = strftime('%Y-%m-%d-%H.%M.%S', gmtime())

    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--csv_file", help="CSV file to read)")
    parser.add_argument("-v", "--verbose", help="Increase output verbosity", type=int)
    parser.add_argument("-d", "--display_plots", help="Display Plots", action="store_true")
                        
    args = parser.parse_args()

    if args.verbose:
        print("verbose turned on")
        print(args.verbose)

    if args.display_plots:
        print("display_plots:")
        print(args.display_plots)
                   
#     if args.csv_file:
#         fname = args.csv_file
#         out_dirname = "./output/" + fname[:len(fname) - 4]
#         print("Processing file: ", fname)
#         print("Output directory: ", out_dirname)
#         
#         
#     else:
#         print("Filename not specified")
#         sys.exit(1)
# 


    main(date_time_now)


#     sys.exit(0)


