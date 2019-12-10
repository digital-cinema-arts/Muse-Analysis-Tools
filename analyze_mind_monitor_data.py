#!/usr/bin/env python3

''' 

This code will analyze Mind Monitor CSV files and plot the results.


'''

from time import time, sleep
import datetime as dt

import numpy as np
from scipy import fftpack, interpolate
import scipy.signal as signal
import math
import bitstring
import pandas as pd
import os
from time import time, sleep, strftime, gmtime
import sys
import csv
import argparse
import math
from tqdm import tqdm
from progress.bar import Bar, IncrementalBar
import json
from pathlib import Path
from scipy import integrate, signal
from scipy.signal import butter, lfilter

from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()

import matplotlib
matplotlib.use('Qt5Agg')

# matplotlib.use('Agg')
import matplotlib.pyplot as plt
# from matplotlib import cm
# import matplotlib.dates as md
import matplotlib.ticker as ticker

from PyQt5.QtWidgets import *
import PyQt5.QtWidgets as QtWidgets
from PyQt5.QtGui import QPalette, QIcon, QPixmap

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
Sampling_Rate = 250.0
Filter_Lowcut  = 1.0
Filter_Highcut  = 100.0
Filter_Order = 5
NOTCH_B, NOTCH_A = butter(4, np.array([55, 65]) / (256 / 2), btype='bandstop')
Verbosity = 0
session_dict = {}
gui_dict = {}
plot_color_scheme = {}
first_name = ""
last_name = ""
data_dir = ""

# Constants
VERSION_NUM = 0.1
FIGURE_SIZE = (8, 6)
PLOT_DPI = 100

PLOT_PARAMS = {
    'axes.titlesize' : 9,
    'axes.labelsize' : 7,
    'lines.linewidth' : 1,
    'lines.markersize' : 2,
    'xtick.labelsize' : 7,
    'ytick.labelsize' : 7,
    'legend.fontsize': 7,
    'legend.handlelength': 2}
# plt.rcParams.update(PLOT_PARAMS)


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

# ABCS Colors
ABCS_Colors = {
'RawTP9': '#8459E2',
'RawAF7': '#12A714',
'RawAF8': '#3E40E0',
'RawTP10':'#E2D659',
'Delta': '#A20000',
'Theta': '#D1A70C',
'Alpha': '#64D606',
'Beta':  '#25B2E3',
'Gamma': '#A259E2'
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
#         mainLayout.addWidget(self.progressBar, 3, 0, 1, 2)
        mainLayout.setRowStretch(1, 1)
        mainLayout.setRowStretch(2, 1)
        mainLayout.setColumnStretch(0, 1)
        mainLayout.setColumnStretch(1, 1)
        self.setLayout(mainLayout)


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

               
        self.setWindowTitle("Algorithmic Biofeedback Control System Plotting Tools")
        
#         self.changeStyle('macintosh')
#         self.setStyleSheet("QGroupBox { background-color: \
#                 rgb(255, 255, 255); border: 2px solid rgb(100, 50, 200); }")

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

        global Sampling_Rate
        global gui_dict      


#         alert = QMessageBox()
#         alert.setText('Plotting!')
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
        last_name = self.lineLastNameEdit.text()
        interative_GUI = self.checkBoxInteractive.isChecked()        
        plot_EEG = self.checkBoxEEG.isChecked()
        coherence = self.checkBoxCoherence.isChecked()
        power_bands = self.checkBoxPowerBands.isChecked()
        mellow_concentrate = self.checkBoxMellowConcentration.isChecked()
        accel_gyro = self.checkBoxAccelGyro.isChecked()
        plot_3D = self.checkBox3D.isChecked()
        filter = self.checkBoxFilter.isChecked()      
        statistical_plots = self.checkBoxStatistical.isChecked()
        muse_direct = self.checkBoxMuseDirect.isChecked()
        verbosity = self.verbosityComboBox.currentText()
        sample_rate_sel = self.sample_rate_selComboBox.currentText()      
        auto_reject = self.checkBoxAutoReject.isChecked()
        DB = self.checkBoxDB.isChecked()
        HDF5 = self.checkBoxHFDF5.isChecked()
        plot_colors = self.plotColorsComboBox.currentText()
        
        mood = self.moodComboBox.currentText()
        session_notes = self.notesTextEdit.toPlainText()

        if sample_rate_sel == '250 HZ':
            Sampling_Rate = 250.            
        elif sample_rate_sel == '0.5 HZ':
            Sampling_Rate = 0.5
        elif sample_rate_sel == '1.0 HZ':
            Sampling_Rate = 1.0
                    
#         print("Sampling_Rate: ", Sampling_Rate)    
        
        gui_dict.update({'firstName': first_name,'lastName': last_name,
                "session_notes": session_notes,
                "checkBoxInteractive": interative_GUI,
                "checkBoxEEG": plot_EEG,
                "checkBoxCoherence": coherence,
                "checkBoxPowerBands": power_bands,
                "checkBoxMellowConcentration": mellow_concentrate,
                "checkBoxAccelGyro": accel_gyro,
                "checkBox3D": plot_3D,
                "checkBoxFilter": filter,                
                "checkBoxStatistical": statistical_plots,
                "checkBoxMuseDirect": muse_direct,
                "verbosityComboBox": verbosity,
                "sample_rate_selComboBox": sample_rate_sel,
                "checkBoxAutoReject": auto_reject,
                "checkBoxDB": DB,
                "checkBoxHFDF5": HDF5,
                "plotColorsComboBox": plot_colors,               
                "Mood": mood})


        if gui_dict['verbosityComboBox'] == 'Quiet':
            Verbosity = 0
        if gui_dict['verbosityComboBox'] == 'Informative':
            Verbosity = 1
        if gui_dict['verbosityComboBox'] == 'Verbose':
            Verbosity = 2
        if gui_dict['verbosityComboBox'] == 'Debug':
            Verbosity = 3

        if Verbosity > 1:
            print("plot_button_clicked(): gui_dict ", gui_dict)
        
        self.accept()
        
#         self.close()

         
         

    def createTopLeftGroupBox(self):
        self.topLeftGroupBox = QGroupBox("Select Options")

        layout = QVBoxLayout()

        self.checkBoxInteractive = QCheckBox("Display Interactive Plots")
        self.checkBoxInteractive.setChecked(True)
        self.checkBoxInteractive.setEnabled(True)

        self.checkBoxEEG = QCheckBox("Create EEG Plots")
        self.checkBoxEEG.setChecked(True)
        self.checkBoxEEG.setEnabled(True)
        
        self.checkBoxCoherence = QCheckBox("Create Coherence Plots")
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

        self.checkBoxResample = QCheckBox("Resample Data")
        self.checkBoxResample.setChecked(False)
        self.checkBoxResample.setEnabled(False)

        self.checkBoxMuseDirect = QCheckBox("Include Muse Direct Plots")
        self.checkBoxMuseDirect.setChecked(False)
        self.checkBoxMuseDirect.setEnabled(False)

        self.checkBoxStatistical = QCheckBox("Include Statistical Plots")
        self.checkBoxStatistical.setChecked(True)
        self.checkBoxStatistical.setEnabled(True)

        self.checkBoxAutoReject = QCheckBox("Auto-Reject EEG Data")
        self.checkBoxAutoReject.setChecked(True)
        self.checkBoxAutoReject.setEnabled(True)

        self.checkBoxDB = QCheckBox("Send Results to Database")
        self.checkBoxDB.setChecked(False)
        self.checkBoxDB.setEnabled(False)

        self.checkBoxHFDF5 = QCheckBox("Write HDF5 File")
        self.checkBoxHFDF5.setChecked(False)
        self.checkBoxHFDF5.setEnabled(False)
 
        self.labelSampleRate = QtWidgets.QLabel(self)
        self.labelSampleRate.setText('Select Sample Rate')
        self.sample_rate_selComboBox = QComboBox()
        self.sample_rate_selComboBox.addItems(['250 HZ', '0.5 HZ', '1.0 HZ'])
        self.sample_rate_selComboBox.setEnabled(True)
 
        self.plotColorsComboBox = QComboBox()
        self.plotColorsComboBox.addItems(['ABCS Colors', 'Mind Monitor Colors'])
        self.plotColorsLabel = QtWidgets.QLabel(self)
        self.plotColorsLabel.setText('Set Plot Color Scheme')


        layout.addWidget(self.checkBoxInteractive)
        layout.addWidget(self.checkBoxEEG)
        layout.addWidget(self.checkBoxCoherence)
        layout.addWidget(self.checkBoxPowerBands)
        layout.addWidget(self.checkBoxMellowConcentration)
        layout.addWidget(self.checkBoxAccelGyro)
        layout.addWidget(self.checkBox3D)
        layout.addWidget(self.checkBoxStatistical)
        layout.addWidget(self.checkBoxMuseDirect)
        layout.addWidget(self.checkBoxFilter)
        layout.addWidget(self.checkBoxResample)
        layout.addWidget(self.checkBoxAutoReject)
        layout.addWidget(self.checkBoxDB)
        layout.addWidget(self.checkBoxHFDF5)        
        layout.addWidget(self.labelSampleRate)
        layout.addWidget(self.sample_rate_selComboBox)
        layout.addWidget(self.plotColorsLabel)
        layout.addWidget(self.plotColorsComboBox)

#         layout.addWidget(self.verbosityLabel)
#         layout.addWidget(self.radioButton1)
#         layout.addWidget(self.radioButton2)
#         layout.addWidget(self.radioButton2)
#         layout.addWidget(self.radioButton3)

        layout.addStretch(1)
        self.topLeftGroupBox.setLayout(layout)    


    def createTopRightGroupBox(self):
        self.topRightGroupBox = QGroupBox("Meditation Session Details")

        layout = QGridLayout()

#         linePasswordEdit = QLineEdit('Enter a Password')
#         linePasswordEdit.setEchoMode(QLineEdit.Password)

        self.lineFirstNameEdit = QLineEdit(first_name)
        self.lineFirstNameEdit.setEchoMode(QLineEdit.Normal)
        
        self.lineLastNameEdit = QLineEdit(last_name)
        self.lineLastNameEdit.setEchoMode(QLineEdit.Normal)

        self.dateTimeEdit = QDateTimeEdit(self.topRightGroupBox)
        self.dateTimeEdit.setDateTime(QDateTime.currentDateTime())

        self.moodComboBox = QComboBox()
        self.moodComboBox.addItems(['Calm', 'Awake', 'Excited', 'Stressed', 'Sleepy'])
        
        moodLabel = QLabel("Mood")
#         moodLabel.setBuddy(self.moodComboBox)

#         self.moodLabel = QtWidgets.QLabel(self)
#         self.moodLabel.setText('Mood')


#         labelB = QtWidgets.QLabel(windowExample)
#         labelB.setPixmap(QtGui.QPixmap('python.jpg'))
#         labelB.move(100, 40)

        self.labelNotes = QtWidgets.QLabel(self)
        self.labelNotes.setText('Session Notes')

        self.notesTextEdit = QTextEdit()
        self.notesTextEdit.setPlainText("Add any details about your meditation session.  "
                              "For example, mood, place, music, etc.\n")


        layout.addWidget(self.lineFirstNameEdit)
        layout.addWidget(self.lineLastNameEdit)
        layout.addWidget(self.dateTimeEdit)
#         layout.addWidget(self.moodLabel)
        layout.addWidget(moodLabel)
        layout.addWidget(self.moodComboBox)
        layout.addWidget(self.labelNotes)
        layout.addWidget(self.notesTextEdit)

   
#         layout.addWidget(self.lineFirstNameEdit, 1, 0, 1, 2)
#         layout.addWidget(self.lineLastNameEdit, 2, 0, 1, 2)

#         layout.addWidget(linePasswordEdit, 3, 0, 1, 2)
                
#         layout.addWidget(spinBox, 1, 0, 1, 2)
#         layout.addWidget(self.dateTimeEdit, 0, 0, 1, 2)
#         layout.addWidget(slider, 3, 0)
#         layout.addWidget(scrollBar, 4, 0)
#         layout.addWidget(dial, 3, 1, 2, 1)
  
#         layout.setRowStretch(5, 1)
        
    
    
    
        self.topRightGroupBox.setLayout(layout)



    def createBottomLeftTabWidget(self):
        self.bottomRightTabWidget = QTabWidget()

#         self.bottomRightTabWidget.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Ignored)

        tab1 = QWidget()
        tableWidget = QTableWidget(10, 10)

        tab1hbox = QHBoxLayout()
        tab1hbox.setContentsMargins(5, 5, 5, 5)
        tab1hbox.addWidget(tableWidget)
        tab1.setLayout(tab1hbox)

        tab2 = QWidget()

        tab2hbox = QHBoxLayout()
        tab2hbox.setContentsMargins(5, 5, 5, 5)
        tab2.setLayout(tab2hbox)

#         self.bottomRightTabWidget.addTab(tab2, "Session Notes")




    def createBottomRightGroupBox(self):

        self.filePushButton = QPushButton("Select CSV File")
        self.filePushButton.clicked.connect(self.file_button_clicked)
#         filePushButton.setDefault(False)

        self.plotPushButton = QPushButton("Create Plots")
        self.plotPushButton.setDefault(True)
        self.plotPushButton.clicked.connect(self.plot_button_clicked)

        self.bottomLeftGroupBox = QGroupBox("Create Plots")

        self.verbosityComboBox = QComboBox()
        self.verbosityComboBox.addItems(['Quiet', 'Informative', 'Verbose', 'Debug'])
        self.verbosityLabel = QtWidgets.QLabel(self)
        self.verbosityLabel.setText('Set Verbosity')
#         self.verbosityLabel.setBuddy(self.verbosityComboBox)


        self.labelChooseFile = QLabel(self)
        self.labelChooseFile.setText("Choose File:")
        self.labelChooseFile.setAlignment(Qt.AlignCenter)

        layout = QVBoxLayout()
        layout.addWidget(self.labelChooseFile)
        layout.addWidget(self.filePushButton)
        layout.addWidget(self.plotPushButton)
        layout.addWidget(self.verbosityLabel)
        layout.addWidget(self.verbosityComboBox)

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
                        "Select Mind Monitor CSV File", "","MM CSV files (*.csv)", options=options)

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
#         "Select Mind Monitor CSV Files", "","All Files (*);;Python Files (*.py)", options=options)
#         if files:
#             print(files)
  
    
    def saveFileDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getSaveFileName(self,
        "Select Output file","","All Files (*);;PNG Files (*.png)", options=options)
        if fileName:
            print(fileName)
            
            
            

'''

Manage session data 

'''

def manage_session_data(init=False, new_data={}, session_date='', date_time=''):

#     print("manage_session_data()")

    global session_dict
    global EEG_Dict

    if init:

        if Verbosity > 1:
            print("manage_session_data(): Initialize Session Data")

        # Fill in default values for now.  
        # (NOTE: Need to create DB interface)
        session_dict = {
            'ABCS Info':{'Version':VERSION_NUM},
            'Muse Info':{'Headband Version':'2016'},
            'Session_Data':{
            'session_date': session_date,
            'date': date_time,
            'data_file_fname': 'data file name',
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
                        'age': 28,
                        'gender': 'male'
                        }
                    }
                }
            }


        session_dict.update({'GUI_Data':gui_dict})
#     print("manage_session_data() - session_dict: ", session_dict)

    return(session_dict)
 


'''

Connect to database


''' 

def connct_to_DB():
    import mysql.connector
    import sqlite3


    return True
   
   
   
   

'''

Read EEG data from disk. 

'''

def read_eeg_data(fname, date_time_now):
   
    print("read_eeg_data(): Reading EEG data ...")

    global session_dict
    global EEG_Dict


# Muse Direct CSV file format

# timestamps,
# eeg_1,eeg_2,eeg_3,eeg_4,eeg_5,eeg_6,
# acc_1,acc_2,acc_3,gyro_1,gyro_2,gyro_3,
# batt_1,batt_2,batt_3,
# drlref_1,drlref_2,
# delta_absolute_1,delta_absolute_2,delta_absolute_3,delta_absolute_4,
# theta_absolute_1,theta_absolute_2,theta_absolute_3,theta_absolute_4,
# alpha_absolute_1,alpha_absolute_2,alpha_absolute_3,alpha_absolute_4,
# beta_absolute_1,beta_absolute_2,beta_absolute_3,beta_absolute_4,
# gamma_absolute_1,gamma_absolute_2,gamma_absolute_3,gamma_absolute_4,
# delta_relative_1,delta_relative_2,delta_relative_3,delta_relative_4,
# theta_relative_1,theta_relative_2,theta_relative_3,theta_relative_4,
# alpha_relative_1,alpha_relative_2,alpha_relative_3,alpha_relative_4,
# beta_relative_1,beta_relative_2,beta_relative_3,beta_relative_4,
# gamma_relative_1,gamma_relative_2,gamma_relative_3,gamma_relative_4,
# delta_session_score_1,delta_session_score_2,delta_session_score_3,delta_session_score_4,
# theta_session_score_1,theta_session_score_2,theta_session_score_3,theta_session_score_4,
# alpha_session_score_1,alpha_session_score_2,alpha_session_score_3,alpha_session_score_4,
# beta_session_score_1,beta_session_score_2,beta_session_score_3,beta_session_score_4,
# gamma_session_score_1,gamma_session_score_2,gamma_session_score_3,gamma_session_score_4,
# blink,jaw_clench,
# hsi_precision_1,hsi_precision_2,hsi_precision_3,hsi_precision_4,
# note,recorder_info,config,device,
# ppg_1,ppg_2,ppg_3


# Mind Monitor CSV format:

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

# dateparse = lambda x: pd.datetime.strptime(x, '%Y-%m-%d %H:%M:%S')
# df = pd.read_csv(infile, parse_dates=['datetime'], date_parser=dateparse)


    muse_EEG_data = pd.read_csv(fname, verbose=Verbosity)

    num_cols = len(muse_EEG_data.columns)


    time_df = pd.DataFrame(muse_EEG_data, columns=['TimeStamp'])    
    if Verbosity > 1:
        print("read_eeg_data(): Session Date: ", time_df['TimeStamp'][0])
        print("read_eeg_data(): num_cols: ", num_cols)
        print("read_eeg_data(): muse_EEG_data.columns: ", muse_EEG_data.columns)
        print("read_eeg_data() - muse_EEG_data.describe(): ", muse_EEG_data.describe())   
        print("read_eeg_data() - muse_EEG_data.keys(): ", muse_EEG_data.keys())   
    
    pause_and_prompt(1, "Data successfuly read")

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
    
    elements_df = pd.DataFrame(muse_EEG_data, columns=['TimeStamp', 'Elements'])

    if Verbosity > 1:
        print("read_eeg_data() - Elements.describe(): ", elements_df.describe())   
        print("read_eeg_data() - elements_df.count(): ", elements_df.count())

#     sys.exit()

     
    elements_df['Elements'] = elements_df.Elements.astype(str)

#     for index, row in elements_df.iterrows():
#         if row['Elements'] != 'nan':
#             print(row['TimeStamp'])
#             print(row['Elements'])


    for temp_df in (raw_df, delta_df, theta_df, alpha_df, beta_df, gamma_df):
#         if args.verbose:
#             print("verbose turned on")

        if Verbosity > 1:
            print("read_eeg_data(): Sensor data description", temp_df.describe())
#         data_str = temp_df.mean()
        data_str = temp_df.describe()
#         print("type", type(data_str))
#         print("data_str.index", data_str.index)
        EEG_Dict.update(data_str.to_dict())
#         print("EEG_Dict: ", EEG_Dict)
#         print("data_str.to_dict()", data_str.to_dict())
    



    sample_length = len(raw_df['RAW_AF7'])
    sample_time_sec = (sample_length/Sampling_Rate)
    sample_time_min = sample_time_sec/60.0

    parms_dict = {
            'Analysis Parameters':{
            "lowcut":Filter_Lowcut, "highcut": Filter_Highcut, "filter_order":Filter_Order, 
                        "sample_length":sample_length, "sample_time_sec":sample_time_sec, 
                        "sample_time_min":sample_time_min}
            }
             
    session_dict = manage_session_data(init=True, 
                    session_date=str(time_df['TimeStamp'][0]), date_time=date_time_now)
    session_dict.update({'EEG Data':EEG_Dict})
    session_dict.update({'Parameters':parms_dict})

#         session_dict.update({'GUI_Data':gui_dict})


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



'''

Auto reject that exceeds min/max limits.  

'''
def auto_reject_EEG_data(data):

# TODO: Insert markers 


    print("auto_reject_EEG_data()")


#     print("auto_reject_EEG_data() - data.describe()", data['RAW_TP9'].describe())


#     tp9_quantile = data['RAW_TP9'].quantile([.35, .65])
#     tp10_quantile = data['RAW_TP10'].quantile([.35, .65])
#     
#     print("auto_reject_EEG_data() - type(tp9_quantile) ", type(tp9_quantile))                    
#     print("auto_reject_EEG_data() - tp9_quantile ", tp9_quantile)                    
#     print("auto_reject_EEG_data() - tp10_quantile ", tp10_quantile)                    


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


#     data_stats = (EEG_Dict['RAW_AF7']['25%'], EEG_Dict['RAW_AF7']['75%'],
#                 EEG_Dict['RAW_AF8']['25%'], EEG_Dict['RAW_AF8']['75%'],
#                 EEG_Dict['RAW_TP9']['25%'], EEG_Dict['RAW_TP9']['75%'],
#                 EEG_Dict['RAW_TP10']['25%'], EEG_Dict['RAW_TP10']['75%'])
# 
#     data.loc[df['column_name'].isin(some_values)]

#     new_df = data.loc[data['RAW_TP9'] < 1200.]
#     new_df = new_df.loc[new_df['RAW_TP9'] > 800.]

    clip_padding = 100.
    
    new_df = data.loc[data['RAW_TP9'] <  (EEG_Dict['RAW_TP9']['75%'] + clip_padding)]
    new_df = new_df.loc[new_df['RAW_TP9'] >  (EEG_Dict['RAW_TP9']['25%'] - clip_padding)]

    new_df = new_df.loc[new_df['RAW_AF7'] <  (EEG_Dict['RAW_AF7']['75%'] + clip_padding)]
    new_df = new_df.loc[new_df['RAW_AF7'] >  (EEG_Dict['RAW_AF7']['25%'] - clip_padding)]

    new_df = new_df.loc[new_df['RAW_AF8'] <  (EEG_Dict['RAW_AF8']['75%'] + clip_padding)]
    new_df = new_df.loc[new_df['RAW_AF8'] >  (EEG_Dict['RAW_AF8']['25%'] - clip_padding)]

    new_df = new_df.loc[new_df['RAW_TP10'] <  (EEG_Dict['RAW_TP10']['75%'] + clip_padding)]
    new_df = new_df.loc[new_df['RAW_TP10'] >  (EEG_Dict['RAW_TP10']['25%'] - clip_padding)]


#     print("auto_reject_EEG_data() - data.describe()", data['RAW_TP9'].describe())
#     print("auto_reject_EEG_data() - new_df.describe()", new_df['RAW_TP9'].describe())
    
    
# 
#     new_df = new_df.loc[new_df['RAW_TP9'] < 550.]
# 
#     print("auto_reject_EEG_data() - new_df.describe()", new_df.describe())
    

    return new_df
    


'''

Scale data 

'''

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



def butter_lowpass(cutoff, fs, order=5):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq

    print("butter_lowpass() nyq: ", nyq, " cutoff ", cutoff,  
            "normal_cutoff:", normal_cutoff, " fs ", fs, " order ", order)

    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    return b, a


def butter_lowpass_filter(data, cutoff, fs, order=5):
    b, a = butter_lowpass(cutoff, fs, order=order)
    y = lfilter(b, a, data)
    return y
    



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




'''

Plot  coherence 

'''

def plot_coherence(x, y, a, b, title, data_fname, plot_fname, date_time_now, analysis_parms, fig_num):

    print('plot_coherence() called')

#     fig = plt.figure(num=fig_num, figsize=(FIGURE_SIZE), dpi=PLOT_DPI, 
#                              sharex=True, sharey=True, facecolor='w', edgecolor='k')

    fig, axs = plt.subplots(nrows=1, num=fig_num, figsize=(6, 6),
        dpi=PLOT_DPI, facecolor='w', edgecolor='k', sharex=True, sharey=True,
        gridspec_kw={'hspace': 0.25}, tight_layout=False)
        
    plt.rcParams.update(PLOT_PARAMS)

    plt_axes = plt.gca()
#     plt_axes.set_xlim([0, len(x)])
#     plt_axes.set_ylim([-1000, 1000])
    
    plt.scatter(x, y, s=1, color='r', alpha=0.7, label='AF7/AF8')
    plt.scatter(a, b, s=1, color='g', alpha=0.7, label='TP9/TP10')

    
    plt.xlabel('Amp uV')
    plt.ylabel('Amp uV')
    # plt.hlines([-a, a], 0, T, linestyles='--')
    plt.grid(True)
    plt.axis('auto')
    plt.suptitle('Algorithmic Biofeedback Control System', fontsize=12, fontweight='bold')
    plt.title(title)
    plt.legend(loc='upper left')

    plt.text(0.175, 1.03, 'Session Date: ' + session_dict['Session_Data']['session_date'], 
            transform=plt_axes.transAxes, style='italic', fontsize=6, horizontalalignment='right',
            bbox={'facecolor':'blue', 'alpha':0.1, 'pad':4})

#     plt_axes.xaxis.set_major_locator(ticker.MultipleLocator(Sampling_Rate))
#     plt_axes.xaxis.set_minor_locator(ticker.MultipleLocator(Sampling_Rate/10))

    plt_axes.xaxis.set_major_locator(ticker.AutoLocator())  
    plt_axes.xaxis.set_minor_locator(ticker.AutoMinorLocator())


    create_analysis_parms_text(0.76, 1.01, plt_axes, analysis_parms)    
    basename = os.path.basename(data_fname)
    create_file_date_text(-0.1, -0.1, -0.1, -0.06, plt_axes, basename, date_time_now)
         
        
    plt.savefig(plot_fname, dpi=300)

#     if (args.display_plots or gui_dict['checkBoxInteractive']):
#     if (args.display_plots):
    if (gui_dict['checkBoxInteractive']):
        plt.show()

    plt.close()
    print("Finished writing EEG EF7 & EF8 Integrated Data - Coherence plot")
    print(plot_fname)
    print





'''

Plot the sensor data 

'''

def plot_sensor_data(timestamps, tp9, af7, af8, tp10, data_fname, plot_fname, date_time_now, 
                        title, data_stats, analysis_parms, fig_num):

    global session_dict
    
    print('plot_sensor_data() called')
#     print('plot_sensor_data() data_stats: ', data_stats)


    # Run the stats of the incoming data which is specific to each call to this function
    tp9_mean = np.mean(np.nan_to_num(tp9))
    tp9_std = np.std(np.nan_to_num(tp9))
    tp9_max = np.max(np.nan_to_num(tp9))
    tp9_min = np.min(np.nan_to_num(tp9))

    af7_mean = np.mean(np.nan_to_num(af7))
    af7_std = np.std(np.nan_to_num(af7))
    af7_max = np.max(np.nan_to_num(af7))
    af7_min = np.min(np.nan_to_num(af7))

    af8_mean = np.mean(np.nan_to_num(af8))
    af8_std = np.std(np.nan_to_num(af8))
    af8_max = np.max(np.nan_to_num(af8))
    af8_min = np.min(np.nan_to_num(af8))

    tp10_mean = np.mean(np.nan_to_num(tp10))
    tp10_std = np.std(np.nan_to_num(tp10))
    tp10_max = np.max(np.nan_to_num(tp10))
    tp10_min = np.min(np.nan_to_num(tp10))

    if Verbosity > 2:  

        print("tp9_mean: ", tp9_mean)
        print("tp9_std: ", tp9_std)
        print("tp9_max: ", tp9_max)
        print("tp9_min: ", tp9_min)
    
        print("af7_mean: ", af7_mean)
        print("af7_std: ", af7_std)
        print("af7_max: ", af7_max)
        print("af7_min: ", af7_min)

        print("af8_mean: ", af8_mean)
        print("af8_std: ", af8_std)
        print("af8_max: ", af8_max)
        print("af8_min: ", af8_min)

        print("tp10_mean: ", tp10_mean)
        print("tp10_std: ", tp10_std)
        print("tp10_max: ", tp10_max)
        print("tp10_min: ", tp10_min)

   
    t_len = len(timestamps)

#     print('plot_sensor_data() t_len: ', t_len)
    
    period = (1.0/Sampling_Rate)
    x_series = np.arange(0, t_len * period, period)
 
#     print('plot_sensor_data() x_series: ', x_series)

    fig, axs = plt.subplots(nrows=5, num=fig_num, figsize=FIGURE_SIZE, 
                    dpi=PLOT_DPI, facecolor='w', edgecolor='k', sharex=True, sharey=False, 
                        gridspec_kw={'hspace': 0.25}, tight_layout=False)
       
    plt.suptitle('Algorithmic Biofeedback Control System', fontsize=12, fontweight='bold')

    plt.rcParams.update(PLOT_PARAMS)
            
    plt_axes = plt.gca()


#     data_stats = (EEG_Dict['RAW_AF7']['25%'], EEG_Dict['RAW_AF7']['75%'],
#                 EEG_Dict['RAW_AF8']['25%'], EEG_Dict['RAW_AF8']['75%'],
#                 EEG_Dict['RAW_TP9']['25%'], EEG_Dict['RAW_TP9']['75%'],
#                 EEG_Dict['RAW_TP10']['25%'], EEG_Dict['RAW_TP10']['75%'])
 
#     plt_axes.set_ylim([data_stats[0], data_stats[1]])

    data_min = np.min((data_stats[0], data_stats[2], data_stats[4], data_stats[6]))
    data_max = np.max((data_stats[1], data_stats[3], data_stats[5], data_stats[7]))
  
    if Verbosity > 1:  
        print('plot_sensor_data() data_stats: ', data_stats)
        print('plot_sensor_data() data_min: ', data_min)
        print('plot_sensor_data() data_max: ', data_max)


#     plt_axes.set_ylim(data_min - 100, data_max + 100)

    clip_padding = 100. 
    y_limits = [data_min - clip_padding, data_max + clip_padding]

    pt_size = 2

    if (gui_dict['plotColorsComboBox'] == 'ABCS Colors'):
        plot_color_scheme = ABCS_Colors
    else:
        plot_color_scheme = MM_Colors
    

#     x1 = np.arange(0, t_len)    
# #     y1 = np.cos(x1)
#     y1 = np.cos(x1/1000)
# 
#     f1 = interpolate.interp1d(x1, y1, kind='cubic')
# #     f1 = interpolate.interp1d(df['TimeStamp'], df['RAW_TP9'], kind='cubic')
#     xnew1 = np.arange(0, t_len - 1, 0.1)
#     interp_data = f1(xnew1)  
#     print('plot_sensor_data() interp_data: ', interp_data)


#     axs[0] = axs[1].twiny()           
            
    axs[0].plot(x_series, tp9, alpha=0.8, ms=pt_size, 
                color=plot_color_scheme['RawTP9'], label='TP9')
                              
    axs[0].plot(x_series, af7, alpha=0.8, ms=pt_size, 
                color=plot_color_scheme['RawAF7'], label='AF7')
    axs[0].plot(x_series, af8, alpha=0.8, ms=pt_size, 
                color=plot_color_scheme['RawAF8'], label='AF8')
    axs[0].plot(x_series, tp10, alpha=0.8, ms=pt_size, 
                color=plot_color_scheme['RawTP10'], label='TP10')
  
#     axs[0].xaxis.set_major_locator(ticker.MultipleLocator(Sampling_Rate))  
#     axs[0].xaxis.set_minor_locator(ticker.MultipleLocator(Sampling_Rate/10))
    axs[0].xaxis.set_major_locator(ticker.AutoLocator())  
    axs[0].xaxis.set_minor_locator(ticker.AutoMinorLocator())
    axs[0].set_ylim(y_limits)
     
 
            
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
            

    axs[1].plot(x_series, tp9, alpha=0.5, ms=pt_size, color=plot_color_scheme['RawTP9'], label='TP9')
    axs[1].set(title='TP9', ylabel="Amp uV") 
 #    axs[1].plot(xnew1, interp_data, alpha=0.5, ms=pt_size, 
#                 color='b', label='TP9 - Interp')
#     
#     axs[1].set_ylim(y_limits)
    axs[1].set_ylim((data_stats[0] - clip_padding), (data_stats[1] + clip_padding))
    

    
    axs[2].plot(x_series, af7, alpha=1.0, ms=pt_size, color=plot_color_scheme['RawAF7'], label='AF7')
    axs[2].set(title='AF7', ylabel="Amp uV") 
    axs[2].set_ylim(y_limits)

    axs[3].plot(x_series, af8, alpha=1.0, ms=pt_size, color=plot_color_scheme['RawAF8'], label='AF8')
    axs[3].set(title='AF8', ylabel="Amp uV") 
    axs[3].set_ylim(y_limits)

    axs[4].plot(x_series, tp10, alpha=1.0, ms=pt_size, color=plot_color_scheme['RawTP10'], label='TP10')
    axs[4].set(title='TP10', xlabel="Time (Seconds)", ylabel="Amp uV") 
    axs[4].set_ylim(y_limits)

       
    for tmp_ax in axs:
            tmp_ax.grid(True)
            tmp_ax.legend(loc='upper right')

    basename = os.path.basename(data_fname)
    create_file_date_text(-0.1, -0.7, -0.1, -0.4, axs[4], basename, date_time_now)


#     axs[0].text(0.01, 0.01, 
    plt.text(0.01, 4.55, 
        'Mean: ' + "{:.3f}".format(tp9_mean) + 
        ' Std: ' + "{:.3f}".format(tp9_std) + 
        '\nMin: ' + "{:.3f}".format(tp9_min) +
        ' Max: ' + "{:.3f}".format(tp9_max), style='italic', 
        transform=plt_axes.transAxes, fontsize=5, 
        bbox={'facecolor': 'blue', 'alpha': 0.05, 'pad': 2})

    plt.text(0.01, 3.25, 
        'Mean: ' + "{:.3f}".format(af7_mean) + 
        ' Std: ' + "{:.3f}".format(af7_std) + 
        '\nMin: ' + "{:.3f}".format(af7_min) +
        ' Max: ' + "{:.3f}".format(af7_max), style='italic', 
        transform=plt_axes.transAxes, fontsize=5, 
        bbox={'facecolor': 'blue', 'alpha': 0.05, 'pad': 2})

    plt.text(0.01, 2.05, 
        'Mean: ' + "{:.3f}".format(af8_mean) + 
        ' Std: ' + "{:.3f}".format(af8_std) + 
        '\nMin: ' + "{:.3f}".format(af8_min) +
        ' Max: ' + "{:.3f}".format(af8_max), style='italic', 
        transform=plt_axes.transAxes, fontsize=5, 
        bbox={'facecolor': 'blue', 'alpha': 0.05, 'pad': 2})

    plt.text(0.01, 0.82, 
        'Mean: ' + "{:.3f}".format(tp10_mean) + 
        ' Std: ' + "{:.3f}".format(tp10_std) + 
        '\nMin: ' + "{:.3f}".format(tp10_min) +
        ' Max: ' + "{:.3f}".format(tp10_max), style='italic', 
        transform=plt_axes.transAxes, fontsize=5, 
        bbox={'facecolor': 'blue', 'alpha': 0.05, 'pad': 2})

    
#     plt.axis('tight')

    plt.savefig(plot_fname, dpi=300)
   
    if (args.display_plots or gui_dict['checkBoxInteractive']):
#     if args.display_plots:
        plt.show()
  
    plt.close()
    print("Finished writing sensor data plot ")
    print(plot_fname)
    print("\n")
    







'''

Plot the sensor data as a single plot

'''

def plot_sensor_data_single(timestamps, tp9, af7, af8, tp10, data_fname, plot_fname, date_time_now, 
                        title, data_stats, analysis_parms, fig_num):

    global session_dict
    
    print('plot_sensor_data_single() called')
#     print('plot_sensor_data_single() data_stats: ', data_stats)

    # Run the stats of the incoming data which is specific to each call to this function
    tp9_mean = np.mean(np.nan_to_num(tp9))
    tp9_std = np.std(np.nan_to_num(tp9))
    tp9_max = np.max(np.nan_to_num(tp9))
    tp9_min = np.min(np.nan_to_num(tp9))

    af7_mean = np.mean(np.nan_to_num(af7))
    af7_std = np.std(np.nan_to_num(af7))
    af7_max = np.max(np.nan_to_num(af7))
    af7_min = np.min(np.nan_to_num(af7))

    af8_mean = np.mean(np.nan_to_num(af8))
    af8_std = np.std(np.nan_to_num(af8))
    af8_max = np.max(np.nan_to_num(af8))
    af8_min = np.min(np.nan_to_num(af8))

    tp10_mean = np.mean(np.nan_to_num(tp10))
    tp10_std = np.std(np.nan_to_num(tp10))
    tp10_max = np.max(np.nan_to_num(tp10))
    tp10_min = np.min(np.nan_to_num(tp10))

    if Verbosity > 2:  

        print("tp9_mean: ", tp9_mean)
        print("tp9_std: ", tp9_std)
        print("tp9_max: ", tp9_max)
        print("tp9_min: ", tp9_min)
    
        print("af7_mean: ", af7_mean)
        print("af7_std: ", af7_std)
        print("af7_max: ", af7_max)
        print("af7_min: ", af7_min)

        print("af8_mean: ", af8_mean)
        print("af8_std: ", af8_std)
        print("af8_max: ", af8_max)
        print("af8_min: ", af8_min)

        print("tp10_mean: ", tp10_mean)
        print("tp10_std: ", tp10_std)
        print("tp10_max: ", tp10_max)
        print("tp10_min: ", tp10_min)

   
    t_len = len(timestamps)
    
    period = (1.0/Sampling_Rate)
    x_series = np.arange(0, t_len * period, period)
 
    fig, axs = plt.subplots(nrows=1, num=fig_num, figsize=FIGURE_SIZE, 
                    dpi=PLOT_DPI, facecolor='w', edgecolor='k',
                        gridspec_kw={'hspace': 0.25}, tight_layout=False)
       
    plt.suptitle('Algorithmic Biofeedback Control System', fontsize=12, fontweight='bold')

    plt.rcParams.update(PLOT_PARAMS)            
    plt_axes = plt.gca()

    data_min = np.min((data_stats[0], data_stats[2], data_stats[4], data_stats[6]))
    data_max = np.max((data_stats[1], data_stats[3], data_stats[5], data_stats[7]))
  
    if Verbosity > 1:  
        print('plot_sensor_data_single() data_stats: ', data_stats)
        print('plot_sensor_data_single() data_min: ', data_min)
        print('plot_sensor_data_single() data_max: ', data_max)

    clip_padding = 100. 
    y_limits = [data_min - clip_padding, data_max + clip_padding]

    pt_size = 2

    if (gui_dict['plotColorsComboBox'] == 'ABCS Colors'):
        plot_color_scheme = ABCS_Colors
    else:
        plot_color_scheme = MM_Colors
    
            
    axs.plot(x_series, tp9, alpha=0.8, ms=pt_size, marker='+',
                color=plot_color_scheme['RawTP9'], label='TP9')                            
    axs.plot(x_series, af7, alpha=0.8, ms=pt_size, marker='+',
                color=plot_color_scheme['RawAF7'], label='AF7')
    axs.plot(x_series, af8, alpha=0.8, ms=pt_size, marker='+',
                color=plot_color_scheme['RawAF8'], label='AF8')
    axs.plot(x_series, tp10, alpha=0.8, ms=pt_size, marker='+',
                color=plot_color_scheme['RawTP10'], label='TP10')
  
    axs.xaxis.set_major_locator(ticker.AutoLocator())  
    axs.xaxis.set_minor_locator(ticker.AutoMinorLocator())
    axs.set_ylim(y_limits)
                
    axs.set(title=title, ylabel="Amp uV", xlabel="Time (Seconds)") 

      
#     axs.text(0.95, 0.025, '(All Sensor Data Combined)',
#         verticalalignment='bottom', horizontalalignment='right',
#         transform=axs[0].transAxes, color='green', fontsize=5) 
#        
#     axs.text(0.2, 1.1, 'Session Date: ' + session_dict['Session_Data']['session_date'], 
#             transform=axs[0].transAxes, style='italic', fontsize=6, horizontalalignment='right',
#             bbox={'facecolor':'blue', 'alpha':0.1, 'pad':4})

#     create_analysis_parms_text(0.75, 1.1, axs, analysis_parms)    
            
#     axs[0].annotate('Notable Data Point', xy=([data_stats[0], data_stats[1]]), 
#                             xytext=([data_stats[2], data_stats[3]]),
#             arrowprops=dict(facecolor='black', shrink=0.01))
                   
    axs.grid(True)
    axs.legend(loc='upper right')

    basename = os.path.basename(data_fname)
    create_file_date_text(-0.1, -0.7, -0.1, -0.4, axs, basename, date_time_now)


#     axs[0].text(0.01, 0.01, 

#     plt.text(0.01, 4.55, 
#         'Mean: ' + "{:.3f}".format(tp9_mean) + 
#         ' Std: ' + "{:.3f}".format(tp9_std) + 
#         '\nMin: ' + "{:.3f}".format(tp9_min) +
#         ' Max: ' + "{:.3f}".format(tp9_max), style='italic', 
#         transform=plt_axes.transAxes, fontsize=5, 
#         bbox={'facecolor': 'blue', 'alpha': 0.05, 'pad': 2})
# 

    plt.savefig(plot_fname, dpi=300)
   
    if (args.display_plots or gui_dict['checkBoxInteractive']):
#     if args.display_plots:
        plt.show()
  
    plt.close()
    print("Finished writing sensor data single plot ")
    print(plot_fname)
    print("\n")
    











'''

Plot all the power bands

'''

def plot_all_power_bands(delta, theta, alpha, beta, gamma,
                lowcut, highcut, fs, point_sz, title, 
                data_fname, plot_fname, date_time_now, analysis_parms, fig_num):


# TODO:  Make multiple windows

    plot_alpha = 0.8

    print('plot_all_power_bands() called')

#     print("plot_all_power_bands: ***********************")
#     print("plot_all_power_bands: EEG_Dict\n\n", EEG_Dict)
#     print("plot_all_power_bands: ***********************")
        
    # Run the stats of the incoming data which is specific to each call to this function
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


    if Verbosity > 2:  
        print("gamma_mean: ", gamma_mean)
        print("gamma_std: ", gamma_std)
        print("gamma_max: ", gamma_max)
        print("gamma_min: ", gamma_min)
    
        print("beta_mean: ", beta_mean)
        print("beta_std: ", beta_std)
        print("beta_max: ", beta_max)
        print("beta_min: ", beta_min)

        print("alpha_mean: ", alpha_mean)
        print("alpha_std: ", alpha_std)
        print("alpha_max: ", alpha_max)
        print("alpha_min: ", alpha_min)

        print("theta_mean: ", theta_mean)
        print("theta_std: ", theta_std)
        print("theta_max: ", theta_max)
        print("theta_min: ", theta_min)

        print("delta_mean: ", delta_mean)
        print("delta_std: ", delta_std)
        print("delta_max: ", delta_max)
        print("delta_min: ", delta_min)


    fig, axs = plt.subplots(num=fig_num, nrows=5, figsize=(FIGURE_SIZE), 
                            sharex=True, sharey=False, gridspec_kw={'hspace': 0})

#     fig.subplots_adjust(top=0.85)

    plt_axes = plt.gca()
#     plt.axis('auto')

    xmin, xmax, ymin, ymax = plt.axis()

#     print("xmin: ", xmin)
#     print("xmax: ", xmax)
#     print("ymin: ", ymin)
#     print("ymax: ", ymax)


    plt.rcParams.update(PLOT_PARAMS)

    if (gui_dict['plotColorsComboBox'] == 'ABCS Colors'):
        plot_color_scheme = ABCS_Colors
    else:
        plot_color_scheme = MM_Colors


    t_len = len(delta)
    period = (1.0/Sampling_Rate)
    x_series = np.arange(0, t_len * period, period)

    axs[0].set(title=title) 

#     axs[0].xaxis.set_major_locator(ticker.MultipleLocator(Sampling_Rate))
#     axs[0].xaxis.set_minor_locator(ticker.MultipleLocator(Sampling_Rate/10))
    axs[0].xaxis.set_major_locator(ticker.AutoLocator())  
    axs[0].xaxis.set_minor_locator(ticker.AutoMinorLocator())

    axs[0].axis('auto')

    l0 = axs[0].plot(x_series, gamma,  color=plot_color_scheme['Gamma'], 
                    alpha=plot_alpha, label='Gamma')
    axs[0].legend(loc='upper right', prop={'size': 6})     
    axs[0].grid(True)
#     axs[0].hlines([-a, a], 0, T, linestyles='--')

    l1 = axs[1].plot(x_series, beta,  color=plot_color_scheme['Beta'], 
                    alpha=plot_alpha, label='Beta')
    axs[1].legend(loc='upper right', prop={'size': 6})
    axs[1].grid(True)
#     axs[1].hlines([-a, a], 0, T, linestyles='--')
#     axs[1].set(title='Beta') 
    axs[1].axis('auto')

    l2 = axs[2].plot(x_series, alpha,  color=plot_color_scheme['Alpha'], 
                    alpha=plot_alpha, label='Alpha')
    axs[2].legend(loc='upper right', prop={'size': 6})
    axs[2].grid(True)
#     axs[2].hlines([-a, a], 0, T, linestyles='--')
#     axs[2].set(title='Alpha') 
    axs[2].axis('auto')

    l3 = axs[3].plot(x_series, theta,  color=plot_color_scheme['Theta'], 
                alpha=plot_alpha, label='Theta')
    axs[3].legend(loc='upper right', prop={'size': 6})
    axs[3].grid(True)
#     axs[3].hlines([-a, a], 0, T, linestyles='--')
#     axs[3].set(title='Theta') 
    axs[3].axis('auto')

    l4 = axs[4].plot(x_series, delta,  color=plot_color_scheme['Delta'], 
                alpha=plot_alpha, label='Delta')
    axs[4].legend(loc='upper right', prop={'size': 6})
    axs[4].grid(True)
#     axs[4].hlines([-a, a], 0, T, linestyles='--')
#     axs[4].set(title='Delta') 
    axs[4].axis('auto')


    fig.suptitle('Algorithmic Biofeedback Control System', fontsize=12, fontweight='bold')
     
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

    plt.text(0.25, 5.075, 'Session Date: ' + session_dict['Session_Data']['session_date'], 
            transform=plt_axes.transAxes, style='italic', fontsize=6, horizontalalignment='right',
            bbox={'facecolor':'blue', 'alpha':0.1, 'pad':4})

    create_analysis_parms_text(0.8, 5.075, plt_axes, analysis_parms)    
    basename = os.path.basename(data_fname)
    create_file_date_text(-0.1, -0.55, -0.1, -0.4, plt_axes, basename, date_time_now)

    plt.savefig(plot_fname, dpi=300)

    if (args.display_plots or gui_dict['checkBoxInteractive']):
#     if args.display_plots:
        plt.show()

    plt.close()

    print("Finished writing " + title + " data plot ")
    print(plot_fname)
    print



'''

Plot all the sensor power bands

'''

def plot_sensor_power_bands(delta, theta, alpha, beta, gamma,
                lowcut, highcut, fs, point_sz, title, 
                data_fname, plot_fname, date_time_now, analysis_parms, fig_num):

# TODO:  Make multiple windows

    plot_alpha = 0.8

    print('plot_sensor_power_bands() called')

    # Run the stats of the incoming data which is specific to each call to this function
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


    if Verbosity > 2:  

        print("gamma_mean: ", gamma_mean)
        print("gamma_std: ", gamma_std)
        print("gamma_max: ", gamma_max)
        print("gamma_min: ", gamma_min)
    
        print("beta_mean: ", beta_mean)
        print("beta_std: ", beta_std)
        print("beta_max: ", beta_max)
        print("beta_min: ", beta_min)

        print("alpha_mean: ", alpha_mean)
        print("alpha_std: ", alpha_std)
        print("alpha_max: ", alpha_max)
        print("alpha_min: ", alpha_min)

        print("theta_mean: ", theta_mean)
        print("theta_std: ", theta_std)
        print("theta_max: ", theta_max)
        print("theta_min: ", theta_min)

        print("delta_mean: ", delta_mean)
        print("delta_std: ", delta_std)
        print("delta_max: ", delta_max)
        print("delta_min: ", delta_min)

    plt.rcParams.update(PLOT_PARAMS)
    

    if (gui_dict['plotColorsComboBox'] == 'ABCS Colors'):
        plot_color_scheme = ABCS_Colors
    else:
        plot_color_scheme = MM_Colors

    fig, axs = plt.subplots(num=fig_num, nrows=5, figsize=(FIGURE_SIZE), 
                            sharex=True, sharey=False, gridspec_kw={'hspace': 0})

#     fig.subplots_adjust(top=0.85)

    plt_axes = plt.gca()
#     plt.axis('auto')

    xmin, xmax, ymin, ymax = plt.axis()

#     print("xmin: ", xmin)
#     print("xmax: ", xmax)
#     print("ymin: ", ymin)
#     print("ymax: ", ymax)

    t_len = len(delta)
    period = (1.0/Sampling_Rate)
    x_series = np.arange(0, t_len * period, period)

    axs[0].set(title=title) 

#     axs[0].xaxis.set_major_locator(ticker.MultipleLocator(Sampling_Rate))
#     axs[0].xaxis.set_minor_locator(ticker.MultipleLocator(Sampling_Rate/10))
    axs[0].xaxis.set_major_locator(ticker.AutoLocator())  
    axs[0].xaxis.set_minor_locator(ticker.AutoMinorLocator())

    loop_cntr = 0 
    markers = ('o', 's', '^', 'D')
    marker_size = 1.5
    
    for key, value in gamma.iteritems():
        loop_cntr  += 1

        l0 = axs[0].plot(x_series, value, color=plot_color_scheme['Gamma'], 
                markerfacecolor=('#000000'), markevery=10, ms=marker_size,
                    marker=markers[loop_cntr - 1], alpha=plot_alpha, label=key)

#     l0 = axs[0].plot(x_series, gamma,  color=plot_color_scheme['Gamma'], 
#                     alpha=plot_alpha, label='Gamma')

    axs[0].legend(loc='upper right', prop={'size': 6})     
    axs[0].grid(True)
    #     axs[0].hlines([-a, a], 0, T, linestyles='--')

    loop_cntr = 0 
    for key, value in beta.iteritems():
        loop_cntr  += 1

        l1 = axs[1].plot(x_series, value, color=plot_color_scheme['Beta'], 
                markerfacecolor=('#000000'), markevery=10, ms=marker_size,
                    marker=markers[loop_cntr - 1], alpha=plot_alpha, label=key)

    axs[1].legend(loc='upper right', prop={'size': 6})
    axs[1].grid(True)
#     axs[1].hlines([-a, a], 0, T, linestyles='--')

    loop_cntr = 0 
    for key, value in alpha.iteritems():
        loop_cntr  += 1

        l2 = axs[2].plot(x_series, value, color=plot_color_scheme['Alpha'], 
                markerfacecolor=('#000000'), markevery=10, ms=marker_size,
                    marker=markers[loop_cntr - 1], alpha=plot_alpha, label=key)

    axs[2].legend(loc='upper right', prop={'size': 6})
    axs[2].grid(True)
#     axs[2].hlines([-a, a], 0, T, linestyles='--')

    loop_cntr = 0 
    for key, value in theta.iteritems():
        loop_cntr  += 1

        l3 = axs[3].plot(x_series, value, color=plot_color_scheme['Theta'], 
                markerfacecolor=('#000000'), markevery=10, ms=marker_size,
                    marker=markers[loop_cntr - 1], alpha=plot_alpha, label=key)

    axs[3].legend(loc='upper right', prop={'size': 6})
    axs[3].grid(True)
#     axs[3].hlines([-a, a], 0, T, linestyles='--')

    loop_cntr = 0 
    for key, value in delta.iteritems():
        loop_cntr  += 1

        l4 = axs[4].plot(x_series, value, color=plot_color_scheme['Delta'], 
                markerfacecolor=('#000000'), markevery=10, ms=marker_size,
                    marker=markers[loop_cntr - 1], alpha=plot_alpha, label=key)

    axs[4].legend(loc='upper right', prop={'size': 6})
    axs[4].grid(True)
#     axs[4].hlines([-a, a], 0, T, linestyles='--')

#
    fig.suptitle('Algorithmic Biofeedback Control System', fontsize=12, fontweight='bold')

     
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

    plt.text(0.25, 5.08, 'Session Date: ' + session_dict['Session_Data']['session_date'], 
            transform=plt_axes.transAxes, style='italic', fontsize=6, horizontalalignment='right',
            bbox={'facecolor':'blue', 'alpha':0.1, 'pad':4})

    create_analysis_parms_text(0.8, 5.08, plt_axes, analysis_parms)    
    basename = os.path.basename(data_fname)
    create_file_date_text(-0.11, -0.58, -0.1, -0.35, plt_axes, basename, date_time_now)

    plt.savefig(plot_fname, dpi=300)

    if (args.display_plots or gui_dict['checkBoxInteractive']):
#     if args.display_plots:
        plt.show()

    plt.close()

    print("Finished writing " + title + " data plot ")
    print(plot_fname)
    print





'''

Plot combined power bands

'''

def plot_combined_power_bands(delta_raw, theta_raw, alpha_raw, beta_raw, gamma_raw,
                delta, theta, alpha, beta, gamma,
                lowcut, highcut, fs, point_sz, title, 
                data_fname, plot_fname, date_time_now, analysis_parms, fig_num):


# TODO:  Make multiple windows correctly

    print('plot_combined_power_bands() called')

    plot_alpha = 0.8

    # Run the stats of the incoming data which is specific to each call to this function
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

    
    fig, axs = plt.subplots(5, num=fig_num, figsize=(FIGURE_SIZE), 
                sharex=True, sharey=False, gridspec_kw={'hspace': 0})

    plt.rcParams.update(PLOT_PARAMS)

    if (gui_dict['plotColorsComboBox'] == 'ABCS Colors'):
        plot_color_scheme = ABCS_Colors
    else:
        plot_color_scheme = MM_Colors


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


    t_len = len(delta)
    period = (1.0/Sampling_Rate)
    x_series = np.arange(0, t_len * period, period)

    axs[0].set(title=title) 
#     axs[0].xaxis.set_major_locator(ticker.MultipleLocator(Sampling_Rate))
#     axs[0].xaxis.set_minor_locator(ticker.MultipleLocator(Sampling_Rate/10))
    axs[0].xaxis.set_major_locator(ticker.AutoLocator())  
    axs[0].xaxis.set_minor_locator(ticker.AutoMinorLocator())


    l0 = axs[0].plot(x_series, gamma_raw, color=plot_color_scheme['Gamma'], 
                alpha=plot_alpha, label='Gamma Raw')
    l00 = axs[0].scatter(x_series, gamma, s=1, color=plot_color_scheme['Gamma'], marker='+',
                alpha=plot_alpha, label='Gamma')
    axs[0].legend(loc='upper right', prop={'size': 6})     
    axs[0].grid(True)
#     axs[0].set_xlim([0,2])
    axs[0].set_ylim(y_limits)
    
#     axs[0].hlines([-a, a], 0, T, linestyles='--')

    l1 = axs[1].plot(x_series, beta_raw, color=plot_color_scheme['Beta'], 
        alpha=plot_alpha, label='Beta Raw')
    l11 = axs[1].scatter(x_series, beta, s=1, color=plot_color_scheme['Beta'], marker='+',
        alpha=plot_alpha, label='Beta')
    axs[1].legend(loc='upper right', prop={'size': 6})
    axs[1].grid(True)
    axs[1].set_ylim(y_limits)
#     axs[1].hlines([-a, a], 0, T, linestyles='--')

    l2 = axs[2].plot(x_series, alpha_raw, color=plot_color_scheme['Alpha'], 
        alpha=plot_alpha, label='Alpha Raw')
    l22 = axs[2].scatter(x_series, alpha, s=1, color=plot_color_scheme['Alpha'], marker='+', 
        alpha=plot_alpha, label='Alpha')
    axs[2].legend(loc='upper right', prop={'size': 6})
    axs[2].grid(True)
    axs[2].set_ylim(y_limits)    
#     axs[2].hlines([-a, a], 0, T, linestyles='--')

    l3 = axs[3].plot(x_series, theta_raw, color=plot_color_scheme['Theta'], 
        alpha=plot_alpha, label='Theta Raw')
    l33 = axs[3].scatter(x_series, theta, s=1, color=plot_color_scheme['Theta'], marker='+', 
        alpha=plot_alpha, label='Theta')
    axs[3].legend(loc='upper right', prop={'size': 6})
    axs[3].grid(True)
    axs[3].set_ylim(y_limits)
#     axs[3].hlines([-a, a], 0, T, linestyles='--')

    l4 = axs[4].plot(x_series, delta_raw, color=plot_color_scheme['Delta'], 
        alpha=plot_alpha, label='Delta Raw')
    l44 = axs[4].scatter(x_series, delta, s=1, color=plot_color_scheme['Delta'], marker='+', 
        alpha=plot_alpha, label='Delta')
    axs[4].legend(loc='upper right', prop={'size': 6})
    axs[4].grid(True)
    axs[4].set_ylim(y_limits)
#     axs[4].hlines([-a, a], 0, T, linestyles='--')


    fig.suptitle('Algorithmic Biofeedback Control System', fontsize=12, fontweight='bold')

     
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

    plt.text(0.15, 5.07, 'Session Date: ' + session_dict['Session_Data']['session_date'], 
            transform=plt_axes.transAxes, style='italic', fontsize=6, horizontalalignment='right',
            bbox={'facecolor':'blue', 'alpha':0.1, 'pad':4})


    create_analysis_parms_text(0.75, 5.07, plt_axes, analysis_parms)
    basename = os.path.basename(data_fname)
    create_file_date_text(-0.1, -0.6, -0.1, -0.35, plt_axes, basename, date_time_now)


    plt.savefig(plot_fname, dpi=300)

    if (args.display_plots or gui_dict['checkBoxInteractive']):
#     if args.display_plots:
        plt.show()

    plt.close()

    print("Finished writing " + title + " data plot ")
    print(plot_fname)
    print



'''

Plot Mind Monitor's mellow and concentration data

'''

def plot_mellow_concentration(mellow, concentration,
                lowcut, highcut, fs, point_sz, title, 
                data_fname, plot_fname, date_time_now, analysis_parms, fig_num):


    plot_alpha = 0.8

    print('plot_mellow_concentration() called')

    # Run the stats of the incoming data which is specific to each call to this function
    mellow_mean = np.mean(np.nan_to_num(mellow))
    mellow_std = np.std(np.nan_to_num(mellow))
    mellow_max = np.max(np.nan_to_num(mellow))
    mellow_min = np.min(np.nan_to_num(mellow))

    concentration_mean = np.mean(np.nan_to_num(concentration))
    concentration_std = np.std(np.nan_to_num(concentration))
    concentration_max = np.max(np.nan_to_num(concentration))
    concentration_min = np.min(np.nan_to_num(concentration))

    if Verbosity > 1:
        print("mellow_mean: ", mellow_mean)
        print("mellow_std: ", mellow_std)
        print("mellow_max: ", mellow_max)
        print("mellow_min: ", mellow_min)
    
        print("concentration_mean: ", concentration_mean)
        print("concentration_std: ", concentration_std)
        print("concentration_max: ", concentration_max)
        print("concentration_min: ", concentration_min)

  
    fig, axs = plt.subplots(num=fig_num, nrows=2, figsize=(FIGURE_SIZE), 
                            sharex=True, sharey=False, gridspec_kw={'hspace': 0})

    plt.rcParams.update(PLOT_PARAMS)

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
    period = (1.0/Sampling_Rate)
    x_series = np.arange(0, t_len * period, period)

    axs[0].set(title=title) 
#     axs[0].xaxis.set_major_locator(ticker.MultipleLocator(Sampling_Rate))
#     axs[0].xaxis.set_minor_locator(ticker.MultipleLocator(Sampling_Rate/10))
    axs[0].xaxis.set_major_locator(ticker.AutoLocator())  
    axs[0].xaxis.set_minor_locator(ticker.AutoMinorLocator())

    l0 = axs[0].plot(x_series, mellow,  color='b', alpha=plot_alpha, label='Mellow')
    axs[0].legend(loc='upper right', prop={'size': 6})     
    axs[0].grid(True)
#     axs[0].hlines([-a, a], 0, T, linestyles='--')

    l1 = axs[1].plot(x_series, concentration,  color='g', alpha=plot_alpha, label='Concentration')
    axs[1].legend(loc='upper right', prop={'size': 6})
    axs[1].grid(True)

    fig.suptitle('Algorithmic Biofeedback Control System', fontsize=12, fontweight='bold')

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
 
    plt.text(0.175, 2.05, 'Session Date: ' + session_dict['Session_Data']['session_date'], 
        transform=plt_axes.transAxes, style='italic', fontsize=6, horizontalalignment='right',
        bbox={'facecolor':'blue', 'alpha':0.1, 'pad':4})

    basename = os.path.basename(data_fname)
    create_file_date_text(0.1, -0., 0.1, -0., plt_axes, basename, date_time_now)
    create_analysis_parms_text(0.75, 2.0, plt_axes, analysis_parms)

       
#     create_analysis_parms_text(0.7, 5.07, plt_axes, analysis_parms)    
#     basename = os.path.basename(data_fname)
#     create_file_date_text(-0.12, -0.5, 0.9, -0.5, plt_axes, basename, date_time_now)

    plt.savefig(plot_fname, dpi=300)

    if (args.display_plots or gui_dict['checkBoxInteractive']):
#     if args.display_plots:
        plt.show()

    plt.close()

    print("Finished writing " + title + " data plot ")
    print(plot_fname)
    print




'''

Plot the accelerometer and gyro data 

'''

def plot_accel_gryo_data(acc_gyro_df, title, data_fname, plot_fname, date_time_now, analysis_parms, fig_num):

    print('plot_accel_gryo_data() called')

    plot_alpha = 0.8
    
    t_len = len(acc_gyro_df['Accelerometer_X'])
    period = (1.0/Sampling_Rate)
    x_series = np.arange(0, t_len * period, period)

    fig, axs = plt.subplots(6, num=fig_num, figsize=(FIGURE_SIZE), 
                    sharex=True, sharey=False, gridspec_kw={'hspace': 0})
#     fig.subplots_adjust(top=0.85)

    plt.rcParams.update(PLOT_PARAMS)

    plt_axes = plt.gca()
#     plt.axis('auto')

#     plt_axes.set_ylim(-10, 10)
 
    axs[0].set(title=title) 
#     axs[0].xaxis.set_major_locator(ticker.MultipleLocator(Sampling_Rate))
#     axs[0].xaxis.set_minor_locator(ticker.MultipleLocator(Sampling_Rate/10))
    axs[0].xaxis.set_major_locator(ticker.AutoLocator())  
    axs[0].xaxis.set_minor_locator(ticker.AutoMinorLocator())

    axs[0].set_ylim(-1, 1)
    axs[1].set_ylim(-1, 1)
    axs[2].set_ylim(-1, 1)
    axs[3].set_ylim(-10, 10)
    axs[4].set_ylim(-10, 10)
    axs[5].set_ylim(-10, 10)


#     axs[0].ylabel('Accelerometer/Gyro')
    axs[1].set(ylabel="Accelerometer") 
    axs[4].set(ylabel="Gyro") 
 
            
    l0 = axs[0].plot(x_series, acc_gyro_df['Accelerometer_X'], color='#00AAFF', 
            alpha=plot_alpha, label='X')
    axs[0].legend(loc='upper right', prop={'size': 6})     
    axs[0].grid(True)

    l1 = axs[1].plot(x_series, acc_gyro_df['Accelerometer_Y'], color='#33FF33', 
            alpha=plot_alpha, label='Y')
    axs[1].legend(loc='upper right', prop={'size': 6})
    axs[1].grid(True)

    l2 = axs[2].plot(x_series, acc_gyro_df['Accelerometer_Z'], color='#FF8800', 
            alpha=plot_alpha, label='Z')
    axs[2].legend(loc='upper right', prop={'size': 6})
    axs[2].grid(True)

    l3 = axs[3].plot(x_series, acc_gyro_df['Gyro_X'], color='#00AAFF', 
            alpha=plot_alpha, label='X')
    axs[3].legend(loc='upper right', prop={'size': 6})     
    axs[3].grid(True)

    l4 = axs[4].plot(x_series, acc_gyro_df['Gyro_Y'], color='#33FF33',
            alpha=plot_alpha, label='Y')
    axs[4].legend(loc='upper right', prop={'size': 6})
    axs[4].grid(True)

    l5 = axs[5].plot(x_series, acc_gyro_df['Gyro_Z'], color='#FF8800', 
            alpha=plot_alpha, label='Z')
    axs[5].legend(loc='upper right', prop={'size': 6})
    axs[5].grid(True)

    plt.suptitle('Algorithmic Biofeedback Control System', fontsize=12, fontweight='bold')
#     plt.title(title)
       
    plt.text(0.175, 6.12, 'Session Date: ' + session_dict['Session_Data']['session_date'], 
        transform=plt_axes.transAxes, style='italic', fontsize=6, horizontalalignment='right',
        bbox={'facecolor':'blue', 'alpha':0.1, 'pad':4})

    basename = os.path.basename(data_fname)
    create_file_date_text(-0.1, -0.6, -0.1, -0.4, plt_axes, basename, date_time_now)
    create_analysis_parms_text(0.7, 6.07, plt_axes, analysis_parms)

    plt.savefig(plot_fname, dpi=300)

    if (args.display_plots or gui_dict['checkBoxInteractive']):
#     if args.display_plots:
        plt.show()
 
    plt.close()

    print("Finished writing accel/gyro data plot ")
    print(plot_fname)
    print



   
   
'''

Make labels for the file name and date  

'''

def create_file_date_text(x1, y1, x2, y2, plt_axes, data_fname, date_time_now):

    plt.text(x1, y1, "file: " + data_fname, 
        transform=plt_axes.transAxes, fontsize=5, style='italic',
        bbox={'facecolor':'blue', 'alpha':0.1, 'pad':4})

    plt.text(x2, y2, "Date: " + date_time_now, 
        transform=plt_axes.transAxes, fontsize=5, style='italic',
        bbox={'facecolor':'blue', 'alpha':0.1, 'pad':4})



'''

Make labels for the analysis parameters  

'''

def create_analysis_parms_text(x, y, plt_axes, analysis_parms):

#     plt.text(x, y, 
#         'Low Cut: ' + "{:.1f}".format(analysis_parms['lowcut']) + " HZ " + 
#         ' High Cut: ' + "{:.1f}".format(analysis_parms['highcut']) + " HZ "+ 
#         ' Filter Order: ' + "{:.1f}".format(analysis_parms['filter_order']) +
#         '\nSample Time: ' + "{:.2f}".format(analysis_parms['sample_time_min']) +
#         ' (minutes) ' + "{:.2f}".format(analysis_parms['sample_time_sec']) + " (seconds)" + 
#         '\nSample Length: ' + "{:d}".format(analysis_parms['sample_length']),
#         style='italic', transform=plt_axes.transAxes, fontsize=5, 
#         bbox={'facecolor': 'blue', 'alpha': 0.05, 'pad': 2})


   plt.text(x, y, 
        'Sample Time:\n' + "{:.2f}".format(analysis_parms['sample_time_min']) +
        ' (minutes) ' + "{:.2f}".format(analysis_parms['sample_time_sec']) + " (seconds)" + 
        '\nSample Length: ' + "{:d}".format(analysis_parms['sample_length']),
        style='italic', transform=plt_axes.transAxes, fontsize=6, 
        bbox={'facecolor': 'blue', 'alpha': 0.05, 'pad': 2})





def pause_and_prompt(pause_time, msg):

    print("Pausing ... " + msg)
    sleep(pause_time)


'''

Make sure a directory exits, if it doesn't create it.  

'''

def ensure_dir(file_path):
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.makedirs(directory)



'''

Plot the data!

'''

def generate_plots(muse_EEG_data, data_fname, date_time_now):

    print("Generating plots ", date_time_now)
    print

    ensure_dir(out_dirname + "/plots/")

    df = pd.DataFrame(muse_EEG_data, columns=['TimeStamp', 'RAW_TP9', 'RAW_AF7', 'RAW_AF8', 'RAW_TP10'])    
#     df = np.clip(df, -100.0, 100.0)

#     df['RAW_TP9'] = np.nan_to_num(df['RAW_TP9'])
#     df['RAW_AF7'] = np.nan_to_num(df['RAW_AF7'])
#     df['RAW_AF8'] = np.nan_to_num(df['RAW_AF8'])
#     df['RAW_TP10'] = np.nan_to_num(df['RAW_TP10'])

    if Verbosity > 1:
        print("Sampling_Rate: ", Sampling_Rate)
        print("Filter_Lowcut: ", Filter_Lowcut)
        print("Filter_Highcut: ", Filter_Highcut)
        print("Filter_Order: ", Filter_Order)


    sample_length = len(df['TimeStamp'])
    sample_time_sec = (sample_length/Sampling_Rate)
    sample_time_min = sample_time_sec/60.0

    if Verbosity > 1:
        print("sample_length: ", sample_length)
        print("sample_time_sec: ", sample_time_sec)
        print("sample_time_min: ", sample_time_min)
        print("\n")

    
    analysis_parms = {"lowcut":Filter_Lowcut, 
        "highcut": Filter_Highcut, "filter_order":Filter_Order, 
        "sample_length":sample_length, "sample_time_sec":sample_time_sec, 
        "sample_time_min":sample_time_min}


    point_sz = 1                    

    # Generate plots 

#     print("generate_plots() - EEG_Dict['RAW_TP9']: ", EEG_Dict['RAW_TP9'])
#     print("generate_plots() - EEG_Dict['RAW_TP9']: ", 
#                 EEG_Dict['RAW_TP9']['25%'], EEG_Dict['RAW_TP9']['75%'])


    data_stats = (EEG_Dict['RAW_AF7']['25%'], EEG_Dict['RAW_AF7']['75%'],
                EEG_Dict['RAW_AF8']['25%'], EEG_Dict['RAW_AF8']['75%'],
                EEG_Dict['RAW_TP9']['25%'], EEG_Dict['RAW_TP9']['75%'],
                EEG_Dict['RAW_TP10']['25%'], EEG_Dict['RAW_TP10']['75%'])
    
 
    
    if (gui_dict['checkBoxEEG']):
 
        plot_sensor_data_single(df['TimeStamp'], df['RAW_TP9'], df['RAW_AF7'], 
            df['RAW_AF8'], df['RAW_TP10'], data_fname, 
            out_dirname + '/plots/22-ABCS_eeg_raw_single_' + date_time_now + '.png',
            date_time_now,  "Raw EEG", data_stats, analysis_parms, 22)

        plot_sensor_data(df['TimeStamp'], df['RAW_TP9'], df['RAW_AF7'], 
            df['RAW_AF8'], df['RAW_TP10'], data_fname, 
            out_dirname + '/plots/20-ABCS_eeg_raw_' + date_time_now + '.png',
            date_time_now,  "Raw EEG", data_stats, analysis_parms, 20)
    
        smooth_sz = 25
        plot_sensor_data_single(df['TimeStamp'], smooth_data(df['RAW_TP9'], smooth_sz), 
            smooth_data(df['RAW_AF7'], smooth_sz), 
            smooth_data(df['RAW_AF8'], smooth_sz), 
            smooth_data(df['RAW_TP10'], smooth_sz), data_fname, 
            out_dirname + '/plots/25-ABCS_eeg_smoothed_single_' + date_time_now + '.png',
            date_time_now, "Smoothed EEG", data_stats, analysis_parms, 25)

        plot_sensor_data(df['TimeStamp'], smooth_data(df['RAW_TP9'], smooth_sz), 
            smooth_data(df['RAW_AF7'], smooth_sz), 
            smooth_data(df['RAW_AF8'], smooth_sz), 
            smooth_data(df['RAW_TP10'], smooth_sz), data_fname, 
            out_dirname + '/plots/21-ABCS_eeg_smoothed_' + date_time_now + '.png',
            date_time_now, "Smoothed EEG", data_stats, analysis_parms, 21)




#     x1 = np.arange(0, len(df['TimeStamp']))    
#     y1 = np.cos(x1)
#     f1 = interpolate.interp1d(x1, df['RAW_TP9'], kind='cubic')
#     f1 = interpolate.interp1d(df['TimeStamp'], df['RAW_TP9'], kind='cubic')
#     xnew1 = np.arange(0, len(x1) - 1, 0.2)
#     ynew1 = f1(xnew1)  

# Generate an array of data, interpolate, re-sample and graph
# x1 = np.arange(0, num_points)
# y1 = np.cos(x1)
# f1 = interpolate.interp1d(x1, y1, kind='cubic')
# xnew1 = np.arange(0, num_points - 1, 0.2)
# ynew1 = f1(xnew1)  


        if False:
            plot_sensor_data(df['TimeStamp'], df['RAW_TP9'], 
                smooth_data(df['RAW_AF7'], smooth_sz), 
                smooth_data(df['RAW_AF8'], smooth_sz), 
                smooth_data(df['RAW_TP10'], smooth_sz), data_fname, 
                out_dirname + '/plots/21-ABCS_eeg_smoothed_' + date_time_now + '.png',
                date_time_now, "Interpolated EEG", data_stats, analysis_parms, 21)



# TODO fix filtering (Add resampling) 
    if False:
        plot_sensor_data(df['TimeStamp'], filter_data(df['RAW_TP9'], smooth_sz), 
            filter_data(df['RAW_AF7'], smooth_sz), 
            filter_data(df['RAW_AF8'], smooth_sz), 
            filter_data(df['RAW_TP10'], smooth_sz), 
            data_fname,  out_dirname + '/plots/22-ABCS_eeg_filtered_' + date_time_now + '.png',
            date_time_now,  "Filtered EEG", data_stats, analysis_parms, 22)


    if False:
        plot_sensor_data(df['TimeStamp'], butter_bandpass_filter(df['RAW_TP9'], 
            Filter_Lowcut, Filter_Highcut, Sampling_Rate, Filter_Order), 
            butter_bandpass_filter(df['RAW_AF7'],
            Filter_Lowcut, Filter_Highcut, Sampling_Rate, Filter_Order), 
            butter_bandpass_filter(df['RAW_AF8'], 
            Filter_Lowcut, Filter_Highcut, Sampling_Rate, Filter_Order), 
            butter_bandpass_filter(df['RAW_TP10'], 
            Filter_Lowcut, Filter_Highcut, Sampling_Rate, Filter_Order), 
            data_fname,  out_dirname + '/plots/23-ABCS_eeg_bandpass_filtered_' + date_time_now + '.png',
            date_time_now,  "Filtered (Bandpass) EEG", data_stats, analysis_parms, 23)


#    data_stats = (EEG_Dict['RAW_TP9']['25%'], EEG_Dict['RAW_TP9']['75%'])
#     plot_sensor_data(df['RAW_TP9'], df['RAW_TP10'], data_fname, 
#         out_dirname + '/plots/2-ABCS_eeg_TP9_TP10_time_series_data_' + date_time_now + '.png',
#         date_time_now,  "RAW_AF7 & RAW_AF8", data_stats, analysis_parms)
 
                
                
    if (gui_dict['checkBoxCoherence']):

        plot_coherence(df['RAW_AF7'], df['RAW_AF8'], df['RAW_TP9'], df['RAW_TP10'],
            "Raw Data - Coherence", data_fname,
             out_dirname + '/plots/10-ABCS_eeg_raw_coherence_data_' + date_time_now + '.png', 
             date_time_now, analysis_parms, 10)

    if False:
#         if args.plot_3D:

        filt_d = {'FILT_AF7': af7_filt_band, 'FILT_AF8': af8_filt_band, 
                    'FILT_TP9': tp9_filt_band, 'FILT_TP10': tp10_filt_band}

#         filt_df = DataFrame([data, index, columns, dtype, copy])
        filt_df = pd.DataFrame(filt_d, dtype=np.float64)

        pause_and_prompt(0.1, "Plotting 3D")

        plot_3D(muse_EEG_data, filt_df, data_fname,
             out_dirname + '/plots/70-ABCS_3D_' + date_time_now + '.png', 
             date_time_now, analysis_parms, 70)


# Delta_TP9,Delta_AF7,Delta_AF8,Delta_TP10,
# Theta_TP9,Theta_AF7,Theta_AF8,Theta_TP10,
# Alpha_TP9,Alpha_AF7,Alpha_AF8,Alpha_TP10,
# Beta_TP9,Beta_AF7,Beta_AF8,Beta_TP10,
# Gamma_TP9,Gamma_AF7,Gamma_AF8,Gamma_TP10,
# RAW_TP9,RAW_AF7,RAW_AF8,RAW_TP10,AUX_RIGHT,
# Mellow,Concentration,


    if (gui_dict['checkBoxPowerBands']):

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

    
        # Row mean of the dataframe
        if Verbosity > 2:
            print("***************************")
            print(delta_df.mean(axis=1))
            print("***************************")
            print(theta_df.mean(axis=1))
            print("***************************")
            print(alpha_df.mean(axis=1))
            print("***************************")
            print(beta_df.mean(axis=1))
            print("***************************")
            print(gamma_df.mean(axis=1))
            print("***************************")


        plot_sensor_power_bands(delta_df, theta_df, 
            alpha_df, beta_df, gamma_df,
            Filter_Lowcut, Filter_Highcut, Sampling_Rate, point_sz,
            'Power Bands (All Sensors-Raw)', data_fname,
            out_dirname + '/plots/30-ABCS_all_sensors_power_raw_' + date_time_now + '.png',
            date_time_now, analysis_parms, 30)


        if (gui_dict['checkBoxStatistical']):

            plot_all_power_bands(delta_df.mean(axis=1), theta_df.mean(axis=1), 
                alpha_df.mean(axis=1), beta_df.mean(axis=1), gamma_df.mean(axis=1),
                Filter_Lowcut, Filter_Highcut, Sampling_Rate, point_sz,
                'Power Bands (Mean Average)', data_fname,
                out_dirname + '/plots/31-ABCS_power_mean_' + date_time_now + '.png',
                date_time_now, analysis_parms, 31)


    #     plot_all_power_bands(all_delta, all_theta, all_alpha, all_beta, all_gamma,
    #                 Filter_Lowcut, Filter_Highcut, Sampling_Rate, point_sz,
    #                 'Power Bands (Filtered)', data_fname,
    #                  out_dirname + '/plots/51-ABCS_power_flitered_' + date_time_now + '.png',
    #                  date_time_now, analysis_parms)


            plot_combined_power_bands(delta_df.mean(axis=1), theta_df.mean(axis=1), 
                alpha_df.mean(axis=1), beta_df.mean(axis=1), gamma_df.mean(axis=1),
                delta_df.median(axis=1), theta_df.median(axis=1), 
                alpha_df.median(axis=1), beta_df.median(axis=1), gamma_df.median(axis=1),
                Filter_Lowcut, Filter_Highcut, Sampling_Rate, 
                point_sz,'Power Bands Mean & Median', data_fname,
                out_dirname + '/plots/32-ABCS_power_bands_median_mean' + date_time_now + '.png', 
                date_time_now, analysis_parms, 32)


            plot_combined_power_bands(delta_df, theta_df, 
                        alpha_df, beta_df, gamma_df,
                        delta_df.mean(axis=1), theta_df.mean(axis=1), 
                        alpha_df.mean(axis=1), beta_df.mean(axis=1), gamma_df.mean(axis=1),
                        Filter_Lowcut, Filter_Highcut, Sampling_Rate, 
                        point_sz,'Power Bands Mean & Raw', data_fname,
                         out_dirname + '/plots/33-ABCS_power_bands_raw_mean' + date_time_now + '.png', 
                         date_time_now, analysis_parms, 33)






#     if args.filter_data:

#         print("Runnning filters on RAW data")
#         print
# 
#         # Run bandpass filters
#         tp9_filt_band = butter_bandpass_filter(df['RAW_TP9'], Filter_Lowcut, Filter_Highcut, 
#             Sampling_Rate, Filter_Order)
#         af8_filt_band = butter_bandpass_filter(df['RAW_AF8'], Filter_Lowcut, Filter_Highcut, 
#             Sampling_Rate, Filter_Order)
#         af7_filt_band = butter_bandpass_filter(df['RAW_AF7'], Filter_Lowcut, Filter_Highcut, 
#             Sampling_Rate, Filter_Order)
#         tp10_filt_band = butter_bandpass_filter(df['RAW_TP10'], Filter_Lowcut, Filter_Highcut, 
#             Sampling_Rate, Filter_Order)
# 
# 
#         tp9_filt_lowpass = butter_lowpass_filter(df['RAW_TP9'], Filter_Highcut, 
#                 Sampling_Rate, Filter_Order)
#         af8_filt_lowpass = butter_lowpass_filter(df['RAW_AF8'], Filter_Highcut, 
#                 Sampling_Rate, Filter_Order)
#         af7_filt_lowpass = butter_lowpass_filter(df['RAW_AF7'], Filter_Highcut, 
#                 Sampling_Rate, Filter_Order)
#         tp10_filt_lowpass = butter_lowpass_filter(df['RAW_TP10'], Filter_Highcut, 
#                 Sampling_Rate, Filter_Order)



# 
#         tp9_filt_band_low = butter_bandpass_filter(tp9_filt_lowpass, 
#                                 Filter_Lowcut, Filter_Highcut, Sampling_Rate, Filter_Order)
#         af8_filt_band_low = butter_bandpass_filter(af8_filt_lowpass, 
#                                 Filter_Lowcut, Filter_Highcut, Sampling_Rate, Filter_Order)
#         af7_filt_band_low = butter_bandpass_filter(af7_filt_lowpass, 
#                                 Filter_Lowcut, Filter_Highcut, Sampling_Rate, Filter_Order)
#         tp10_filt_band_low = butter_bandpass_filter(tp10_filt_lowpass, 
#                                 Filter_Lowcut, Filter_Highcut, Sampling_Rate, Filter_Order)
# 
# 
# 
#         plot_sensor_data(df['TimeStamp'], tp9_filt_band, af8_filt_band, af8_filt_band, tp10_filt_band, 
#             data_fname, out_dirname + '/plots/34-ABCS_bandpass_' + date_time_now + '.jpg', 
#              date_time_now,  "Filtered EEG", data_stats, analysis_parms, 34)
# 
#         plot_sensor_data(df['TimeStamp'], tp9_filt_lowpass, af8_filt_lowpass, 
#         af7_filt_lowpass, tp10_filt_lowpass, data_fname,
#              out_dirname + '/plots/35-ABCS_lowpass_' + date_time_now + '.jpg', 
#              date_time_now,  "Filtered - Lowpass EEG", data_stats, analysis_parms, 35)
# 
#         plot_sensor_data(df['TimeStamp'], tp9_filt_band_low, af8_filt_band_low, 
#                 af7_filt_band_low, tp10_filt_band_low, 
#                 data_fname, out_dirname + '/plots/35-ABCS_band_low_' + date_time_now + '.jpg', 
#               date_time_now,  "Filtered - Bandpass EEG", data_stats, analysis_parms, 36)
# 
# 
#         plot_coherence(af7_filt_band, af8_filt_band, tp9_filt_band, tp10_filt_band,
#             "EF7 & EF8 Bandpass Filtered - Coherance", data_fname,
#              out_dirname + '/plots/9-ABCS_eeg_bandpass_coherence_data_' + date_time_now + '.jpg', 
#              date_time_now, analysis_parms, 99)
# 
#         plot_coherence(af7_filt_lowpass, af8_filt_lowpass, tp9_filt_band, tp10_filt_band,
#             "EF7 & EF8 Lowpass Filtered - Coherance", data_fname,
#              out_dirname + '/plots/9-ABCS_eeg_bandpass_coherence_data_' + date_time_now + '.jpg', 
#              date_time_now, analysis_parms, 99)
# 
#         plot_coherence(af8_filt_band_low, af8_filt_band_low, tp9_filt_band, tp10_filt_band,
#             "EF7 & EF8 Band/Lowpass Filtered - Coherance", data_fname,
#              out_dirname + '/plots/9-ABCS_eeg_low_bandpass_coherence_data_' + date_time_now + '.jpg', 
#              date_time_now, analysis_parms, 99)




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
                        out_dirname + '/plots/40-ABCS_accel_gyro_' + date_time_now + 
                        '.png', date_time_now, analysis_parms, 40)


    if (gui_dict['checkBoxMellowConcentration']):
            
        mc_df = pd.DataFrame(muse_EEG_data, columns=['Mellow', 'Concentration'])    
#         print("generate_plots() -  muse_EEG_data.keys(): ", muse_EEG_data.keys())


        if 'Mellow' in muse_EEG_data.keys(): 
#             print("Mellow Present, ", end =" ") 
#             print("value =", muse_EEG_data['Mellow']) 
            
#         if len(mc_df['Mellow']) > 1:
        
            plot_mellow_concentration(mc_df['Mellow'], mc_df['Concentration'], 
                         Filter_Lowcut, Filter_Highcut, Sampling_Rate, point_sz,
                         'Mellow/Concentration', data_fname, 
                         out_dirname + '/plots/50-ABCS_accel_gyro_' + date_time_now + '.png', 
                         date_time_now, analysis_parms, 50)

        else: 
#             print("Mellow  Not present") 
#         else:
            print("generate_plots() -  ********* ")
            print("generate_plots() -  Mellow/Concentration not in data file!")
            print("generate_plots() -  ********* ")
        

    return(True)
            



'''

Main ....   

'''

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
        if Verbosity > 1:
            print("main() - rc_obj: ", rc_obj)
        first_name = rc_obj['First Name']
        last_name = rc_obj['Last Name']
        data_dir = rc_obj['Data Dir']


    app = QApplication(sys.argv)
    gui = The_GUI()
    gui.show()

    GUI_status = app.exec_() 

    gui.close()

    app.closeAllWindows()
    app.exit()

#     print("main() - GUI_status: ", GUI_status)
#     print("main() - gui_dict: ", gui_dict)
#     print("main() - MM_CVS_fname: ", MM_CVS_fname)

    head_tail = os.path.split(MM_CVS_fname) 
  
    if len(MM_CVS_fname) != 0:
        out_dirname = head_tail[0] + "/output/" + head_tail[1][:len( head_tail[1]) - 4] 
        if Verbosity > 1:
            print("main() - Processing file: ", MM_CVS_fname)
            print("main() - Output directory: ", out_dirname)
        
    else:
        print("main() - Filename not specified, exiting ...")
        sys.exit(1)
    
          
    (muse_EEG_data, EEG_Dict) = read_eeg_data(MM_CVS_fname, date_time_now)

#     print("main() - EEG_Dict: ", EEG_Dict)
#     print("\n")
    
    
    if (gui_dict['checkBoxAutoReject']): 
        muse_EEG_data = auto_reject_EEG_data(muse_EEG_data)
    
  
#     try:
        
        generate_plots(muse_EEG_data, MM_CVS_fname, date_time_now)
 
   #  except (KeyboardInterrupt, SystemExit):
#         raise
#     except:
#         # report error and proceed

          
#     generate_plots(muse_EEG_data, MM_CVS_fname, date_time_now)


#     session_dict = manage_session_data(init=False)
#     print(session_dict)
      




if __name__ == '__main__':

    import pkg_resources
    import sys

if sys.platform in ['darwin', 'linux', 'linux2', 'win32']:
#     liblo_path = pkg_resources.resource_filename('liblo', 'liblo.so')
#     dso_path = [(liblo_path, '.')]
#     print("DSO path:", dso_path)    
#     print("LIBLO path:", liblo_path)    

    if Verbosity > 1:
        print("Platform: ", sys.platform)
    
    date_time_now = strftime('%Y-%m-%d-%H.%M.%S', gmtime())

    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--csv_file", help="CSV file to read)")
    parser.add_argument("-v", "--verbose", help="Increase output verbosity", type=int)
    parser.add_argument("-d", "--display_plots", help="Display Plots", action="store_true")
    parser.add_argument("-b", "--batch", help="Batch Mode", action="store_true")
    parser.add_argument("-p", "--power", help="Plot Power Bands", action="store_true")
    parser.add_argument("-e", "--eeg", help="Plot EEG Data", action="store_true")
    parser.add_argument("-sr", "--sample_rate", 
            help="Sample Rate: 250 HZ, 0.5 HZ, 1.0 HZ, 2.0 HZ, 60 Sec", action="store_true")
    parser.add_argument("--plot_3D", help="3D Display Plots", action="store_true")
    parser.add_argument("-i", "--integrate", help="Integrate EEG Data", action="store_true")
    parser.add_argument("-s", "--step_size", help="Integration Step Size", type=int)
    parser.add_argument("-ps", "--power_spectrum", help="Analyze Spectrum", action="store_true")
    parser.add_argument("-f", "--filter_data", help="Filter EEG Data", action="store_true")
    parser.add_argument("-lc", "--lowcut", help="Filter Low Cuttoff Frequency",  type=float)
    parser.add_argument("-hc", "--highcut", help="Filter High Cuttoff Frequency", type=float)
    parser.add_argument("-o", "--filter_order", help="Filter Order", type=int)
    parser.add_argument("-l", "--logging_level", 
                    help="Logging verbosity: 1 = info, 2 = warning, 2 = debug", type=int)    
                                        
    args = parser.parse_args()

    if args.verbose:
        print("verbose turned on")
        print(args.verbose)
        Verbosity = args.verbose

    if args.display_plots:
        print("display_plots:")
        print(args.display_plots)


    if args.display_plots:
        print("batch:")
        print(args.batch)
        BatchMode = True

                   
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

#     try:
#         main()
#     except KeyboardInterrupt:
#         print('Interrupted')
#         try:
#             sys.exit(0)
#         except SystemExit:
#             os._exit(0)
            

    try:
        main(date_time_now)

    except KeyboardInterrupt:
            print('Interrupted')

            try:
                sys.exit(0)
            except SystemExit:

                print('Finished')
                os._exit(0)
            

#     main(date_time_now)


    sys.exit(0)


