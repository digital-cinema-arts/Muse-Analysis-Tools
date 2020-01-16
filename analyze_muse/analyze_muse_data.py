#!/usr/bin/env python3

''' 

This code will analyze Muse EEG headband CSV files and plot the results.


'''

from time import time, sleep
import datetime as dt
import numpy as np
from scipy import fftpack, interpolate
import scipy.signal as signal
from scipy import integrate, signal
from scipy.signal import butter, lfilter
import math
import bitstring
import pandas as pd
import os
from time import time, sleep, strftime, gmtime
import sys
# import csv
import argparse
# import filetype
# from tqdm import tqdm
# from progress.bar import Bar, IncrementalBar
import json
from pathlib import Path

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
from PyQt5.QtGui import QPalette, QIcon, QPixmap, QFont

from PyQt5.QtCore import QDateTime, Qt, QTimer, QUrl
from PyQt5.QtWidgets import (QApplication, QCheckBox, QComboBox, QDateTimeEdit,
        QDial, QDialog, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit,
        QProgressBar, QPushButton, QRadioButton, QScrollBar, QSizePolicy,
        QSlider, QSpinBox, QStyleFactory, QTableWidget, QTabWidget, QTextEdit,
        QVBoxLayout, QWidget)

import analyze_muse.resources.resources_rc
import analyze_muse.ABCS_version


# Globals
# Integrate_Step_Size = 4
muse_EEG_data = []
EEG_Dict ={}
eeg_stats = []
CVS_fname = ""
out_dirname = ""
EEG_data_source = 'Mind Monitor'
Sampling_Rate = 256.0
Filter_Lowcut  = 0.1
Filter_Highcut  = 100.0
Filter_Order = 3
Filter_Type = 0
NOTCH_B, NOTCH_A = butter(4, np.array([55, 65]) / (256 / 2), btype='bandstop')
Verbosity = 0
Save_DB = False
session_dict = {}
gui_dict = {}
plot_color_scheme = {}
first_name = ""
last_name = ""
data_dir = ""
db_location = ""

# Constants
ABCS_FORMAT_VERSION_NUM = 1.0
FIGURE_SIZE = (8, 6)
PLOT_DPI = 100

PLOT_PARAMS = {
    'axes.titlesize' : 8,
    'axes.labelsize' : 7,
    'lines.linewidth' : 1.0,
    'lines.markersize' : 1.5,
    'xtick.labelsize' : 7,
    'ytick.labelsize' : 7,
    'scatter.marker' : '.',
    'legend.fontsize': 6,
    'legend.handlelength': 2}

plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Tahoma', 'DejaVu Sans',
                               'Lucida Grande', 'Verdana']                               
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Tahoma']
# plt.rcParams['font.weight'] = ['bold']
plt.rcParams['font.size'] = 6


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
'RawAF7': '#19A724',
'RawAF8': '#dd172b',
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
        self.splitter = QSplitter(Qt.Horizontal)

#         print("keys: ", QStyleFactory.keys())
        
        self.createTopLeftGroupBox()
        self.createTopRightGroupBox()
#         self.createBottomLeftTabWidget()
#         self.createBottomLeftTabWidget()

        self.createBottomLeftGroupBox()

        self.createBottomRightGroupBox()
#         self.createProgressBar()

#         self.openFileNameDialog()

        topLayout = QHBoxLayout()
        topLayout.addStretch(1)

        mainLayout = QGridLayout()
        mainLayout.addLayout(topLayout, 0, 0, 1, 2)
        mainLayout.addWidget(self.topLeftGroupBox, 1, 0)
        mainLayout.addWidget(self.topRightGroupBox, 1, 1)
        mainLayout.addWidget(self.bottomRightGroupBox, 2, 1)
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
#         print("The_GUI(): self.first_name ", self.first_name)
#         print("The_GUI(): self.last_name ", self.last_name)
               
        self.setWindowTitle("Algorithmic Biofeedback Control System Plotting Tools")
        
        QApplication.setStyle(QStyleFactory.create('macintosh'))



#    def advanceProgressBar(self):
#        curVal = self.progressBar.value()
#        maxVal = self.progressBar.maximum()
#        self.progressBar.setValue(curVal + (maxVal - curVal) / 100)


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
        global Verbosity 

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
        filter_data = self.checkBoxFilter.isChecked()      
        statistical_plots = self.checkBoxStatistical.isChecked()
        muse_direct = self.checkBoxMuseDirect.isChecked()
        verbosity = self.verbosityComboBox.currentText()
        auto_reject = self.checkBoxAutoReject.isChecked()
        DB = self.checkBoxDB.isChecked()
        HDF5 = self.checkBoxHFDF5.isChecked()
        vertical_lock = self.checkBoxVerticalLock.isChecked()
        graph_markers = self.checkBoxPlotMarkers.isChecked()
        data_markers = self.checkBoxDataMarkers.isChecked()
        plot_colors = self.plotColorsComboBox.currentText()
        
        mood = self.moodComboBox.currentText()
        session_notes = self.notesTextEdit.toPlainText()
                
        gui_dict.update({'firstName': first_name,'lastName': last_name,
                "session_notes": session_notes,
                "checkBoxInteractive": interative_GUI,
                "checkBoxEEG": plot_EEG,
                "checkBoxCoherence": coherence,
                "checkBoxPowerBands": power_bands,
                "checkBoxMellowConcentration": mellow_concentrate,
                "checkBoxAccelGyro": accel_gyro,
                "checkBox3D": plot_3D,
                "checkBoxFilter": filter_data,                
                "checkBoxStatistical": statistical_plots,
                "checkBoxMuseDirect": muse_direct,
                "verbosityComboBox": verbosity,
                "checkBoxAutoReject": auto_reject,
                "checkBoxDB": DB,
                "checkBoxHFDF5": HDF5,
                "checkBoxVerticalLock": vertical_lock,
                "checkBoxPlotMarkers": graph_markers,
                "checkBoxDataMarkers": data_markers,
                "plotColorsComboBox": plot_colors,               
                "Mood": mood})

# TODO Sort out this switch for interactive plots and batch mode ... 
        args.display_plots = gui_dict['checkBoxInteractive']
        
        if gui_dict['verbosityComboBox'] == 'Quiet':
            Verbosity = 0
        if gui_dict['verbosityComboBox'] == 'Informative':
            Verbosity = 1
        if gui_dict['verbosityComboBox'] == 'Verbose':
            Verbosity = 2
        if gui_dict['verbosityComboBox'] == 'Debug':
            Verbosity = 3

        if Verbosity > 2:
            print("plot_button_clicked(): gui_dict ", gui_dict)
        
        self.accept()

         
    

    def createTopLeftGroupBox(self):
        self.topLeftGroupBox = QGroupBox("Select Options")
        self.topLeftGroupBox.setStyleSheet("color: black; background-color: #F0F0F8;")
 
# setStyleSheet("color: black;"
#                         "background-color: yellow;"
#                         "selection-color: yellow;"
#                         "selection-background-color: black;");
 
        layout = QVBoxLayout()

        self.checkBoxInteractive = QCheckBox("Display Interactive Plots")
        self.checkBoxInteractive.setChecked(args.display_plots)
        self.checkBoxInteractive.setEnabled(True)

        self.checkBoxEEG = QCheckBox("Create EEG Plots")
        self.checkBoxEEG.setChecked(True)
        self.checkBoxEEG.setEnabled(True)
        
        self.checkBoxCoherence = QCheckBox("Create Coherence Plots")
        self.checkBoxCoherence.setChecked(args.coherence_plots)
        self.checkBoxCoherence.setEnabled(True)
        
        self.checkBoxPowerBands = QCheckBox("Create Power Bands Plots")
        self.checkBoxPowerBands.setChecked(True)
        self.checkBoxPowerBands.setEnabled(True)
        
        self.checkBoxMellowConcentration = QCheckBox("Create Mellow/Concentration Plots")
        self.checkBoxMellowConcentration.setChecked(args.mellow_concentration)
        self.checkBoxMellowConcentration.setEnabled(True)

        self.checkBoxAccelGyro = QCheckBox("Create Accleration/Gyro Plots")
        self.checkBoxAccelGyro.setChecked(args.accel_gyro)
        self.checkBoxAccelGyro.setEnabled(True)

        self.checkBox3D = QCheckBox("Create 3D Plots")
        self.checkBox3D.setChecked(False)
        self.checkBox3D.setEnabled(False)

        self.checkBoxFilter = QCheckBox("Filter Data")
        self.checkBoxFilter.setChecked(args.filter_data)
        self.checkBoxFilter.setEnabled(True)

        self.checkBoxResample = QCheckBox("Resample Data")
        self.checkBoxResample.setChecked(False)
        self.checkBoxResample.setEnabled(False)

        self.checkBoxMuseDirect = QCheckBox("Include Muse Direct Plots")
        self.checkBoxMuseDirect.setChecked(False)
        self.checkBoxMuseDirect.setEnabled(False)

        self.checkBoxStatistical = QCheckBox("Include Statistical Plots")
        self.checkBoxStatistical.setChecked(args.stats_plots)
        self.checkBoxStatistical.setEnabled(True)

        self.checkBoxAutoReject = QCheckBox("Auto-Reject EEG Data")
        self.checkBoxAutoReject.setChecked(args.auto_reject_data)
        self.checkBoxAutoReject.setEnabled(True)

        self.checkBoxDB = QCheckBox("Send Results to Database")
        self.checkBoxDB.setChecked(args.data_base)
        self.checkBoxDB.setEnabled(True)

        self.checkBoxHFDF5 = QCheckBox("Write HDF5 File")
        self.checkBoxHFDF5.setChecked(args.write_hdf5_file)
        self.checkBoxHFDF5.setEnabled(True)
  
        self.plotColorsComboBox = QComboBox()
        self.plotColorsComboBox.addItems(['ABCS Colors', 'Mind Monitor Colors'])
        self.plotColorsLabel = QtWidgets.QLabel(self)
        self.plotColorsLabel.setText('Set Plot Color Scheme')

        self.checkBoxVerticalLock = QCheckBox("Y Axis Lock")
        self.checkBoxVerticalLock.setChecked(True)
        self.checkBoxVerticalLock.setEnabled(True)

        self.checkBoxPlotMarkers = QCheckBox("Add Plot Markers")
        self.checkBoxPlotMarkers.setChecked(False)
        self.checkBoxPlotMarkers.setEnabled(True)
  
        self.checkBoxDataMarkers = QCheckBox("Add Data Markers")
        self.checkBoxDataMarkers.setChecked(args.data_markers)
        self.checkBoxDataMarkers.setEnabled(True)
  
        layout.addWidget(self.checkBoxInteractive)
        layout.addWidget(self.checkBoxEEG)
        layout.addWidget(self.checkBoxCoherence)
        layout.addWidget(self.checkBoxPowerBands)
        layout.addWidget(self.checkBoxMellowConcentration)
        layout.addWidget(self.checkBoxAccelGyro)
#         layout.addWidget(self.checkBox3D)
        layout.addWidget(self.checkBoxStatistical)
#         layout.addWidget(self.checkBoxMuseDirect)
        layout.addWidget(self.checkBoxFilter)
#         layout.addWidget(self.checkBoxResample)
        layout.addWidget(self.checkBoxAutoReject)
        layout.addWidget(self.checkBoxDB)
        layout.addWidget(self.checkBoxHFDF5)
        layout.addWidget(self.checkBoxHFDF5)
        layout.addWidget(self.checkBoxVerticalLock)        
        layout.addWidget(self.checkBoxPlotMarkers)        
        layout.addWidget(self.checkBoxDataMarkers)        
 
        layout.addWidget(self.plotColorsLabel)
        layout.addWidget(self.plotColorsComboBox)

#         layout.addWidget(self.verbosityLabel)

        layout.addStretch(1)
        self.topLeftGroupBox.setLayout(layout)    



    def createTopRightGroupBox(self):
        self.topRightGroupBox = QGroupBox("Meditation Session Details")
        self.topRightGroupBox.setStyleSheet("color: black; background-color: #F0F0F8;")

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

        self.labelNotes = QtWidgets.QLabel(self)
        self.labelNotes.setText('Session Notes')

        self.notesTextEdit = QTextEdit()
        self.notesTextEdit.setPlainText("Add any details about your meditation session.  "
                              "For example, mood, place, music, etc.\n")

        layout.addWidget(self.lineFirstNameEdit)
        layout.addWidget(self.lineLastNameEdit)
        layout.addWidget(self.dateTimeEdit)
        layout.addWidget(self.splitter)        

#         layout.addWidget(self.moodLabel)
        layout.addWidget(moodLabel)
        layout.addWidget(self.moodComboBox)
        layout.addWidget(self.labelNotes)
        layout.addWidget(self.notesTextEdit)
#         layout.addWidget(linePasswordEdit, 3, 0, 1, 2)
                    
        self.topRightGroupBox.setLayout(layout)




    def createBottomRightGroupBox(self):
        self.bottomRightGroupBox = QGroupBox("Breathe")
#         self.bottomRightGroupBox.setStyleSheet("background-color: #c2bc9b;")


        layout = QVBoxLayout()

#         self.im = QPixmap("./sanctuary1.jpg")
        self.im = QPixmap(":/images/sanctuary1.jpg")
  
        self.im = self.im.scaled(256, 256, Qt.KeepAspectRatio, Qt.FastTransformation)
        self.label = QtWidgets.QLabel()
        self.label.setPixmap(self.im)
        layout.addWidget(self.label)

        layout.addStretch(1)
        self.bottomRightGroupBox.setLayout(layout)    



    def createBottomLeftGroupBox(self):
        self.bottomLeftGroupBox = QGroupBox("Create Plots")
        self.bottomLeftGroupBox.setStyleSheet("color: black; background-color: #F0F0F8;")

        self.filePushButton = QPushButton("Select Data File")
        self.filePushButton.clicked.connect(self.file_button_clicked)
        self.filePushButton.setStyleSheet("color: black; background-color: #b69bc2;")
#         filePushButton.setDefault(False)

        self.plotPushButton = QPushButton("Create Plots")
        self.plotPushButton.setDefault(True)
        self.plotPushButton.setStyleSheet("color: black; background-color: #9bb4c2;")
        self.plotPushButton.clicked.connect(self.plot_button_clicked)

        self.verbosityComboBox = QComboBox()
        self.verbosityComboBox.addItems(['Quiet', 'Informative', 'Verbose', 'Debug'])
        self.verbosityLabel = QtWidgets.QLabel(self)
        self.verbosityLabel.setText('Set Verbosity')
        self.verbosityLabel.setAlignment(Qt.AlignCenter)
        self.verbosityComboBox.setCurrentIndex(args.verbose)
#         self.verbosityComboBox.setCurrentIndex(0)

        self.versionLabel = QtWidgets.QLabel(self)
        self.versionLabel.setText('Version: ' + str(analyze_muse.ABCS_version.ABCS_version))
        self.versionLabel.setAlignment(Qt.AlignCenter)
        self.versionLabel.setFont(QFont("Tahoma", 10, QFont.Light))


#         self.labelChooseFile = QLabel(self)
#         self.labelChooseFile.setText("Choose File")
#         self.labelChooseFile.setAlignment(Qt.AlignCenter)

        layout = QVBoxLayout()
        layout.addWidget(self.splitter)
#         layout.addWidget(self.labelChooseFile)
        layout.addWidget(self.filePushButton)
        layout.addWidget(self.splitter)
        layout.addWidget(self.verbosityLabel)
        layout.addWidget(self.verbosityComboBox)
        layout.addWidget(self.splitter)        
        layout.addWidget(self.plotPushButton)
        layout.addWidget(self.splitter)        
        layout.addWidget(self.versionLabel)        

        layout.addStretch(1)
        self.bottomLeftGroupBox.setLayout(layout)



#    def createProgressBar(self):
#        self.progressBar = QProgressBar()
#        self.progressBar.setRange(0, 10000)
#        self.progressBar.setValue(0)

#        timer = QTimer(self)
#        timer.timeout.connect(self.advanceProgressBar)
#        timer.start(1000)



    def openFileNameDialog(self):
        options = QFileDialog.Options()

# TODO Figure out proper use of QFileDialog.DontUseNativeDialog
        options |= QFileDialog.DontUseNativeDialog

#         if sys.platform in ['linux', 'linux2', 'win32']:
#            options |= QFileDialog.DontUseNativeDialog

        
#         place = os.getcwd()
        place = os.sep.join((os.path.expanduser('~'), 'Desktop'))

        dialog = QFileDialog(self)
        dialog.setFileMode(QFileDialog.AnyFile)
#         dialog.setSidebarUrls([QUrl.fromLocalFile(data_dir)])
#         dialog.setSidebarUrls([QUrl.fromLocalFile(place)])       
#         dialog.setDirectory(data_dir) 

        file_filter = "CSV files (*.csv);;GZIP files (*.gz);;ZIP files (*.zip)"
#         file_filter = "Images (*.png *.xpm .jpg);;Text files (.txt);;XML files (*.xml)"

        fileName, _ = dialog.getOpenFileName(self,
                        "Select EEG CSV File", 
                        data_dir, file_filter, 
                        options=options)

        if fileName:
            if Verbosity > 1:
                print(fileName)
            
        global gui_dict    
        global CVS_fname 
        CVS_fname = fileName
    
        gui_dict = {'fileName': CVS_fname}
  
  
    
    def saveFileDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getSaveFileName(self,
        "Select Output file","","All Files (*);;PNG Files (*.png)", options=options)
        if fileName:
            if Verbosity > 1:
                print(fileName)
            
            
            

'''

Manage session data 

'''

def manage_session_data(init=False, new_data={}, session_date='', date_time=''):

    if Verbosity > 0:
        print("manage_session_data()")

    global session_dict
    global EEG_Dict

    if init:

        if Verbosity > 1:
            print("manage_session_data(): Initialize Session Data")

        # Fill in default values for now.  
        session_dict = {
            'ABCS Info':{'Version':ABCS_FORMAT_VERSION_NUM},
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

def connect_to_DB(date_time_now):
#     import mysql.connector
    import sqlite3

    if Verbosity > 0:
        print("connect_to_DB(): Sending data to database ...")

    db_fname = db_location + '/EEG_data.db'

    # If the database does not exist, create it
    if os.path.exists(db_fname):

        if Verbosity > 0:
            print("connect_to_DB(): Database exists ...")

    else:
    
        if Verbosity > 0:
            print("connect_to_DB(): Creating new database ...")
        conn = sqlite3.connect(db_fname)
        c = conn.cursor()

        c.execute('''CREATE TABLE eeg_data
                     (date text, type text, data_type text, average real, std real)''')


    conn = sqlite3.connect(db_fname)
    c = conn.cursor()

    sql_insert = "INSERT INTO eeg_data VALUES ( '" + date_time_now + "','" + \
                        json.dumps(session_dict) + "','" + json.dumps(gui_dict) + "', 100, 0.05)"


    if Verbosity > 2:
        print("connect_to_DB() - sql_insert: ", sql_insert)
    
    c.execute(sql_insert)
    conn.commit()
        
    conn.close()
    if Verbosity > 1:
        print("connect_to_DB(): Closed DB")


    return True





def initialize_EEG_dict():
   
    if Verbosity > 0:
        print("initialize_EEG_dict()")


    if EEG_data_source == 'Mind Monitor':

        data_keys = ['Delta_TP9', 'Delta_AF7', 'Delta_AF8', 'Delta_TP10',
                    'Theta_TP9', 'Theta_AF7', 'Theta_AF8', 'Theta_TP10',
                    'Alpha_TP9', 'Alpha_AF7', 'Alpha_AF8', 'Alpha_TP10',
                    'Beta_TP9', 'Beta_AF7', 'Beta_AF8', 'Beta_TP10',                        
                    'Gamma_TP9', 'Gamma_AF7', 'Gamma_AF8', 'Gamma_TP10']
        
        for key in data_keys:
            EEG_Dict[key] = None
#             print("initialize_EEG_dict() - key, EEG_Dict[key]: ", key, EEG_Dict[key])
        

    return True



   

'''

Read EEG data from disk. 

'''

def read_eeg_data(fname, date_time_now):
   
    if Verbosity > 0:
        print("read_eeg_data(): Reading EEG data ...")

    global session_dict
    global EEG_Dict

    initialize_EEG_dict()

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


#     kind = filetype.guess(fname)
#     if kind is None:
#         if Verbosity > 2:
#             print("read_eeg_data(): Cannot guess file type!")
#     else:
# 
#         if Verbosity > 1:    
#             print('read_eeg_data(): File extension: %s' % kind.extension)
#             print('read_eeg_data(): File MIME type: %s' % kind.mime)

 
#     dtypes={'TimeStamp': 'str', 
#             'Delta_TP9': 'float', 
#             'Delta_AF7': 'float', 
#             'Delta_AF8': 'float', 
#             'Delta_TP10': 'float',
#             'Theta_TP9': 'float', 
#             'Theta_AF7': 'float', 
#             'Theta_AF8': 'float', 
#             'Theta_TP10': 'float',
#             'Alpha_TP9': 'float', 
#             'Alpha_AF7': 'float', 
#             'Alpha_AF8': 'float', 
#             'Alpha_TP10': 'float',
#             'Beta_TP9': 'float', 
#             'Beta_AF7': 'float', 
#             'Beta_AF8': 'float', 
#             'Beta_TP10': 'float',
#             'Gamma_TP9': 'float', 
#             'Gamma_AF7': 'float', 
#             'Gamma_AF8': 'float', 
#             'Gamma_TP10': 'float',
#             'RAW_TP9': 'float', 
#             'RAW_AF7': 'float', 
#             'RAW_AF8': 'float', 
#             'RAW_TP10': 'float',
#             'Mellow': 'float', 
#             'Concentration': 'float', 
#             'Accelerometer_X': 'float', 
#             'Accelerometer_Y': 'float', 
#             'Accelerometer_Z': 'float', 
#             'Gyro_X': 'float', 
#             'Gyro_Y': 'float', 
#             'Gyro_Z': 'float', 
#             'HeadBandOn': 'float', 
#             'HSI_TP9': 'float', 
#             'HSI_AF7': 'float', 
#             'HSI_AF8': 'float', 
#             'HSI_TP10': 'float', 
#             'Battery': 'float', 
#             'Elements': 'str'
#             }

#     csv_data = pd.read_csv(fname, parse_dates=['TimeStamp'], 
# #                     date_parser=pd.to_datetime, compression='infer')
#                     date_parser=pd.to_datetime, dtype=dtypes, compression='infer')
#     num_cols = len(csv_data.columns)
    
    dtypes={'TimeStamp': 'str', 
            'Battery': 'float',
            'Elements': 'str'
            }

#     csv_data = pd.read_csv(fname, parse_dates=['TimeStamp'], 
#                     date_parser=pd.to_datetime, dtype=dtypes, compression='infer')    
    
# df = pd.read_csv('filename.tar.gz', compression='gzip', header=0, sep=',', quotechar='"')
    muse_EEG_data = pd.read_csv(fname,  parse_dates=['TimeStamp'], 
                        date_parser=pd.to_datetime, dtype=dtypes, 
                        compression='infer', verbose=Verbosity)

    num_cols = len(muse_EEG_data.columns)

    time_df = pd.DataFrame(muse_EEG_data, columns=['TimeStamp'])    
    if Verbosity > 2:
        print("read_eeg_data(): Session Date: ", time_df['TimeStamp'][0])
        print("read_eeg_data(): num_cols: ", num_cols)
        print("read_eeg_data(): time_df.shape: ", time_df.shape)
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


#     Scale Mind Monitor brainwave data 
    if EEG_data_source == 'Mind Monitor':

        data_keys = ['Delta_TP9', 'Delta_AF7', 'Delta_AF8', 'Delta_TP10',
                    'Theta_TP9', 'Theta_AF7', 'Theta_AF8', 'Theta_TP10',
                    'Alpha_TP9', 'Alpha_AF7', 'Alpha_AF8', 'Alpha_TP10',
                    'Beta_TP9', 'Beta_AF7', 'Beta_AF8', 'Beta_TP10',                        
                    'Gamma_TP9', 'Gamma_AF7', 'Gamma_AF8', 'Gamma_TP10']
#         y = ((x + 1.0) * 50)

        for data_col in data_keys:       
            muse_EEG_data[data_col] += 1.0
            muse_EEG_data[data_col] *= 50.


    elements_df = pd.DataFrame(muse_EEG_data, columns=['TimeStamp', 'Elements'])

    if Verbosity > 2:
#         print("read_eeg_data() - Elements.describe(): ", elements_df.describe())   
        print("read_eeg_data() - elements_df.count(): ", elements_df.count())


 # TODO: Insert markers 
    
    elements_df['Elements'] = elements_df.Elements.astype(str)

#     for index, row in elements_df.iterrows():
#         if row['Elements'] != 'nan':
#             print(row['TimeStamp'])
#             print(row['Elements'])

# 
#     for temp_df in (raw_df, delta_df, theta_df, alpha_df, beta_df, gamma_df):
# #         if args.verbose:
# #             print("verbose turned on")
# 
#         if Verbosity > 2:
#             print("read_eeg_data(): Sensor data description", temp_df.describe())
# #         data_str = temp_df.mean()
#         data_str = temp_df.describe()
# #         print("type", type(data_str))
# #         print("data_str.index", data_str.index)
#         EEG_Dict.update(data_str.to_dict())
# #         print("EEG_Dict: ", EEG_Dict)
# #         print("data_str.to_dict()", data_str.to_dict())
#     


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

    session_json = json.dumps(session_dict, sort_keys=True)

    global out_dirname
    
    # Save the session data to a JSON file
    session_data_fname = out_dirname + "/session_data/EEG_session_data-" + date_time_now + ".json"
    
    ensure_dir(out_dirname + "/session_data/")
    data_file=open(session_data_fname,"w+")
#     pwr_data_file=open("EEG_power_data.txt","w+")

    data_file.write(session_json)
    data_file.close()
    

    return(muse_EEG_data, EEG_Dict)





def get_data_description(muse_EEG_data):

    if Verbosity > 1:
        print("get_data_description()")

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


    for temp_df in (raw_df, delta_df, theta_df, alpha_df, beta_df, gamma_df):

        if Verbosity > 2:
            print("get_data_description(): Sensor data description", temp_df.describe())
#         data_str = temp_df.mean()
        data_str = temp_df.describe()

        EEG_Dict.update(data_str.to_dict())
                
        for key,val in EEG_Dict.items():
            EEG_Dict[key] = val


    return True




'''

Auto reject that exceeds min/max limits.  

'''
def auto_reject_EEG_data(data):

    if Verbosity > 0:
        print("auto_reject_EEG_data()")


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

    eeg_clip_padding = 50.
    pwr_clip_padding = 0.01
    
    new_df = data.loc[data['RAW_TP9'] <  (EEG_Dict['RAW_TP9']['75%'] + eeg_clip_padding)]
    new_df = new_df.loc[new_df['RAW_TP9'] >  (EEG_Dict['RAW_TP9']['25%'] - eeg_clip_padding)]

    new_df = new_df.loc[new_df['RAW_AF7'] <  (EEG_Dict['RAW_AF7']['75%'] + eeg_clip_padding)]
    new_df = new_df.loc[new_df['RAW_AF7'] >  (EEG_Dict['RAW_AF7']['25%'] - eeg_clip_padding)]

    new_df = new_df.loc[new_df['RAW_AF8'] <  (EEG_Dict['RAW_AF8']['75%'] + eeg_clip_padding)]
    new_df = new_df.loc[new_df['RAW_AF8'] >  (EEG_Dict['RAW_AF8']['25%'] - eeg_clip_padding)]

    new_df = new_df.loc[new_df['RAW_TP10'] <  (EEG_Dict['RAW_TP10']['75%'] + eeg_clip_padding)]
    new_df = new_df.loc[new_df['RAW_TP10'] >  (EEG_Dict['RAW_TP10']['25%'] - eeg_clip_padding)]


    return new_df
    


'''
 
 Write out on HDF5 data file of the data that was plotted
 
''' 
def write_hdf5_data(muse_EEG_data, data_fname):

    import h5py, tables

    if Verbosity > 0:
        print("write_hdf5_data()")

    global session_dict
    global EEG_Dict

    df = pd.DataFrame(muse_EEG_data, columns=['TimeStamp', 'RAW_TP9', 'RAW_AF7', 'RAW_AF8', 'RAW_TP10'])    

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

    motion_df = pd.DataFrame(muse_EEG_data, columns=[
                    'Accelerometer_X', 'Accelerometer_Y', 'Accelerometer_Z', 
                    'Gyro_X', 'Gyro_Y', 'Gyro_Z'])    

    basename = os.path.basename(data_fname)

    data_stats = (EEG_Dict['RAW_AF7']['25%'], EEG_Dict['RAW_AF7']['75%'],
                EEG_Dict['RAW_AF8']['25%'], EEG_Dict['RAW_AF8']['75%'],
                EEG_Dict['RAW_TP9']['25%'], EEG_Dict['RAW_TP9']['75%'],
                EEG_Dict['RAW_TP10']['25%'], EEG_Dict['RAW_TP10']['75%'])


    if Verbosity > 1:
        print("write_hdf5_data() - data_fname: ", data_fname)
        print("write_hdf5_data() - basename: ", basename)

    
    with h5py.File(data_fname, 'w') as f:
        g_base = f.create_group('abcs_base')
        g_stats = g_base.create_group('stats')
        g_raw = g_base.create_group('raw')
        g_power = g_base.create_group('power')
        g_motion = g_base.create_group('motion')

        stats = g_stats.create_dataset('stats', compression="gzip", compression_opts=9,
                    data=(data_stats))
#         for k, v in EEG_Dict.items():
#             print("write_hdf5_data() -  k, v: ",  k, v)
#             g_stats.create_dataset(k, data=np.array(v))
#             g_stats.create_dataset(k, data=np.array(23))
        

        delta = g_power.create_dataset('p_delta', dtype='f8', compression="gzip", compression_opts=9,
                    data=(delta_df['Delta_TP9'], delta_df['Delta_AF7'],
                    delta_df['Delta_AF8'], delta_df['Delta_TP10']))
        theta = g_power.create_dataset('p_theta', dtype='f8', compression="gzip", compression_opts=9,
                    data=(theta_df['Theta_TP9'], theta_df['Theta_AF7'],
                    theta_df['Theta_AF8'], theta_df['Theta_TP10']))
        alpha = g_power.create_dataset('p_alpha', dtype='f8', compression="gzip", compression_opts=9,
                    data=(alpha_df['Alpha_TP9'], alpha_df['Alpha_AF7'],
                    alpha_df['Alpha_AF8'], alpha_df['Alpha_TP10']))
        beta = g_power.create_dataset('p_beta', dtype='f8', compression="gzip", compression_opts=9,
                    data=(beta_df['Beta_TP9'], beta_df['Beta_AF7'],
                    beta_df['Beta_AF8'], beta_df['Beta_TP10']))
        gamma = g_power.create_dataset('p_gamma', dtype='f8', compression="gzip", compression_opts=9,
                    data=(gamma_df['Gamma_TP9'], gamma_df['Gamma_AF7'],
                    gamma_df['Gamma_AF8'], gamma_df['Gamma_TP10']))
       
        raw = g_raw.create_dataset('raw', dtype='f8', compression="gzip", compression_opts=9,
                    data=(df['RAW_TP9'], df['RAW_AF7'], df['RAW_AF8'], df['RAW_TP10']))
       
        accel = g_motion.create_dataset('accel', dtype='f8', compression="gzip", compression_opts=9,
                    data=(motion_df['Accelerometer_X'], motion_df['Accelerometer_Y'], motion_df['Accelerometer_Z']))

        gyro = g_motion.create_dataset('gyro', dtype='f8', compression="gzip", compression_opts=9,
                    data=(motion_df['Gyro_X'], motion_df['Gyro_Y'], motion_df['Gyro_Z']))



    return True
    

                    


'''

Scale data 

'''
def scale(x, out_range=(-1, 1), axis=None):

    # Get the min and max of the data 
    domain = np.min(x, axis), np.max(x, axis)
    # Normalize to +-0.5
    y = (x - (domain[1] + domain[0]) / 2) / (domain[1] - domain[0])
    # Scale and add offset
    
    return y * (out_range[1] - out_range[0]) + (out_range[1] + out_range[0]) / 2




'''

Tail-rolling average transform 

'''
def smooth_data(data_in, win):
    rolling = data_in.rolling(window=win)
    smoothed_data = rolling.mean()

    return smoothed_data




def filter_all_data(muse_EEG_data):

    if Verbosity > 0:
        print('filter_all_data() called')

    smooth_sz = 1
    
    # Default filter
#     if False:
    if Filter_Type == 0:
        muse_EEG_data['RAW_TP9'] = filter_data(muse_EEG_data['RAW_TP9'])
        muse_EEG_data['RAW_AF7'] = filter_data(muse_EEG_data['RAW_AF7'])
        muse_EEG_data['RAW_AF8'] = filter_data(muse_EEG_data['RAW_AF8'])
        muse_EEG_data['RAW_TP10'] = filter_data(muse_EEG_data['RAW_TP10'])

        if Verbosity > 2:
            print('filter_all_data() finished filtering raw data')
    
        muse_EEG_data['Delta_TP9'] = filter_data(muse_EEG_data['Delta_TP9'])
        muse_EEG_data['Delta_AF7'] = filter_data(muse_EEG_data['Delta_AF7'])
        muse_EEG_data['Delta_AF8'] = filter_data(muse_EEG_data['Delta_AF8'])
        muse_EEG_data['Delta_TP10'] = filter_data(muse_EEG_data['Delta_TP10'])

        if Verbosity > 2:
            print('filter_all_data() finished filtering delta data')

        muse_EEG_data['Theta_TP9'] = filter_data(muse_EEG_data['Theta_TP9'])
        muse_EEG_data['Theta_AF7'] = filter_data(muse_EEG_data['Theta_AF7'])
        muse_EEG_data['Theta_AF8'] = filter_data(muse_EEG_data['Theta_AF8'])
        muse_EEG_data['Theta_TP10'] = filter_data(muse_EEG_data['Theta_TP10'])

        if Verbosity > 2:
            print('filter_all_data() finished filtering theta data')

        muse_EEG_data['Alpha_TP9'] = filter_data(muse_EEG_data['Alpha_TP9'])
        muse_EEG_data['Alpha_AF7'] = filter_data(muse_EEG_data['Alpha_AF7'])
        muse_EEG_data['Alpha_AF8'] = filter_data(muse_EEG_data['Alpha_AF8'])
        muse_EEG_data['Alpha_TP10'] = filter_data(muse_EEG_data['Alpha_TP10'])

        if Verbosity > 2:
            print('filter_all_data() finished filtering alpha data')

        muse_EEG_data['Beta_TP9'] = filter_data(muse_EEG_data['Beta_TP9'])
        muse_EEG_data['Beta_AF7'] = filter_data(muse_EEG_data['Beta_AF7'])
        muse_EEG_data['Beta_AF8'] = filter_data(muse_EEG_data['Beta_AF8'])
        muse_EEG_data['Beta_TP10'] = filter_data(muse_EEG_data['Beta_TP10'])

        if Verbosity > 2:
            print('filter_all_data() finished filtering beta data')

        muse_EEG_data['Gamma_TP9'] = filter_data(muse_EEG_data['Gamma_TP9'])
        muse_EEG_data['Gamma_AF7'] = filter_data(muse_EEG_data['Gamma_AF7'])
        muse_EEG_data['Gamma_AF8'] = filter_data(muse_EEG_data['Gamma_AF8'])
        muse_EEG_data['Gamma_TP10'] = filter_data(muse_EEG_data['Gamma_TP10'])

        if Verbosity > 2:
            print('filter_all_data() finished filtering gamma data')

#         muse_EEG_data['Accelerometer_X'] = filter_data(muse_EEG_data['Accelerometer_X'])
#         muse_EEG_data['Accelerometer_Y'] = filter_data(muse_EEG_data['Accelerometer_Y'])
#         muse_EEG_data['Accelerometer_Z'] = filter_data(muse_EEG_data['Accelerometer_Z'])
#         muse_EEG_data['Gyro_X'] = filter_data(muse_EEG_data['Gyro_X'])
#         muse_EEG_data['Gyro_Y'] = filter_data(muse_EEG_data['Gyro_Y'])
#         muse_EEG_data['Gyro_Z'] = filter_data(muse_EEG_data['Gyro_Z'])
# 
#         if Verbosity > 2:
#             print('filter_all_data() finished filtering accel & gyro data')

    # Low pass filter
    if Filter_Type == 1:
        muse_EEG_data['RAW_TP9'] = butter_lowpass_filter(muse_EEG_data['RAW_TP9'], 
                                        Filter_Highcut, Sampling_Rate, Filter_Order)
        muse_EEG_data['RAW_AF7'] = butter_lowpass_filter(muse_EEG_data['RAW_AF7'], 
                                        Filter_Highcut, Sampling_Rate, Filter_Order)
        muse_EEG_data['RAW_AF8'] = butter_lowpass_filter(muse_EEG_data['RAW_AF8'], 
                                        Filter_Highcut, Sampling_Rate, Filter_Order)
        muse_EEG_data['RAW_TP10'] = butter_lowpass_filter(muse_EEG_data['RAW_TP10'], 
                                        Filter_Highcut, Sampling_Rate, Filter_Order)

        if Verbosity > 2:
            print('filter_all_data() finished filtering raw data')
    
        muse_EEG_data['Delta_TP9'] = butter_lowpass_filter(muse_EEG_data['Delta_TP9'], 
                                        Filter_Highcut, Sampling_Rate, Filter_Order)
        muse_EEG_data['Delta_AF7'] = butter_lowpass_filter(muse_EEG_data['Delta_AF7'], 
                                        Filter_Highcut, Sampling_Rate, Filter_Order)
        muse_EEG_data['Delta_AF8'] = butter_lowpass_filter(muse_EEG_data['Delta_AF8'], 
                                        Filter_Highcut, Sampling_Rate, Filter_Order)
        muse_EEG_data['Delta_TP10'] = butter_lowpass_filter(muse_EEG_data['Delta_TP10'], 
                                        Filter_Highcut, Sampling_Rate, Filter_Order)

        if Verbosity > 2:
            print('filter_all_data() finished filtering delta data')

        muse_EEG_data['Theta_TP9'] = butter_lowpass_filter(muse_EEG_data['Theta_TP9'], 
                                        Filter_Highcut, Sampling_Rate, Filter_Order)
        muse_EEG_data['Theta_AF7'] = butter_lowpass_filter(muse_EEG_data['Theta_AF7'], 
                                        Filter_Highcut, Sampling_Rate, Filter_Order)
        muse_EEG_data['Theta_AF8'] = butter_lowpass_filter(muse_EEG_data['Theta_AF8'], 
                                        Filter_Highcut, Sampling_Rate, Filter_Order)
        muse_EEG_data['Theta_TP10'] = butter_lowpass_filter(muse_EEG_data['Theta_TP10'], 
                                        Filter_Highcut, Sampling_Rate, Filter_Order)

        if Verbosity > 2:
            print('filter_all_data() finished filtering theta data')

        muse_EEG_data['Alpha_TP9'] = butter_lowpass_filter(muse_EEG_data['Alpha_TP9'], 
                                        Filter_Highcut, Sampling_Rate, Filter_Order)
        muse_EEG_data['Alpha_AF7'] = butter_lowpass_filter(muse_EEG_data['Alpha_AF7'], 
                                        Filter_Highcut, Sampling_Rate, Filter_Order)
        muse_EEG_data['Alpha_AF8'] = butter_lowpass_filter(muse_EEG_data['Alpha_AF8'], 
                                        Filter_Highcut, Sampling_Rate, Filter_Order)
        muse_EEG_data['Alpha_TP10'] = butter_lowpass_filter(muse_EEG_data['Alpha_TP10'], 
                                        Filter_Highcut, Sampling_Rate, Filter_Order)

        if Verbosity > 2:
            print('filter_all_data() finished filtering alpha data')

        muse_EEG_data['Beta_TP9'] = butter_lowpass_filter(muse_EEG_data['Beta_TP9'], 
                                        Filter_Highcut, Sampling_Rate, Filter_Order)
        muse_EEG_data['Beta_AF7'] = butter_lowpass_filter(muse_EEG_data['Beta_AF7'], 
                                        Filter_Highcut, Sampling_Rate, Filter_Order)
        muse_EEG_data['Beta_AF8'] = butter_lowpass_filter(muse_EEG_data['Beta_AF8'], 
                                        Filter_Highcut, Sampling_Rate, Filter_Order)
        muse_EEG_data['Beta_TP10'] = butter_lowpass_filter(muse_EEG_data['Beta_TP10'], 
                                        Filter_Highcut, Sampling_Rate, Filter_Order)

        if Verbosity > 2:
            print('filter_all_data() finished filtering beta data')

        muse_EEG_data['Gamma_TP9'] = butter_lowpass_filter(muse_EEG_data['Gamma_TP9'], 
                                        Filter_Highcut, Sampling_Rate, Filter_Order)
        muse_EEG_data['Gamma_AF7'] = butter_lowpass_filter(muse_EEG_data['Gamma_AF7'], 
                                        Filter_Highcut, Sampling_Rate, Filter_Order)
        muse_EEG_data['Gamma_AF8'] = butter_lowpass_filter(muse_EEG_data['Gamma_AF8'], 
                                        Filter_Highcut, Sampling_Rate, Filter_Order)
        muse_EEG_data['Gamma_TP10'] = butter_lowpass_filter(muse_EEG_data['Gamma_TP10'], 
                                        Filter_Highcut, Sampling_Rate, Filter_Order)

        if Verbosity > 2:
            print('filter_all_data() finished filtering gamma data')

#         muse_EEG_data['Accelerometer_X'] = butter_lowpass_filter(muse_EEG_data['Accelerometer_X'], 
#                                         Filter_Highcut, Sampling_Rate, Filter_Order)
#         muse_EEG_data['Accelerometer_Y'] = butter_lowpass_filter(muse_EEG_data['Accelerometer_Y'], 
#                                         Filter_Highcut, Sampling_Rate, Filter_Order)
#         muse_EEG_data['Accelerometer_Z'] = butter_lowpass_filter(muse_EEG_data['Accelerometer_Z'], 
#                                         Filter_Highcut, Sampling_Rate, Filter_Order)
#         muse_EEG_data['Gyro_X'] = butter_lowpass_filter(muse_EEG_data['Gyro_X'], 
#                                         Filter_Highcut, Sampling_Rate, Filter_Order)
#         muse_EEG_data['Gyro_Y'] = butter_lowpass_filter(muse_EEG_data['Gyro_Y'], 
#                                         Filter_Highcut, Sampling_Rate, Filter_Order)
#         muse_EEG_data['Gyro_Z'] = butter_lowpass_filter(muse_EEG_data['Gyro_Z'], 
#                                         Filter_Highcut, Sampling_Rate, Filter_Order)
# 
#         if Verbosity > 2:
#             print('filter_all_data() finished filtering accel & gyro data')



    # Band pass filter
    if Filter_Type == 2:
        muse_EEG_data['RAW_TP9'] = butter_bandpass_filter(muse_EEG_data['RAW_TP9'], 
                                            Filter_Lowcut, Filter_Highcut, Sampling_Rate, Filter_Order) 
        muse_EEG_data['RAW_AF7'] = butter_bandpass_filter(muse_EEG_data['RAW_AF7'], 
                                            Filter_Lowcut, Filter_Highcut, Sampling_Rate, Filter_Order) 
        muse_EEG_data['RAW_AF8'] = butter_bandpass_filter(muse_EEG_data['RAW_AF8'], 
                                            Filter_Lowcut, Filter_Highcut, Sampling_Rate, Filter_Order) 
        muse_EEG_data['RAW_TP10'] = butter_bandpass_filter(muse_EEG_data['RAW_TP10'], 
                                            Filter_Lowcut, Filter_Highcut, Sampling_Rate, Filter_Order) 

        if Verbosity > 2:
            print('filter_all_data() finished filtering raw data')
    
        muse_EEG_data['Delta_TP9'] = butter_bandpass_filter(muse_EEG_data['Delta_TP9'], 
                                            Filter_Lowcut, Filter_Highcut, Sampling_Rate, Filter_Order)
        muse_EEG_data['Delta_AF7'] = butter_bandpass_filter(muse_EEG_data['Delta_AF7'], 
                                            Filter_Lowcut, Filter_Highcut, Sampling_Rate, Filter_Order)
        muse_EEG_data['Delta_AF8'] = butter_bandpass_filter(muse_EEG_data['Delta_AF8'], 
                                            Filter_Lowcut, Filter_Highcut, Sampling_Rate, Filter_Order)
        muse_EEG_data['Delta_TP10'] = butter_bandpass_filter(muse_EEG_data['Delta_TP10'], 
                                            Filter_Lowcut, Filter_Highcut, Sampling_Rate, Filter_Order)

        if Verbosity > 2:
            print('filter_all_data() finished filtering delta data')

        muse_EEG_data['Theta_TP9'] = butter_bandpass_filter(muse_EEG_data['Theta_TP9'], 
                                            Filter_Lowcut, Filter_Highcut, Sampling_Rate, Filter_Order)
        muse_EEG_data['Theta_AF7'] = butter_bandpass_filter(muse_EEG_data['Theta_AF7'], 
                                            Filter_Lowcut, Filter_Highcut, Sampling_Rate, Filter_Order)
        muse_EEG_data['Theta_AF8'] = butter_bandpass_filter(muse_EEG_data['Theta_AF8'], 
                                            Filter_Lowcut, Filter_Highcut, Sampling_Rate, Filter_Order)
        muse_EEG_data['Theta_TP10'] = butter_bandpass_filter(muse_EEG_data['Theta_TP10'], 
                                            Filter_Lowcut, Filter_Highcut, Sampling_Rate, Filter_Order)

        if Verbosity > 2:
            print('filter_all_data() finished filtering theta data')

        muse_EEG_data['Alpha_TP9'] = butter_bandpass_filter(muse_EEG_data['Alpha_TP9'], 
                                            Filter_Lowcut, Filter_Highcut, Sampling_Rate, Filter_Order)
        muse_EEG_data['Alpha_AF7'] = butter_bandpass_filter(muse_EEG_data['Alpha_AF7'], 
                                            Filter_Lowcut, Filter_Highcut, Sampling_Rate, Filter_Order)
        muse_EEG_data['Alpha_AF8'] = butter_bandpass_filter(muse_EEG_data['Alpha_AF8'], 
                                            Filter_Lowcut, Filter_Highcut, Sampling_Rate, Filter_Order)
        muse_EEG_data['Alpha_TP10'] = butter_bandpass_filter(muse_EEG_data['Alpha_TP10'], 
                                            Filter_Lowcut, Filter_Highcut, Sampling_Rate, Filter_Order)

        if Verbosity > 2:
            print('filter_all_data() finished filtering alpha data')

        muse_EEG_data['Beta_TP9'] = butter_bandpass_filter(muse_EEG_data['Beta_TP9'], 
                                            Filter_Lowcut, Filter_Highcut, Sampling_Rate, Filter_Order)
        muse_EEG_data['Beta_AF7'] = butter_bandpass_filter(muse_EEG_data['Beta_AF7'], 
                                            Filter_Lowcut, Filter_Highcut, Sampling_Rate, Filter_Order)
        muse_EEG_data['Beta_AF8'] = butter_bandpass_filter(muse_EEG_data['Beta_AF8'], 
                                            Filter_Lowcut, Filter_Highcut, Sampling_Rate, Filter_Order)
        muse_EEG_data['Beta_TP10'] = butter_bandpass_filter(muse_EEG_data['Beta_TP10'], 
                                            Filter_Lowcut, Filter_Highcut, Sampling_Rate, Filter_Order)

        if Verbosity > 2:
            print('filter_all_data() finished filtering beta data')

        muse_EEG_data['Gamma_TP9'] = butter_bandpass_filter(muse_EEG_data['Gamma_TP9'], 
                                            Filter_Lowcut, Filter_Highcut, Sampling_Rate, Filter_Order)
        muse_EEG_data['Gamma_AF7'] = butter_bandpass_filter(muse_EEG_data['Gamma_AF7'], 
                                            Filter_Lowcut, Filter_Highcut, Sampling_Rate, Filter_Order)
        muse_EEG_data['Gamma_AF8'] = butter_bandpass_filter(muse_EEG_data['Gamma_AF8'], 
                                            Filter_Lowcut, Filter_Highcut, Sampling_Rate, Filter_Order)
        muse_EEG_data['Gamma_TP10'] = butter_bandpass_filter(muse_EEG_data['Gamma_TP10'], 
                                            Filter_Lowcut, Filter_Highcut, Sampling_Rate, Filter_Order)

        if Verbosity > 2:
            print('filter_all_data() finished filtering gamma data')

#         muse_EEG_data['Accelerometer_X'] = butter_bandpass_filter(muse_EEG_data['Accelerometer_X'], 
#                                             Filter_Lowcut, Filter_Highcut, Sampling_Rate, Filter_Order)
#         muse_EEG_data['Accelerometer_Y'] = butter_bandpass_filter(muse_EEG_data['Accelerometer_Y'], 
#                                             Filter_Lowcut, Filter_Highcut, Sampling_Rate, Filter_Order)
#         muse_EEG_data['Accelerometer_Z'] = butter_bandpass_filter(muse_EEG_data['Accelerometer_Z'], 
#                                             Filter_Lowcut, Filter_Highcut, Sampling_Rate, Filter_Order)
#         muse_EEG_data['Gyro_X'] = butter_bandpass_filter(muse_EEG_data['Gyro_X'], 
#                                             Filter_Lowcut, Filter_Highcut, Sampling_Rate, Filter_Order)
#         muse_EEG_data['Gyro_Y'] = butter_bandpass_filter(muse_EEG_data['Gyro_Y'], 
#                                             Filter_Lowcut, Filter_Highcut, Sampling_Rate, Filter_Order)
#         muse_EEG_data['Gyro_Z'] = butter_bandpass_filter(muse_EEG_data['Gyro_Z'], 
#                                             Filter_Lowcut, Filter_Highcut, Sampling_Rate, Filter_Order)
# 
#         if Verbosity > 2:
#             print('filter_all_data() finished filtering accel & gyro data')


    return(muse_EEG_data)




def filter_data(data_in):

#     filtered_data = butter_lowpass_filter(data_in100.0, Sampling_Rate)

# TODO: FInd a simple/faster/better lowpass filter 

    b, a = butter_lowpass(50.0, Sampling_Rate, order=3)
    filtered_data = lfilter(b, a, data_in)


#     N  = 3    
#     Wn = 0.05
#     B, A = signal.butter(N, Wn, output='ba')
#     filtered_data = signal.filtfilt(B,A, data_in)

# 
#     fc = 300;
#     fs = 1000;
# 
#     [b,a] = butter(6,fc/(fs/2));
#     freqz(b,a)

    return filtered_data



def butter_lowpass(cutoff, fs, order=5):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq

    if Verbosity > 0:
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

    if Verbosity > 0:
        print("butter_bandpass() nyq: ", nyq, " lowcut ", lowcut,  " highcut ", highcut,  
                "low:", low, "high:", high, " fs ", fs, " order ", order)

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
def plot_coherence_scatter(x, y, a, b, title, data_fname, plot_fname, date_time_now, analysis_parms, fig_num):

    global session_dict
    global muse_EEG_data

    if Verbosity > 0:
        print('plot_coherence_scatter() called')

    fig, axs = plt.subplots(nrows=1, num=fig_num, figsize=FIGURE_SIZE,
        dpi=PLOT_DPI, facecolor='w', edgecolor='k', sharex=True, sharey=True,
        gridspec_kw={'hspace': 0.25}, tight_layout=False)
        
    plt.rcParams.update(PLOT_PARAMS)

    plt_axes = plt.gca()
    
    plt.scatter(x, y, s=1, color='r', alpha=0.5, label='AF7/AF8')
    plt.scatter(a, b, s=1, color='g', alpha=0.5, label='TP9/TP10')

    
    plt.xlabel('Amp uV')
    plt.ylabel('Amp uV')
    # plt.hlines([-a, a], 0, T, linestyles='--')
    plt.grid(True)
    plt.suptitle('Algorithmic Biofeedback Control System', fontsize=12, fontweight='bold')
    plt.title(title)
    plt.legend(loc='upper left')

    plt.text(0.175, 1.025, 'Session Date: ' + session_dict['Session_Data']['session_date'], 
            transform=plt_axes.transAxes, style='italic', horizontalalignment='right',
            bbox={'facecolor':'blue', 'alpha':0.1, 'pad':1})

    plt_axes.xaxis.set_major_locator(ticker.AutoLocator())  
    plt_axes.xaxis.set_minor_locator(ticker.AutoMinorLocator())
    plt_axes.yaxis.set_major_locator(ticker.AutoLocator())  
    plt_axes.yaxis.set_minor_locator(ticker.AutoMinorLocator())

    create_analysis_parms_text(0.76, 1.025, plt_axes, analysis_parms)    
    basename = os.path.basename(data_fname)
    create_file_date_text(-0.1, -0.12, -0.1, -0.06, plt_axes, basename, date_time_now)
         
     
    plt.savefig(plot_fname, dpi=300)

    if (gui_dict['checkBoxInteractive']):
        plt.show()

    plt.close()

    if Verbosity > 0:
        print("Finished writing EEG EF7 & EF8 Integrated Data - Coherence plot")
        print(plot_fname)


    return True






'''

Plot the coherence data 

'''

def plot_coherence_data(timestamps, tp9, af7, af8, tp10, data_fname, plot_fname, date_time_now, 
                        title, data_stats, analysis_parms, fig_num):

    global session_dict
    global muse_EEG_data
    
    if Verbosity > 0:
        print('plot_coherence_data() called')

    af_diff = af7 - af8
    tp_diff = tp9 - tp10
    
# TODO Make this a function
    # Run the stats of the incoming data which is specific to each call to this function
    tp_mean = np.mean(np.nan_to_num(tp_diff))
    tp_std = np.std(np.nan_to_num(tp_diff))
    tp_max = np.max(np.nan_to_num(tp_diff))
    tp_min = np.min(np.nan_to_num(tp_diff))

    af_mean = np.mean(np.nan_to_num(af_diff))
    af_std = np.std(np.nan_to_num(af_diff))
    af_max = np.max(np.nan_to_num(af_diff))
    af_min = np.min(np.nan_to_num(af_diff))

    if Verbosity > 2:  

        print("tp_mean: ", tp_mean)
        print("tp_std: ", tp_std)
        print("tp_max: ", tp_max)
        print("tp_min: ", tp_min)
    
        print("af_mean: ", af_mean)
        print("af_std: ", af_std)
        print("af_max: ", af_max)
        print("af_min: ", af_min)

  
    t_len = len(timestamps)
    
    period = (1.0/Sampling_Rate)
    x_series = np.arange(0, t_len * period, period)
 
 
    fig, axs = plt.subplots(nrows=2, num=fig_num, figsize=FIGURE_SIZE, 
                    dpi=PLOT_DPI, facecolor='w', edgecolor='k', sharex=True, sharey=gui_dict['checkBoxVerticalLock'], 
                        gridspec_kw={'hspace': 0.25}, tight_layout=False)
       
    plt.suptitle('Algorithmic Biofeedback Control System' + '\n' + title, fontsize=12, fontweight='bold')
    plt.rcParams.update(PLOT_PARAMS)
#     plt.title(title)
    plt_axes = plt.gca()

    data_min = np.min((data_stats[0], data_stats[2], data_stats[4], data_stats[6]))
    data_max = np.max((data_stats[1], data_stats[3], data_stats[5], data_stats[7]))


    if Verbosity > 2:  
        print('plot_coherence_data() data_stats: ', data_stats)
        print('plot_coherence_data() data_min: ', data_min)
        print('plot_coherence_data() data_max: ', data_max)

    clip_padding = 50. 
    y_limits = [data_min - clip_padding, data_max + clip_padding]

    axs[0].plot(x_series, af_diff, alpha=0.8, marker='.', mec='xkcd:dark brown',
                color=plot_color_scheme['RawAF8'], label='AF Diff')
    axs[0].set(title='AF7 - AF8', ylabel="Amp uV")      
    axs[0].set_ylim((af_min, af_max))
    if (gui_dict['checkBoxDataMarkers']):    
        generate_data_markers(muse_EEG_data, axs[0], 'Coherence')
     
    axs[1].plot(x_series, tp_diff, alpha=0.8, marker='.', mec='xkcd:wine',
                color=plot_color_scheme['RawTP9'], label='TP Diff')
                              
    axs[1].xaxis.set_major_locator(ticker.AutoLocator())  
    axs[1].xaxis.set_minor_locator(ticker.AutoMinorLocator())
    axs[1].set_ylim((tp_min, tp_max))
    axs[1].set(title='TP9 - TP10', ylabel="Amp uV") 
    if (gui_dict['checkBoxDataMarkers']):    
        generate_data_markers(muse_EEG_data, axs[1], 'Coherence')

#     axs[0].grid(True)

    for tmp_ax in axs:
            tmp_ax.grid(True)
            tmp_ax.legend(loc='upper right')


    basename = os.path.basename(data_fname)
    create_file_date_text(-0.05, -0.15, -0.05, -0.25, axs[1], basename, date_time_now)

    create_analysis_parms_text(0.83, 2.275, plt_axes, analysis_parms)    

    plt.text(0.175, 2.275, 'Session Date: ' + session_dict['Session_Data']['session_date'], 
            transform=plt_axes.transAxes, style='italic', horizontalalignment='right',
            bbox={'facecolor':'blue', 'alpha':0.1, 'pad':1})


    plt.text(1.01, 1.75, 
        'Mean: ' + "{:.3f}".format(af_mean) + 
        '\nStd: ' + "{:.3f}".format(af_std) + 
        '\nMin: ' + "{:.3f}".format(af_min) +
        '\nMax: ' + "{:.3f}".format(af_max), style='italic', 
        transform=plt_axes.transAxes, 
        bbox={'facecolor': 'blue', 'alpha': 0.05, 'pad': 1})

    plt.text(1.01, 0.50, 
        'Mean: ' + "{:.3f}".format(tp_mean) + 
        '\nStd: ' + "{:.3f}".format(tp_std) + 
        '\nMin: ' + "{:.3f}".format(tp_min) +
        '\nMax: ' + "{:.3f}".format(tp_max), style='italic', 
        transform=plt_axes.transAxes,
        bbox={'facecolor': 'blue', 'alpha': 0.05, 'pad': 1})

 
    plt.savefig(plot_fname, dpi=300)
   
    if (gui_dict['checkBoxInteractive']):
        plt.show()
  
    plt.close()

    if Verbosity > 0:
        print("Finished writing coherence sensor data plot ")
        print(plot_fname)
    

    return True






'''

Plot the sensor data 

'''

def plot_sensor_data(timestamps, tp9, af7, af8, tp10, data_fname, plot_fname, date_time_now, 
                        title, data_stats, analysis_parms, fig_num):

    global muse_EEG_data    
    global session_dict
    
    if Verbosity > 0:
        print('plot_sensor_data() called')


    print('\nplot_sensor_data() called: data_stats', data_stats)
    print("\n")
  
    t_len = len(timestamps)
    
    period = (1.0/Sampling_Rate)
    x_series = np.arange(0, t_len * period, period)
 
    fig, axs = plt.subplots(nrows=5, num=fig_num, figsize=FIGURE_SIZE, 
                    dpi=PLOT_DPI, facecolor='w', edgecolor='k', sharex=True, sharey=gui_dict['checkBoxVerticalLock'], 
                        gridspec_kw={'hspace': 0.25}, tight_layout=False)
       
    plt.suptitle('Algorithmic Biofeedback Control System', fontsize=12, fontweight='bold')
    plt.rcParams.update(PLOT_PARAMS)          
    plt_axes = plt.gca()


    data_stats = (EEG_Dict['RAW_AF7']['25%'], EEG_Dict['RAW_AF7']['75%'],
                EEG_Dict['RAW_AF8']['25%'], EEG_Dict['RAW_AF8']['75%'],
                EEG_Dict['RAW_TP9']['25%'], EEG_Dict['RAW_TP9']['75%'],
                EEG_Dict['RAW_TP10']['25%'], EEG_Dict['RAW_TP10']['75%'])


    data_min = np.min((EEG_Dict['RAW_AF7']['25%'], data_stats[2], data_stats[4], data_stats[6]))
    data_max = np.max((data_stats[1], data_stats[3], data_stats[5], data_stats[7]))

#     data_min = np.min((data_stats[0], data_stats[2], data_stats[4], data_stats[6]))
#     data_max = np.max((data_stats[1], data_stats[3], data_stats[5], data_stats[7]))

  
    if Verbosity > 2:  
        print('plot_sensor_data() data_stats: ', data_stats)
        print('plot_sensor_data() data_min: ', data_min)
        print('plot_sensor_data() data_max: ', data_max)


    clip_padding = 100. 
    y_limits = [data_min - clip_padding, data_max + clip_padding]
    

#     x1 = np.arange(0, t_len)    
# #     y1 = np.cos(x1)
#     y1 = np.cos(x1/1000)
# 
#     f1 = interpolate.interp1d(x1, y1, kind='cubic')
# #     f1 = interpolate.interp1d(df['TimeStamp'], df['RAW_TP9'], kind='cubic')
#     xnew1 = np.arange(0, t_len - 1, 0.1)
#     interp_data = f1(xnew1)  
#     print('plot_sensor_data() interp_data: ', interp_data)

# matplotlib.cm.get_cmap('autumn_r')

#     matplotlib.style.use('seaborn')
    
    axs[0].plot(x_series, tp9, alpha=0.8, marker='.', mec='xkcd:dark pink',
                color=plot_color_scheme['RawTP9'], label='TP9')                              
    axs[0].plot(x_series, af7, alpha=0.8, marker='.', mec='xkcd:salmon',
                color=plot_color_scheme['RawAF7'], label='AF7')
    axs[0].plot(x_series, af8, alpha=0.8, marker='.', mec='xkcd:cerulean',
                color=plot_color_scheme['RawAF8'], label='AF8')
    axs[0].plot(x_series, tp10, alpha=0.8, marker='.', mec='xkcd:dark lilac',
                color=plot_color_scheme['RawTP10'], label='TP10')
  
  
    axs[0].xaxis.set_major_locator(ticker.AutoLocator())  
    axs[0].xaxis.set_minor_locator(ticker.AutoMinorLocator())
    axs[0].set_ylim(y_limits)
    axs[0].set(title=title, ylabel="Amp uV")       
    axs[0].text(0.975, 0.025, '(All Sensor Data Combined)',
        verticalalignment='bottom', horizontalalignment='right',
        transform=axs[0].transAxes, color='green') 

    if (gui_dict['checkBoxDataMarkers']):    
        generate_data_markers(muse_EEG_data, axs[0], 'RAW_TP10')
       
                   
#     axs[0].annotate('Notable Data Point', xy=([data_stats[0], data_stats[1]]), 
#                             xytext=([data_stats[2], data_stats[3]]),
#             arrowprops=dict(facecolor='black', shrink=0.01))
            

    axs[1].plot(x_series, tp9, alpha=1.0, marker='.', mec='xkcd:dark pink',
            color=plot_color_scheme['RawTP9'], label='TP9')
    axs[1].set(title='TP9', ylabel="Amp uV")      
    axs[1].set_ylim((EEG_Dict['RAW_TP9']['25%'] - clip_padding), (EEG_Dict['RAW_TP9']['75%'] + clip_padding))
    if (gui_dict['checkBoxDataMarkers']):    
        generate_data_markers(muse_EEG_data, axs[1], 'RAW_TP9')
    
    axs[2].plot(x_series, af7, alpha=1.0, marker='.', mec='xkcd:salmon',
            color=plot_color_scheme['RawAF7'], label='AF7')
    axs[2].set(title='AF7', ylabel="Amp uV") 
    axs[2].set_ylim((EEG_Dict['RAW_AF7']['25%'] - clip_padding), (EEG_Dict['RAW_AF7']['75%'] + clip_padding))
    if (gui_dict['checkBoxDataMarkers']):    
        generate_data_markers(muse_EEG_data, axs[2], 'RAW_AF7')

    axs[3].plot(x_series, af8, alpha=1.0, marker='.', mec='xkcd:cerulean',
            color=plot_color_scheme['RawAF8'], label='AF8')
    axs[3].set(title='AF8', ylabel="Amp uV") 
    axs[3].set_ylim((EEG_Dict['RAW_AF8']['25%'] - clip_padding), (EEG_Dict['RAW_AF8']['75%'] + clip_padding))
    if (gui_dict['checkBoxDataMarkers']):    
        generate_data_markers(muse_EEG_data, axs[3], 'RAW_AF8')

    axs[4].plot(x_series, tp10, alpha=1.0, marker='.', mec='xkcd:dark lilac',
            color=plot_color_scheme['RawTP10'], label='TP10')
    axs[4].set(title='TP10', xlabel="Time (Seconds)", ylabel="Amp uV") 
    axs[4].set_ylim((EEG_Dict['RAW_TP10']['25%'] - clip_padding), (EEG_Dict['RAW_TP10']['75%'] + clip_padding))
    if (gui_dict['checkBoxDataMarkers']):    
        generate_data_markers(muse_EEG_data, axs[4], 'RAW_TP10')
     
    for tmp_ax in axs:
            tmp_ax.grid(True)
            tmp_ax.legend(loc='upper right')

    basename = os.path.basename(data_fname)
    create_file_date_text(-0.1, -0.7, -0.1, -0.4, axs[4], basename, date_time_now)

    create_analysis_parms_text(0.83, 6.1, plt_axes, analysis_parms)    

    plt.text(0.175, 6.1, 'Session Date: ' + session_dict['Session_Data']['session_date'], 
            transform=plt_axes.transAxes, style='italic', horizontalalignment='right',
            bbox={'facecolor':'blue', 'alpha':0.1, 'pad':1})

    plt.text(1.01, 4.25, 
        'Mean: ' + "{:.3f}".format(EEG_Dict['RAW_TP9']['mean']) + 
        '\nStd: ' + "{:.3f}".format(EEG_Dict['RAW_TP9']['std']) + 
        '\nMin: ' + "{:.3f}".format(EEG_Dict['RAW_TP9']['min']) +
        '\nMax: ' + "{:.3f}".format(EEG_Dict['RAW_TP9']['max']), style='italic', 
        transform=plt_axes.transAxes, 
        bbox={'facecolor': 'blue', 'alpha': 0.05, 'pad': 1})

    plt.text(1.01, 3.0, 
        'Mean: ' + "{:.3f}".format(EEG_Dict['RAW_AF7']['mean']) + 
        '\nStd: ' + "{:.3f}".format(EEG_Dict['RAW_AF7']['std']) + 
        '\nMin: ' + "{:.3f}".format(EEG_Dict['RAW_AF7']['min']) +
        '\nMax: ' + "{:.3f}".format(EEG_Dict['RAW_AF7']['max']), style='italic', 
        transform=plt_axes.transAxes,
        bbox={'facecolor': 'blue', 'alpha': 0.05, 'pad': 1})

    plt.text(1.01, 1.75, 
        'Mean: ' + "{:.3f}".format(EEG_Dict['RAW_AF8']['mean']) + 
        '\nStd: ' + "{:.3f}".format(EEG_Dict['RAW_AF8']['std']) + 
        '\nMin: ' + "{:.3f}".format(EEG_Dict['RAW_AF8']['min']) +
        '\nMax: ' + "{:.3f}".format(EEG_Dict['RAW_AF8']['max']), style='italic', 
        transform=plt_axes.transAxes, 
        bbox={'facecolor': 'blue', 'alpha': 0.05, 'pad': 1})

    plt.text(1.01, 0.50, 
        'Mean: ' + "{:.3f}".format(EEG_Dict['RAW_TP10']['mean']) + 
        '\nStd: ' + "{:.3f}".format(EEG_Dict['RAW_TP10']['std']) + 
        '\nMin: ' + "{:.3f}".format(EEG_Dict['RAW_TP10']['min']) +
        '\nMax: ' + "{:.3f}".format(EEG_Dict['RAW_TP10']['max']), style='italic', 
        transform=plt_axes.transAxes,
        bbox={'facecolor': 'blue', 'alpha': 0.05, 'pad': 1})
    
    plt.savefig(plot_fname, dpi=300)
   
    if (gui_dict['checkBoxInteractive']):
        plt.show()
  
    plt.close()

    if Verbosity > 0:
        print("Finished writing sensor data plot ")
        print(plot_fname)
    

    return True






'''

Plot the sensor data as a single plot

'''

def plot_sensor_data_single(timestamps, tp9, af7, af8, tp10, data_fname, plot_fname, date_time_now, 
                        title, data_stats, analysis_parms, fig_num):

    global session_dict
    global muse_EEG_data
    
    if Verbosity > 0:
        print('plot_sensor_data_single() called')
#     print('plot_sensor_data_single() data_stats: ', data_stats)
   
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
  
    if Verbosity > 2:  
        print('plot_sensor_data_single() data_stats: ', data_stats)
        print('plot_sensor_data_single() data_min: ', data_min)
        print('plot_sensor_data_single() data_max: ', data_max)

    clip_padding = 50. 
    y_limits = [data_min - clip_padding, data_max + clip_padding]

    line_alpha = 0.5
    axs.plot(x_series, tp9, alpha=line_alpha, marker='.', mec='xkcd:dark pink',
                color=plot_color_scheme['RawTP9'], label='TP9')                            
    axs.plot(x_series, af7, alpha=line_alpha, marker='.', mec='xkcd:salmon',
                color=plot_color_scheme['RawAF7'], label='AF7')
    axs.plot(x_series, af8, alpha=line_alpha, marker='.', mec='xkcd:cerulean',
                color=plot_color_scheme['RawAF8'], label='AF8')
    axs.plot(x_series, tp10, alpha=line_alpha, marker='.', mec='xkcd:dark lilac',
                color=plot_color_scheme['RawTP10'], label='TP10')
  
    axs.xaxis.set_major_locator(ticker.AutoLocator())  
    axs.xaxis.set_minor_locator(ticker.AutoMinorLocator())
    axs.set_ylim(y_limits)
                
    axs.set(title=title, ylabel="Amp uV", xlabel="Time (Seconds)") 

    if (gui_dict['checkBoxDataMarkers']):    
        generate_data_markers(muse_EEG_data, axs, 'RAW_TP10')
                  
#     axs[0].annotate('Notable Data Point', xy=([data_stats[0], data_stats[1]]), 
#                             xytext=([data_stats[2], data_stats[3]]),
#             arrowprops=dict(facecolor='black', shrink=0.01))
                   
    axs.grid(True)
    axs.legend(loc='upper right')

    plt.text(0.175, 1.025, 'Session Date: ' + session_dict['Session_Data']['session_date'], 
            transform=plt_axes.transAxes, style='italic', horizontalalignment='right',
            bbox={'facecolor':'blue', 'alpha':0.1, 'pad': 1})

    create_analysis_parms_text(0.8, 1.02, plt_axes, analysis_parms)    
    basename = os.path.basename(data_fname)
    create_file_date_text(-0.1, -0.12, -0.1, -0.07, plt_axes, basename, date_time_now)

#     axs[0].text(0.01, 0.01, 

    plt.text(1.01, 0.25, 
        'TP9' +
        '\nMean: ' + "{:.3f}".format(EEG_Dict['RAW_TP9']['mean']) + 
        '\nStd: ' + "{:.3f}".format(EEG_Dict['RAW_TP9']['std']) + 
        '\nMin: ' + "{:.3f}".format(EEG_Dict['RAW_TP9']['min']) +
        '\nMax: ' + "{:.3f}".format(EEG_Dict['RAW_TP9']['max']) +
        '\n\nAF7' +
        '\nMean: ' + "{:.3f}".format(EEG_Dict['RAW_AF7']['mean']) + 
        '\nStd: ' + "{:.3f}".format(EEG_Dict['RAW_AF7']['std']) + 
        '\nMin: ' + "{:.3f}".format(EEG_Dict['RAW_AF7']['min']) +
        '\nMax: ' + "{:.3f}".format(EEG_Dict['RAW_AF7']['max']) +
        '\n\nAF8' +
        '\nMean: ' + "{:.3f}".format(EEG_Dict['RAW_AF8']['mean']) + 
        '\nStd: ' + "{:.3f}".format(EEG_Dict['RAW_AF8']['std']) + 
        '\nMin: ' + "{:.3f}".format(EEG_Dict['RAW_AF8']['min']) +
        '\nMax: ' + "{:.3f}".format(EEG_Dict['RAW_AF8']['max']) +
        '\n\nTP10' +
        '\nMean: ' + "{:.3f}".format(EEG_Dict['RAW_TP10']['mean']) + 
        '\nStd: ' + "{:.3f}".format(EEG_Dict['RAW_TP10']['std']) + 
        '\nMin: ' + "{:.3f}".format(EEG_Dict['RAW_TP10']['max']) +
        '\nMax: ' + "{:.3f}".format(EEG_Dict['RAW_TP10']['min']), style='italic', 
        transform=plt_axes.transAxes, 
        bbox={'facecolor': 'blue', 'alpha': 0.05, 'pad': 1})


    plt.savefig(plot_fname, dpi=300)
   
    if (gui_dict['checkBoxInteractive']):
        plt.show()
  
    plt.close()

    if Verbosity > 0:
        print("Finished writing sensor data single plot ")
        print(plot_fname)
    
    return True




'''

Plot all the power bands

'''

def plot_all_power_bands(delta, theta, alpha, beta, gamma,
                lowcut, highcut, fs, point_sz, title, 
                data_fname, plot_fname, date_time_now, analysis_parms, fig_num):


# TODO:  Make multiple windows

    plot_alpha = 0.95

    if Verbosity > 0:
        print('plot_all_power_bands() called')

    data_stats = calculate_power_stats(delta, theta, alpha, beta, gamma)
#     print('plot_all_power_bands() data_stats ', data_stats)

    data_min = np.min((data_stats['delta']['min'], data_stats['theta']['min'], 
                        data_stats['alpha']['min'], data_stats['beta']['min'], data_stats['gamma']['min']))
    data_max = np.max((data_stats['delta']['max'], data_stats['theta']['max'], 
                        data_stats['alpha']['max'], data_stats['beta']['max'], data_stats['gamma']['max']))


    fig, axs = plt.subplots(nrows=5, num=fig_num, figsize=FIGURE_SIZE, 
                    dpi=PLOT_DPI, facecolor='w', edgecolor='k', sharex=True, sharey=gui_dict['checkBoxVerticalLock'], 
                        gridspec_kw={'hspace': 0.25}, tight_layout=False)

    fig.suptitle('Algorithmic Biofeedback Control System', fontsize=12, fontweight='bold')

    plt_axes = plt.gca()

    xmin, xmax, ymin, ymax = plt.axis()

    plt.rcParams.update(PLOT_PARAMS)

    t_len = len(delta)
    period = (1.0/Sampling_Rate)
    x_series = np.arange(0, t_len * period, period)

    axs[0].set(title=title) 
    axs[0].xaxis.set_major_locator(ticker.AutoLocator())  
    axs[0].xaxis.set_minor_locator(ticker.AutoMinorLocator())

    l0 = axs[0].plot(x_series, gamma,  color=plot_color_scheme['Gamma'], marker='.', mec='xkcd:dark pink',
                    alpha=plot_alpha, label='Gamma')
    axs[0].legend(loc='upper right', prop={'size': 6})     
    axs[0].grid(True)
#     axs[0].hlines([-a, a], 0, T, linestyles='--')

    if (gui_dict['checkBoxDataMarkers']):    
        generate_data_markers(muse_EEG_data, axs[0], 'Gamma_TP10')
                  
    l1 = axs[1].plot(x_series, beta,  color=plot_color_scheme['Beta'], marker='.', mec='xkcd:dark teal',
                    alpha=plot_alpha, label='Beta')
    axs[1].legend(loc='upper right', prop={'size': 6})
    axs[1].grid(True)
#     axs[1].hlines([-a, a], 0, T, linestyles='--')
#     axs[1].set(title='Beta') 
    if (gui_dict['checkBoxDataMarkers']):    
        generate_data_markers(muse_EEG_data, axs[1], 'Beta_TP10')

    l2 = axs[2].plot(x_series, alpha,  color=plot_color_scheme['Alpha'], marker='.', mec='xkcd:dark brown',
                    alpha=plot_alpha, label='Alpha')
    axs[2].legend(loc='upper right', prop={'size': 6})
    axs[2].grid(True)
#     axs[2].hlines([-a, a], 0, T, linestyles='--')
#     axs[2].set(title='Alpha') 
    if (gui_dict['checkBoxDataMarkers']):    
        generate_data_markers(muse_EEG_data, axs[2], 'Alpha_TP10')

    l3 = axs[3].plot(x_series, theta,  color=plot_color_scheme['Theta'], marker='.', mec='xkcd:crimson',
                alpha=plot_alpha, label='Theta')
    axs[3].legend(loc='upper right', prop={'size': 6})
    axs[3].grid(True)
#     axs[3].hlines([-a, a], 0, T, linestyles='--')
#     axs[3].set(title='Theta') 
    if (gui_dict['checkBoxDataMarkers']):    
        generate_data_markers(muse_EEG_data, axs[3], 'Theta_TP10')

    l4 = axs[4].plot(x_series, delta,  color=plot_color_scheme['Delta'], marker='.', mec='xkcd:wine',
                alpha=plot_alpha, label='Delta')
    axs[4].legend(loc='upper right', prop={'size': 6})
    axs[4].grid(True)
#     axs[4].hlines([-a, a], 0, T, linestyles='--')
#     axs[4].set(title='Delta') 
    if (gui_dict['checkBoxDataMarkers']):    
        generate_data_markers(muse_EEG_data, axs[4], 'Delta_TP10')

    axs[4].set(xlabel="Time (Seconds)") 


    plt.text(1.01, 5.5, 
        'Mean: ' + "{:.3f}".format(data_stats['gamma']['mean']) + 
        '\nStd: ' + "{:.3f}".format(data_stats['gamma']['std']) + 
        '\nMin: ' + "{:.3f}".format(data_stats['gamma']['min']) +
        '\nMax: ' + "{:.3f}".format(data_stats['gamma']['max']), style='italic', 
        transform=plt_axes.transAxes, 
        bbox={'facecolor': 'blue', 'alpha': 0.05, 'pad': 1})

    plt.text(1.01, 4.25, 
        'Mean: ' + "{:.3f}".format(data_stats['beta']['mean']) + 
        '\nStd: ' + "{:.3f}".format(data_stats['beta']['std']) +
        '\nMin: ' + "{:.3f}".format(data_stats['beta']['min']) +
        '\nMax: ' + "{:.3f}".format(data_stats['beta']['max']), style='italic', 
        transform=plt_axes.transAxes, 
        bbox={'facecolor': 'blue', 'alpha': 0.05, 'pad': 1})
        
    plt.text(1.01, 3.0, 
        'Mean: ' + "{:.3f}".format(data_stats['alpha']['mean']) + 
        '\nStd: ' + "{:.3f}".format(data_stats['alpha']['std']) +
        '\nMin: ' + "{:.3f}".format(data_stats['alpha']['min']) +
        '\nMax: ' + "{:.3f}".format(data_stats['alpha']['max']), style='italic', 
        
        transform=plt_axes.transAxes, 
        bbox={'facecolor': 'blue', 'alpha': 0.05, 'pad': 1})
        
    plt.text(1.01, 1.75, 
        'Mean: ' + "{:.3f}".format(data_stats['theta']['mean']) + 
        '\nStd: ' + "{:.3f}".format(data_stats['theta']['std']) +
        '\nMin: ' + "{:.3f}".format(data_stats['theta']['min']) +
        '\nMax: ' + "{:.3f}".format(data_stats['theta']['max']), style='italic', 
        transform=plt_axes.transAxes, 
        bbox={'facecolor': 'blue', 'alpha': 0.05, 'pad': 1})
        
    plt.text(1.01, 0.5, 
        'Mean: ' + "{:.3f}".format(data_stats['delta']['mean']) + 
        '\nStd: ' + "{:.3f}".format(data_stats['delta']['std']) + 
        '\nMin: ' + "{:.3f}".format(data_stats['delta']['min']) +
        '\nMax: ' + "{:.3f}".format(data_stats['delta']['max']), style='italic', 
        transform=plt_axes.transAxes, 
        bbox={'facecolor': 'blue', 'alpha': 0.05, 'pad': 1})

    plt.text(0.175, 6.1, 'Session Date: ' + session_dict['Session_Data']['session_date'], 
            transform=plt_axes.transAxes, style='italic', horizontalalignment='right',
            bbox={'facecolor':'blue', 'alpha':0.1, 'pad': 1})

    create_analysis_parms_text(0.8, 6.1, plt_axes, analysis_parms)    
    basename = os.path.basename(data_fname)
    create_file_date_text(-0.1, -0.65, -0.1, -0.4, plt_axes, basename, date_time_now)

    plt.savefig(plot_fname, dpi=300)

    if (gui_dict['checkBoxInteractive']):
        plt.show()

    plt.close()

    if Verbosity > 0:
        print("Finished writing " + title + " data plot ")
        print(plot_fname)


    return True




'''

Plot all the sensor power bands

'''

def plot_sensor_power_bands(delta, theta, alpha, beta, gamma,
                lowcut, highcut, fs, point_sz, title, 
                data_fname, plot_fname, date_time_now, analysis_parms, fig_num):

    global session_dict
    global muse_EEG_data

    plot_alpha = 0.8

    if Verbosity > 0:
        print('plot_sensor_power_bands() called')

    data_stats = calculate_power_stats(delta, theta, alpha, beta, gamma)
#     print('plot_all_power_bands() data_stats ', data_stats)

    data_min = np.min((data_stats['delta']['min'], data_stats['theta']['min'], 
                        data_stats['alpha']['min'], data_stats['beta']['min'], data_stats['gamma']['min']))
    data_max = np.max((data_stats['delta']['max'], data_stats['theta']['max'], 
                        data_stats['alpha']['max'], data_stats['beta']['max'], data_stats['gamma']['max']))


    plt.rcParams.update(PLOT_PARAMS)
    
    fig, axs = plt.subplots(nrows=5, num=fig_num, figsize=FIGURE_SIZE, 
                    dpi=PLOT_DPI, facecolor='w', edgecolor='k', sharex=True, sharey=gui_dict['checkBoxVerticalLock'], 
                        gridspec_kw={'hspace': 0.25}, tight_layout=False)

    fig.suptitle('Algorithmic Biofeedback Control System', fontsize=12, fontweight='bold')

    plt_axes = plt.gca()

    xmin, xmax, ymin, ymax = plt.axis()

    t_len = len(delta)
    period = (1.0/Sampling_Rate)
    x_series = np.arange(0, t_len * period, period)

    axs[0].set(title=title) 

    axs[0].xaxis.set_major_locator(ticker.AutoLocator())  
    axs[0].xaxis.set_minor_locator(ticker.AutoMinorLocator())


# TODO Need figure out a better way to iterate through the 4 data sets    
#     loop_cntr = 0 
#     markers = ('o', 's', '^', 'D')
#     marker_size = 1.5

#     for key, value in gamma.iteritems():
#         loop_cntr  += 1
# 
#         l0 = axs[0].plot(x_series, value, color=plot_color_scheme['Gamma'], 
#                 markerfacecolor=('#000000'), ms=marker_size,
# #                 markerfacecolor=('#000000'), markevery=10, ms=marker_size,
#                     marker=markers[loop_cntr - 1], alpha=plot_alpha, label=key)

    l0 = axs[0].plot(x_series, gamma,  color=plot_color_scheme['Gamma'], marker='.', mec='xkcd:dark pink',
                    alpha=plot_alpha, label='Gamma')

    axs[0].legend(loc='upper right', prop={'size': 6})     
    axs[0].grid(True)
    #     axs[0].hlines([-a, a], 0, T, linestyles='--')

    if (gui_dict['checkBoxDataMarkers']):    
        generate_data_markers(muse_EEG_data, axs[0], 'Gamma_TP10')


# TODO Need figure out a better way to iterate through the 4 data sets    
#     loop_cntr = 0 
#     for key, value in beta.iteritems():
#         loop_cntr  += 1
# 
#         l1 = axs[1].plot(x_series, value, color=plot_color_scheme['Beta'], 
#                 markerfacecolor=('#000000'), ms=marker_size,
# #                 markerfacecolor=('#000000'), markevery=10, ms=marker_size,
#                     marker=markers[loop_cntr - 1], alpha=plot_alpha, label=key)

    l1 = axs[1].plot(x_series, beta,  color=plot_color_scheme['Beta'], marker='.', mec='xkcd:dark teal',
                    alpha=plot_alpha, label='Beta')

    axs[1].legend(loc='upper right', prop={'size': 6})
    axs[1].grid(True)
#     axs[1].hlines([-a, a], 0, T, linestyles='--')
    if (gui_dict['checkBoxDataMarkers']):    
        generate_data_markers(muse_EEG_data, axs[1], 'Beta_TP10')

# TODO Need figure out a better way to iterate through the 4 data sets    
#     loop_cntr = 0 
#     for key, value in alpha.iteritems():
#         loop_cntr  += 1
# 
#         l2 = axs[2].plot(x_series, value, color=plot_color_scheme['Alpha'], 
#                 markerfacecolor=('#000000'), ms=marker_size,
# #                 markerfacecolor=('#000000'), markevery=10, ms=marker_size,
#                     marker=markers[loop_cntr - 1], alpha=plot_alpha, label=key)

    l2 = axs[2].plot(x_series, alpha,  color=plot_color_scheme['Alpha'], marker='.', mec='xkcd:dark brown',
                    alpha=plot_alpha, label='Alpha')

    axs[2].legend(loc='upper right', prop={'size': 6})
    axs[2].grid(True)
#     axs[2].hlines([-a, a], 0, T, linestyles='--')
    if (gui_dict['checkBoxDataMarkers']):    
        generate_data_markers(muse_EEG_data, axs[2], 'Alpha_TP10')

# TODO Need figure out a better way to iterate through the 4 data sets    
#     loop_cntr = 0 
#     for key, value in theta.iteritems():
#         loop_cntr  += 1
# 
#         l3 = axs[3].plot(x_series, value, color=plot_color_scheme['Theta'], 
#                 markerfacecolor=('#000000'), ms=marker_size,
# #                 markerfacecolor=('#000000'), markevery=10, ms=marker_size,
#                     marker=markers[loop_cntr - 1], alpha=plot_alpha, label=key)

    l3 = axs[3].plot(x_series, theta,  color=plot_color_scheme['Theta'], marker='.', mec='xkcd:crimson',
                    alpha=plot_alpha, label='Theta')

    axs[3].legend(loc='upper right', prop={'size': 6})
    axs[3].grid(True)
#     axs[3].hlines([-a, a], 0, T, linestyles='--')
    if (gui_dict['checkBoxDataMarkers']):    
        generate_data_markers(muse_EEG_data, axs[3], 'Theta_TP10')

# TODO Need figure out a better way to iterate through the 4 data sets    
#     loop_cntr = 0 
#     for key, value in delta.iteritems():
#         loop_cntr  += 1
# 
#         l4 = axs[4].plot(x_series, value, color=plot_color_scheme['Delta'], 
#                 markerfacecolor=('#000000'), ms=marker_size,
# #                 markerfacecolor=('#000000'), markevery=10, ms=marker_size,
#                     marker=markers[loop_cntr - 1], alpha=plot_alpha, label=key)

    l4 = axs[4].plot(x_series, delta,  color=plot_color_scheme['Delta'], marker='.', mec='xkcd:wine',
                    alpha=plot_alpha, label='Delta')

    axs[4].set(xlabel="Time (Seconds)") 

    axs[4].legend(loc='upper right', prop={'size': 6})
    axs[4].grid(True)
#     axs[4].hlines([-a, a], 0, T, linestyles='--')
    if (gui_dict['checkBoxDataMarkers']):    
        generate_data_markers(muse_EEG_data, axs[4], 'Delta_TP10')


    plt.text(1.01, 5.5, 
        'Mean: ' + "{:.3f}".format(data_stats['gamma']['mean']) + 
        '\nStd: ' + "{:.3f}".format(data_stats['gamma']['std']) + 
        '\nMin: ' + "{:.3f}".format(data_stats['gamma']['min']) +
        '\nMax: ' + "{:.3f}".format(data_stats['gamma']['max']), style='italic', 
        transform=plt_axes.transAxes, 
        bbox={'facecolor': 'blue', 'alpha': 0.05, 'pad': 1})

    plt.text(1.01, 4.25, 
        'Mean: ' + "{:.3f}".format(data_stats['beta']['mean']) + 
        '\nStd: ' + "{:.3f}".format(data_stats['beta']['std']) +
        '\nMin: ' + "{:.3f}".format(data_stats['beta']['min']) +
        '\nMax: ' + "{:.3f}".format(data_stats['beta']['max']), style='italic', 
        transform=plt_axes.transAxes, 
        bbox={'facecolor': 'blue', 'alpha': 0.05, 'pad': 1})
        
    plt.text(1.01, 3.0, 
        'Mean: ' + "{:.3f}".format(data_stats['alpha']['mean']) + 
        '\nStd: ' + "{:.3f}".format(data_stats['alpha']['std']) +
        '\nMin: ' + "{:.3f}".format(data_stats['alpha']['min']) +
        '\nMax: ' + "{:.3f}".format(data_stats['alpha']['max']), style='italic', 
        
        transform=plt_axes.transAxes, 
        bbox={'facecolor': 'blue', 'alpha': 0.05, 'pad': 1})
        
    plt.text(1.01, 1.75, 
        'Mean: ' + "{:.3f}".format(data_stats['theta']['mean']) + 
        '\nStd: ' + "{:.3f}".format(data_stats['theta']['std']) +
        '\nMin: ' + "{:.3f}".format(data_stats['theta']['min']) +
        '\nMax: ' + "{:.3f}".format(data_stats['theta']['max']), style='italic', 
        transform=plt_axes.transAxes, 
        bbox={'facecolor': 'blue', 'alpha': 0.05, 'pad': 1})
        
    plt.text(1.01, 0.5, 
        'Mean: ' + "{:.3f}".format(data_stats['delta']['mean']) + 
        '\nStd: ' + "{:.3f}".format(data_stats['delta']['std']) + 
        '\nMin: ' + "{:.3f}".format(data_stats['delta']['min']) +
        '\nMax: ' + "{:.3f}".format(data_stats['delta']['max']), style='italic', 
        transform=plt_axes.transAxes, 
        bbox={'facecolor': 'blue', 'alpha': 0.05, 'pad': 1})


    plt.text(0.175, 6.1, 'Session Date: ' + session_dict['Session_Data']['session_date'], 
            transform=plt_axes.transAxes, style='italic', horizontalalignment='right',
            bbox={'facecolor':'blue', 'alpha':0.1, 'pad':1})

    create_analysis_parms_text(0.8, 6.1, plt_axes, analysis_parms)    
    basename = os.path.basename(data_fname)
    create_file_date_text(-0.1, -0.625, -0.1, -0.35, plt_axes, basename, date_time_now)

    plt.savefig(plot_fname, dpi=300)

    if (gui_dict['checkBoxInteractive']):
        plt.show()

    plt.close()

    if Verbosity > 0:
        print("Finished writing " + title + " data plot ")
        print(plot_fname)
    

    return True





'''

Plot combined power bands

'''

def plot_combined_power_bands(delta_raw, theta_raw, alpha_raw, beta_raw, gamma_raw,
                delta, theta, alpha, beta, gamma,
                lowcut, highcut, fs, point_sz, title, 
                data_fname, plot_fname, date_time_now, analysis_parms, fig_num):

    global session_dict
    global muse_EEG_data

    if Verbosity > 0:
        print('plot_combined_power_bands() called')

    plot_alpha = 0.8

    data_stats = calculate_power_stats(delta, theta, alpha, beta, gamma)
#     print('plot_all_power_bands() data_stats ', data_stats)

    data_min = np.min((data_stats['delta']['min'], data_stats['theta']['min'], 
                        data_stats['alpha']['min'], data_stats['beta']['min'], data_stats['gamma']['min']))
    data_max = np.max((data_stats['delta']['max'], data_stats['theta']['max'], 
                        data_stats['alpha']['max'], data_stats['beta']['max'], data_stats['gamma']['max']))

    fig, axs = plt.subplots(nrows=5, num=fig_num, figsize=FIGURE_SIZE, 
                    dpi=PLOT_DPI, facecolor='w', edgecolor='k', sharex=True, sharey=gui_dict['checkBoxVerticalLock'], 
                        gridspec_kw={'hspace': 0.25}, tight_layout=False)

    plt.rcParams.update(PLOT_PARAMS)
    fig.suptitle('Algorithmic Biofeedback Control System', fontsize=12, fontweight='bold')

    plt_axes = plt.gca()

    y_limits = [data_stats['gamma']['min'], data_stats['gamma']['max']]
  
    t_len = len(delta)
    period = (1.0/Sampling_Rate)
    x_series = np.arange(0, t_len * period, period)

    axs[0].set(title=title) 
    axs[0].xaxis.set_major_locator(ticker.AutoLocator())  
    axs[0].xaxis.set_minor_locator(ticker.AutoMinorLocator())

    l0 = axs[0].plot(x_series, gamma_raw, color=plot_color_scheme['Gamma'],  marker='.', mec='xkcd:dark pink',
                alpha=plot_alpha, label='Gamma Raw')
    l00 = axs[0].scatter(x_series, gamma, s=1, color=plot_color_scheme['Gamma'],
                alpha=plot_alpha, label='Gamma')
                
    axs[0].legend(loc='upper right', prop={'size': 6})     
    axs[0].grid(True)
#     axs[0].hlines([-a, a], 0, T, linestyles='--')
    if (gui_dict['checkBoxDataMarkers']):    
        generate_data_markers(muse_EEG_data, axs[0], 'Gamma_TP10')


    l1 = axs[1].plot(x_series, beta_raw, color=plot_color_scheme['Beta'],  marker='.', mec='xkcd:dark teal',
        alpha=plot_alpha, label='Beta Raw')
    l11 = axs[1].scatter(x_series, beta, s=1, color=plot_color_scheme['Beta'], 
        alpha=plot_alpha, label='Beta')
    axs[1].legend(loc='upper right', prop={'size': 6})
    axs[1].grid(True)
#     axs[1].set_ylim(y_limits)
#     axs[1].hlines([-a, a], 0, T, linestyles='--')
    if (gui_dict['checkBoxDataMarkers']):    
        generate_data_markers(muse_EEG_data, axs[1], 'Beta_TP10')

    l2 = axs[2].plot(x_series, alpha_raw, color=plot_color_scheme['Alpha'], marker='.', mec='xkcd:dark brown',
        alpha=plot_alpha, label='Alpha Raw')
    l22 = axs[2].scatter(x_series, alpha, s=1, color=plot_color_scheme['Alpha'],
        alpha=plot_alpha, label='Alpha')
    axs[2].legend(loc='upper right', prop={'size': 6})
    axs[2].grid(True)
#     axs[2].set_ylim(y_limits)    
#     axs[2].hlines([-a, a], 0, T, linestyles='--')
    if (gui_dict['checkBoxDataMarkers']):    
        generate_data_markers(muse_EEG_data, axs[2], 'Alpha_TP10')

    l3 = axs[3].plot(x_series, theta_raw, color=plot_color_scheme['Theta'], marker='.', mec='xkcd:crimson',
        alpha=plot_alpha, label='Theta Raw')
    l33 = axs[3].scatter(x_series, theta, s=1, color=plot_color_scheme['Theta'],
        alpha=plot_alpha, label='Theta')
    axs[3].legend(loc='upper right', prop={'size': 6})
    axs[3].grid(True)
#     axs[3].set_ylim(y_limits)
#     axs[3].hlines([-a, a], 0, T, linestyles='--')
    if (gui_dict['checkBoxDataMarkers']):    
        generate_data_markers(muse_EEG_data, axs[3], 'Theta_TP10')

    l4 = axs[4].plot(x_series, delta_raw, color=plot_color_scheme['Delta'], marker='.', mec='xkcd:wine',
        alpha=plot_alpha, label='Delta Raw')
    l44 = axs[4].scatter(x_series, delta, s=1, color=plot_color_scheme['Delta'],
        alpha=plot_alpha, label='Delta')
    axs[4].legend(loc='upper right', prop={'size': 6})
    axs[4].grid(True)
#     axs[4].set_ylim(y_limits)
#     axs[4].hlines([-a, a], 0, T, linestyles='--')
    if (gui_dict['checkBoxDataMarkers']):    
        generate_data_markers(muse_EEG_data, axs[4], 'Delta_TP10')

    axs[4].set(xlabel="Time (Seconds)")
   
    plt.text(1.01, 5.5, 
        'Mean: ' + "{:.3f}".format(data_stats['gamma']['mean']) + 
        '\nStd: ' + "{:.3f}".format(data_stats['gamma']['std']) + 
        '\nMin: ' + "{:.3f}".format(data_stats['gamma']['min']) +
        '\nMax: ' + "{:.3f}".format(data_stats['gamma']['max']), style='italic', 
        transform=plt_axes.transAxes, 
        bbox={'facecolor': 'blue', 'alpha': 0.05, 'pad': 1})

    plt.text(1.01, 4.25, 
        'Mean: ' + "{:.3f}".format(data_stats['beta']['mean']) + 
        '\nStd: ' + "{:.3f}".format(data_stats['beta']['std']) +
        '\nMin: ' + "{:.3f}".format(data_stats['beta']['min']) +
        '\nMax: ' + "{:.3f}".format(data_stats['beta']['max']), style='italic', 
        transform=plt_axes.transAxes, 
        bbox={'facecolor': 'blue', 'alpha': 0.05, 'pad': 1})
        
    plt.text(1.01, 3.0, 
        'Mean: ' + "{:.3f}".format(data_stats['alpha']['mean']) + 
        '\nStd: ' + "{:.3f}".format(data_stats['alpha']['std']) +
        '\nMin: ' + "{:.3f}".format(data_stats['alpha']['min']) +
        '\nMax: ' + "{:.3f}".format(data_stats['alpha']['max']), style='italic', 
        
        transform=plt_axes.transAxes, 
        bbox={'facecolor': 'blue', 'alpha': 0.05, 'pad': 1})
        
    plt.text(1.01, 1.75, 
        'Mean: ' + "{:.3f}".format(data_stats['theta']['mean']) + 
        '\nStd: ' + "{:.3f}".format(data_stats['theta']['std']) +
        '\nMin: ' + "{:.3f}".format(data_stats['theta']['min']) +
        '\nMax: ' + "{:.3f}".format(data_stats['theta']['max']), style='italic', 
        transform=plt_axes.transAxes, 
        bbox={'facecolor': 'blue', 'alpha': 0.05, 'pad': 1})
        
    plt.text(1.01, 0.5, 
        'Mean: ' + "{:.3f}".format(data_stats['delta']['mean']) + 
        '\nStd: ' + "{:.3f}".format(data_stats['delta']['std']) + 
        '\nMin: ' + "{:.3f}".format(data_stats['delta']['min']) +
        '\nMax: ' + "{:.3f}".format(data_stats['delta']['max']), style='italic', 
        transform=plt_axes.transAxes, 
        bbox={'facecolor': 'blue', 'alpha': 0.05, 'pad': 1})


    plt.text(0.175, 6.1, 'Session Date: ' + session_dict['Session_Data']['session_date'], 
            transform=plt_axes.transAxes, style='italic', horizontalalignment='right',
            bbox={'facecolor':'blue', 'alpha':0.1, 'pad':1})

    create_analysis_parms_text(0.8, 6.1, plt_axes, analysis_parms)
    basename = os.path.basename(data_fname)
    create_file_date_text(-0.1, -0.6, -0.1, -0.35, plt_axes, basename, date_time_now)

    plt.savefig(plot_fname, dpi=300)

    if (gui_dict['checkBoxInteractive']):
        plt.show()

    plt.close()

    if Verbosity > 0:
        print("Finished writing " + title + " data plot ")
        print(plot_fname)



    return True





'''

Plot Mind Monitor's mellow and concentration data

'''

def plot_mellow_concentration(mellow, concentration,
                lowcut, highcut, fs, point_sz, title, 
                data_fname, plot_fname, date_time_now, analysis_parms, fig_num):

    global session_dict
    global muse_EEG_data

    plot_alpha = 0.9

    if Verbosity > 0:
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

    if Verbosity > 2:
        print("mellow_mean: ", mellow_mean)
        print("mellow_std: ", mellow_std)
        print("mellow_max: ", mellow_max)
        print("mellow_min: ", mellow_min)
    
        print("concentration_mean: ", concentration_mean)
        print("concentration_std: ", concentration_std)
        print("concentration_max: ", concentration_max)
        print("concentration_min: ", concentration_min)

    fig, axs = plt.subplots(nrows=2, num=fig_num, figsize=FIGURE_SIZE, 
                    dpi=PLOT_DPI, facecolor='w', edgecolor='k', sharex=True, sharey=gui_dict['checkBoxVerticalLock'], 
                        gridspec_kw={'hspace': 0.25}, tight_layout=False)

    plt.rcParams.update(PLOT_PARAMS)

    fig.suptitle('Algorithmic Biofeedback Control System', fontsize=12, fontweight='bold')

    plt_axes = plt.gca()
#     plt.axis('auto')

    xmin, xmax, ymin, ymax = plt.axis()

    plt_axes.set_ylim(0, 100)

    t_len = len(mellow)
    period = (1.0/Sampling_Rate)
    x_series = np.arange(0, t_len * period, period)

    axs[0].set(title=title) 
    axs[0].xaxis.set_major_locator(ticker.AutoLocator())  
    axs[0].xaxis.set_minor_locator(ticker.AutoMinorLocator())

    l0 = axs[0].plot(x_series, mellow,  color='b', 
                alpha=plot_alpha, marker='.', mec='xkcd:wine', label='Mellow')
    axs[0].legend(loc='upper right', prop={'size': 6})     
    axs[0].grid(True)
#     axs[0].hlines([-a, a], 0, T, linestyles='--')
    if (gui_dict['checkBoxDataMarkers']):    
        generate_data_markers(muse_EEG_data, axs[0], 'Mellow')

    l1 = axs[1].plot(x_series, concentration,  color='g', 
                alpha=plot_alpha, marker='.', mec='xkcd:wine', label='Concentration')
    axs[1].legend(loc='upper right', prop={'size': 6})
    axs[1].grid(True)
    if (gui_dict['checkBoxDataMarkers']):    
        generate_data_markers(muse_EEG_data, axs[1], 'Concentration')

    axs[1].set(xlabel="Time (Seconds)") 

    axs[0].set(ylabel="Mellow") 
    axs[1].set(ylabel="Concentration") 

    plt.text(1.01, 1.95, 
        'Mean: ' + "{:.3f}".format(mellow_mean) + 
        '\nStd: ' + "{:.3f}".format(mellow_std) + 
        '\nMin: ' + "{:.3f}".format(mellow_min) +
        '\nMax: ' + "{:.3f}".format(mellow_max), style='italic', 
        transform=plt_axes.transAxes, 
        bbox={'facecolor': 'blue', 'alpha': 0.05, 'pad': 1})

    plt.text(1.01, 0.75, 
        'Mean: ' + "{:.3f}".format(concentration_mean) + 
        '\nStd: ' + "{:.3f}".format(concentration_std) +
        '\nMin: ' + "{:.3f}".format(concentration_min) +
        '\nMax: ' + "{:.3f}".format(concentration_max), style='italic', 
        transform=plt_axes.transAxes, 
        bbox={'facecolor': 'blue', 'alpha': 0.05, 'pad': 1})
 
    plt.text(0.175, 2.3, 'Session Date: ' + session_dict['Session_Data']['session_date'], 
            transform=plt_axes.transAxes, style='italic', horizontalalignment='right',
            bbox={'facecolor':'blue', 'alpha':0.1, 'pad':1})

    create_analysis_parms_text(0.8, 2.3, plt_axes, analysis_parms)    
    basename = os.path.basename(data_fname)
    create_file_date_text(0., -0.225, 0., -0.15, plt_axes, basename, date_time_now)

    plt.savefig(plot_fname, dpi=300)

    if (gui_dict['checkBoxInteractive']):
        plt.show()

    plt.close()

    if Verbosity > 0:
        print("Finished writing " + title + " data plot ")
        print(plot_fname)


    return True





'''

Plot the accelerometer and gyro data 

'''

def plot_accel_gryo_data(acc_gyro_df, title, data_fname, plot_fname, date_time_now, analysis_parms, fig_num):

    global session_dict
    global muse_EEG_data

    if Verbosity > 0:
        print('plot_accel_gryo_data() called')

    plot_alpha = 1.0
    
    t_len = len(acc_gyro_df['Accelerometer_X'])
    period = (1.0/Sampling_Rate)
    x_series = np.arange(0, t_len * period, period)

#     fig, axs = plt.subplots(nrows=6, num=fig_num, figsize=FIGURE_SIZE, 
#                     dpi=PLOT_DPI, facecolor='w', edgecolor='k', sharex=True, 
#                     sharey=gui_dict['checkBoxVerticalLock'], 
#                         gridspec_kw={'hspace': 0.25})

    fig, axs = plt.subplots(nrows=6, num=fig_num, figsize=FIGURE_SIZE, 
                        dpi=PLOT_DPI, facecolor='w', edgecolor='k', sharex=True, 
#                         sharey=gui_dict['checkBoxVerticalLock'], 
                            gridspec_kw={'hspace': 0.25}, tight_layout=False)


    plt.rcParams.update(PLOT_PARAMS)
    plt.suptitle('Algorithmic Biofeedback Control System', fontsize=12, fontweight='bold')
    plt_axes = plt.gca()

    axs[0].set(title=title) 
    axs[0].xaxis.set_major_locator(ticker.AutoLocator())  
    axs[0].xaxis.set_minor_locator(ticker.AutoMinorLocator())

    # Plot accelerometer data  
            
    l0 = axs[0].plot(x_series, acc_gyro_df['Accelerometer_X'], color='r', marker='.', mec='xkcd:wine',
            alpha=plot_alpha, label='X')
    axs[0].legend(loc='upper right', prop={'size': 6})     
    axs[0].grid(True)
    axs[0].set_ylim((-1.5, 1.5))
    axs[0].set(ylabel="Accelerometer X") 

    l1 = axs[1].plot(x_series, acc_gyro_df['Accelerometer_Y'], color='g', marker='.', mec='xkcd:wine', 
            alpha=plot_alpha, label='Y')
    axs[1].legend(loc='upper right', prop={'size': 6})
    axs[1].grid(True)
    axs[1].set_ylim((-1.5, 1.5))
    axs[1].set(ylabel="Accelerometer Y") 

    l2 = axs[2].plot(x_series, acc_gyro_df['Accelerometer_Z'], color='b', marker='.', mec='xkcd:wine', 
            alpha=plot_alpha, label='Z')
    axs[2].legend(loc='upper right', prop={'size': 6})
    axs[2].grid(True)
    axs[2].set_ylim((-1.5, 1.5))
    axs[2].set(ylabel="Accelerometer Z") 

    if (gui_dict['checkBoxDataMarkers']):    
        generate_data_markers(muse_EEG_data, axs[0], 'Accelerometer_X')
        generate_data_markers(muse_EEG_data, axs[1], 'Accelerometer_X')
        generate_data_markers(muse_EEG_data, axs[2], 'Accelerometer_X')


    # Plot gyro data
    axs[4].set(ylabel="Gyro") 

    l3 = axs[3].plot(x_series, acc_gyro_df['Gyro_X'], color='#FF3AAA', marker='.', mec='xkcd:wine', 
            alpha=plot_alpha, label='Pitch')
    axs[3].legend(loc='upper right', prop={'size': 6})     
    axs[3].grid(True)
    axs[3].set_ylim((-50.0, 50.0))
    axs[3].set(ylabel="Gyro Pitch") 

    l4 = axs[4].plot(x_series, acc_gyro_df['Gyro_Y'], color='#3affe5', marker='.', mec='xkcd:wine',
            alpha=plot_alpha, label='Yaw')
    axs[4].legend(loc='upper right', prop={'size': 6})
    axs[4].grid(True)
    axs[4].set_ylim((-50.0, 50.0))
    axs[4].set(ylabel="Gyro Yaw") 

    l5 = axs[5].plot(x_series, acc_gyro_df['Gyro_Z'], color='#FFC73A', marker='.', mec='xkcd:wine', 
            alpha=plot_alpha, label='Roll')
    axs[5].legend(loc='upper right', prop={'size': 6})
    axs[5].grid(True)
    axs[5].set_ylim((-50.0, 50.0))
    axs[5].set(ylabel="Gyro Roll") 

    if (gui_dict['checkBoxDataMarkers']):    
        generate_data_markers(muse_EEG_data, axs[3], 'Gyro_X')
        generate_data_markers(muse_EEG_data, axs[4], 'Gyro_X')
        generate_data_markers(muse_EEG_data, axs[5], 'Gyro_X')

    axs[5].set(xlabel="Time (Seconds)") 
       
    plt.text(0.175, 7.35, 'Session Date: ' + session_dict['Session_Data']['session_date'], 
        transform=plt_axes.transAxes, style='italic', horizontalalignment='right',
        bbox={'facecolor':'blue', 'alpha':0.1, 'pad':1})

    basename = os.path.basename(data_fname)
    create_file_date_text(-0.1, -0.7, -0.1, -0.41, plt_axes, basename, date_time_now)
    create_analysis_parms_text(0.8, 7.35, plt_axes, analysis_parms)

    plt.savefig(plot_fname, dpi=300)

    if (gui_dict['checkBoxInteractive']):
        plt.show()
 
    plt.close()

    if Verbosity > 0:
        print("Finished writing accel/gyro data plot ")
        print(plot_fname)
    
       
    return True






'''

Calculate stats for power data

'''

def calculate_power_stats(delta, theta, alpha, beta, gamma):

# TODO This whole function can be removed, it's redundant

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

    data_stats = {
    'delta': {'min': delta_min, 'max': delta_max, 'std': delta_std, 'mean': delta_mean},
    'theta': {'min': theta_min, 'max': theta_max, 'std': theta_std, 'mean': theta_mean},
    'alpha': {'min': alpha_min, 'max': alpha_max, 'std': alpha_std, 'mean': alpha_mean},
    'beta': {'min': beta_min, 'max': beta_max, 'std': beta_std, 'mean': beta_mean},
    'gamma': {'min': gamma_min, 'max': gamma_max, 'std': gamma_std, 'mean': gamma_mean}   
    }

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


    if Verbosity > 2:  
        print("data_stats: ", data_stats)


    return data_stats
    
   
   
'''

Generate data markers


'''

def generate_data_markers(muse_EEG_data, axs, col_select):

    if Verbosity > 2:
        print("generate_data_markers() called")

    elements_df = pd.DataFrame(muse_EEG_data, columns=['TimeStamp', 'Elements'])

    if not ((col_select == 'Accelerometer_X') or (col_select == 'Gyro_X') or (col_select == 'No Offset')):
        data_df = pd.DataFrame(muse_EEG_data, columns=[col_select])
        new_df = data_df.fillna(0)
        
    if Verbosity > 2:
#         print("generate_data_markers() - Elements.describe(): ", elements_df.describe())   
        print("generate_data_markers() - elements_df.count(): ", elements_df.count())

    elements_df['Elements'] = elements_df.Elements.astype(str)
    elements_df = elements_df[~elements_df['Elements'].str.contains('nan')]


    for index, row in elements_df.iterrows():
        if Verbosity > 2:
            print(row['TimeStamp'])
            print(row['Elements'])
        
        if 'jaw' in row['Elements']:
            marker_text = 'J'
# TODO don't mark eye blinks for now
        elif 'blink' in row['Elements']:
#             marker_text = 'B'
            continue 
        else:
            marker_text = row['Elements']
                    
        if (col_select == 'Accelerometer_X') or (col_select == 'Gyro_X') or (col_select == 'No Offset'):
            y_offset = 0            
        elif (col_select == 'Coherence'):
            y_offset = 30            
        else:
            y_offset = np.max(new_df[index:index + 30])     
    
#         if Verbosity > 2:
#             print('generate_data_markers() - y_offset: ', y_offset)
                            
        axs.annotate(marker_text, xy=((index/Sampling_Rate), y_offset), xytext=((index/Sampling_Rate)+2, y_offset+1),
                bbox=dict(boxstyle="round", alpha=0.1), ha='right', va="center", rotation=33, size=8,
                arrowprops=dict(arrowstyle='simple', color='blue', alpha=0.5,
                connectionstyle="arc3, rad=0.03"))

        
    return True   
   
   
   
'''

Make labels for the file name and date  

'''

def create_file_date_text(x1, y1, x2, y2, plt_axes, data_fname, date_time_now):

    plt.text(x1, y1, "file: " + data_fname, 
        transform=plt_axes.transAxes, style='italic',
#         transform=plt_axes.transAxes, style='italic',
        bbox={'facecolor':'blue', 'alpha':0.1, 'pad':1})

    plt.text(x2, y2, "Date: " + date_time_now, 
        transform=plt_axes.transAxes, style='italic',
#         transform=plt_axes.transAxes, style='italic',
        bbox={'facecolor':'blue', 'alpha':0.1, 'pad':1})

    return True



'''

Make labels for the analysis parameters  

'''

def create_analysis_parms_text(x, y, plt_axes, analysis_parms):

    if (gui_dict['checkBoxFilter'] or args.filter_data):

        if Filter_Type == 0:
            filter_type_name = 'Default'
        if Filter_Type == 1:
            filter_type_name = 'Low Pass'
        if Filter_Type == 2:
            filter_type_name = 'Band Pass'

        text_string = 'Sample Time: ' + "{:.2f}".format(analysis_parms['sample_time_min']) +  \
            ' (minutes) ' + "{:.2f}".format(analysis_parms['sample_time_sec']) + " (seconds)" +   \
            '\nSample Length: ' + "{:d}".format(analysis_parms['sample_length']) +    \
                '\nFilter Type: ' + filter_type_name +  \
                '  Filter Order: ' + "{:.1f}".format(analysis_parms['filter_order']) + \
                '\nLow Cut: ' + "{:.1f}".format(analysis_parms['lowcut']) + " HZ " +   \
                ' High Cut: ' + "{:.1f}".format(analysis_parms['highcut']) + " HZ "
    else:
    
        text_string = 'Sample Time: ' + "{:.2f}".format(analysis_parms['sample_time_min']) +  \
            ' (minutes) ' + "{:.2f}".format(analysis_parms['sample_time_sec']) + " (seconds)" +   \
            '\nSample Length: ' + "{:d}".format(analysis_parms['sample_length'])
    

    plt.text(x, y, text_string,    
        style='italic', transform=plt_axes.transAxes,
        bbox={'facecolor': 'blue', 'alpha': 0.05, 'pad': 2})

    return True


def pause_and_prompt(pause_time, msg):

    if Verbosity > 0:
        print("Pausing ... " + msg)
    sleep(pause_time)

    return True



'''

Make sure a directory exits, if it doesn't create it.  

'''

def ensure_dir(file_path):
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.makedirs(directory)

    return True



'''

Plot the data!

'''

def generate_plots(muse_EEG_data, data_fname, date_time_now):

    if Verbosity > 0:
        print("Generating plots ", date_time_now)

    ensure_dir(out_dirname + "/plots/")

    df = pd.DataFrame(muse_EEG_data, columns=['TimeStamp', 'RAW_TP9', 'RAW_AF7', 'RAW_AF8', 'RAW_TP10'])    

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

    data_stats = (EEG_Dict['RAW_AF7']['25%'], EEG_Dict['RAW_AF7']['75%'],
                EEG_Dict['RAW_AF8']['25%'], EEG_Dict['RAW_AF8']['75%'],
                EEG_Dict['RAW_TP9']['25%'], EEG_Dict['RAW_TP9']['75%'],
                EEG_Dict['RAW_TP10']['25%'], EEG_Dict['RAW_TP10']['75%'])

    # If the user wants to use an alternative plot style 
    if args.plot_style == 1:
        matplotlib.style.use('seaborn')
    elif args.plot_style == 2:
        matplotlib.style.use('seaborn-pastel')
    elif args.plot_style == 3:
        matplotlib.style.use('seaborn-ticks')
    elif args.plot_style == 4:
        matplotlib.style.use('fast')
    elif args.plot_style == 5:
        matplotlib.style.use('bmh')
    
    # Select color scheme
    global plot_color_scheme
    if (gui_dict['plotColorsComboBox'] == 'ABCS Colors'):
        plot_color_scheme = ABCS_Colors
    else:
        plot_color_scheme = MM_Colors
    

    if (not gui_dict['checkBoxPlotMarkers']):    
        PLOT_PARAMS['lines.markersize'] = 0.0005
        
    if (gui_dict['checkBoxEEG']):

        # TODO don't plot this one for now ...
        if False: 
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

        # TODO don't plot this one for now ...
        if False:
            plot_sensor_data(df['TimeStamp'], df['RAW_TP9'], 
                smooth_data(df['RAW_AF7'], smooth_sz), 
                smooth_data(df['RAW_AF8'], smooth_sz), 
                smooth_data(df['RAW_TP10'], smooth_sz), data_fname, 
                out_dirname + '/plots/21-ABCS_eeg_smoothed_' + date_time_now + '.png',
                date_time_now, "Interpolated EEG", data_stats, analysis_parms, 21)

                
    if (gui_dict['checkBoxCoherence']):

        plot_coherence_scatter(df['RAW_AF7'], df['RAW_AF8'], df['RAW_TP9'], df['RAW_TP10'],
            "Raw Data - Coherence", data_fname,
             out_dirname + '/plots/10-ABCS_eeg_raw_coherence_data_' + date_time_now + '.png', 
             date_time_now, analysis_parms, 10)

        plot_coherence_data(df['TimeStamp'], df['RAW_TP9'], df['RAW_AF7'], 
            df['RAW_AF8'], df['RAW_TP10'], data_fname, 
            out_dirname + '/plots/12-ABCS_eeg_coherence_' + date_time_now + '.png',
            date_time_now,  "EEG Coherence", data_stats, analysis_parms, 12)
    


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




    if (gui_dict['checkBoxPowerBands'] or args.power):

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



        plot_sensor_power_bands(delta_df, theta_df, 
            alpha_df, beta_df, gamma_df,
            Filter_Lowcut, Filter_Highcut, Sampling_Rate, point_sz,
            'Power Bands (All Sensors-Raw)', data_fname,
            out_dirname + '/plots/30-ABCS_all_sensors_power_raw_' + date_time_now + '.png',
            date_time_now, analysis_parms, 30)


        plot_all_power_bands(delta_df.mean(axis=1), theta_df.mean(axis=1), 
            alpha_df.mean(axis=1), beta_df.mean(axis=1), gamma_df.mean(axis=1),
            Filter_Lowcut, Filter_Highcut, Sampling_Rate, point_sz,
            'Power Bands (Mean Average)', data_fname,
            out_dirname + '/plots/31-ABCS_power_mean_' + date_time_now + '.png',
            date_time_now, analysis_parms, 31)


        if (gui_dict['checkBoxStatistical']):


            plot_combined_power_bands(delta_df.mean(axis=1), theta_df.mean(axis=1), 
                alpha_df.mean(axis=1), beta_df.mean(axis=1), gamma_df.mean(axis=1),
                delta_df.median(axis=1), theta_df.median(axis=1), 
                alpha_df.median(axis=1), beta_df.median(axis=1), gamma_df.median(axis=1),
                Filter_Lowcut, Filter_Highcut, Sampling_Rate, 
                point_sz,'Power Bands Mean & Median', data_fname,
                out_dirname + '/plots/32-ABCS_power_bands_median_mean' + 
                date_time_now + '.png', date_time_now, analysis_parms, 32)

            plot_combined_power_bands(delta_df, theta_df, 
                        alpha_df, beta_df, gamma_df,
                        delta_df.mean(axis=1), theta_df.mean(axis=1), 
                        alpha_df.mean(axis=1), beta_df.mean(axis=1), gamma_df.mean(axis=1),
                        Filter_Lowcut, Filter_Highcut, Sampling_Rate, 
                        point_sz,'Power Bands Mean & Raw', data_fname,
                         out_dirname + '/plots/33-ABCS_power_bands_raw_mean' + 
                         date_time_now + '.png', date_time_now, analysis_parms, 33)



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
            




def initialize_GUI_vars(date_time_now):

    if Verbosity > 2:
        print("initialize_GUI_vars(): ", date_time_now)

    gui_dict.update({'firstName': "",'lastName': "",
            "session_notes": "",
            "checkBoxInteractive": False,
            "checkBoxEEG": True,
            "checkBoxCoherence": False,
            "checkBoxPowerBands": True,
            "checkBoxMellowConcentration": False,
            "checkBoxAccelGyro": False,
            "checkBox3D": False,
            "checkBoxFilter": True,                
            "checkBoxStatistical": False,
            "checkBoxMuseDirect": False,
            "verbosityComboBox": 0,
            "checkBoxAutoReject": True,
            "checkBoxDB": False,
            "checkBoxHFDF5": False,
            "plotColorsComboBox": 0,               
            "Mood": 0})

    if Verbosity > 2:
        print("initialize_GUI_vars() - gui_dict: ", gui_dict)
#         pause_and_prompt(2, "initialize_GUI_vars()")


    return True
                

'''


Main ...


'''

def main(date_time_now):

    if Verbosity > 1:
        print("main() ")

    global gui_dict
    global session_dict
    global muse_EEG_data
    global out_dirname
    global first_name
    global last_name
    global data_dir
    global db_location

    if Verbosity > 1:
        print("main() - analyze_muse.ABCS_version.ABCS_version: ", analyze_muse.ABCS_version.ABCS_version)

    initialize_GUI_vars(date_time_now)

    rc_filename = str(Path.home()) + "/.ABCS_parms.rc"           
    my_rc_file = Path(rc_filename)

    if my_rc_file.is_file():
        with open(rc_filename, 'r') as myfile:
            data=myfile.read()

        # parse the runtime config parameters file
        rc_obj = json.loads(data)
        if Verbosity > 1:
            print("main() - rc_obj: ", rc_obj)
        first_name = rc_obj['First Name']
        last_name = rc_obj['Last Name']
        data_dir = rc_obj['Data Dir']
        # Location of sqllite dababase file
        db_location = rc_obj['Data Base Location']



    if not args.batch:
        app = QApplication(sys.argv)
        gui = The_GUI()
        gui.show()
        GUI_status = app.exec_() 
        gui.close()
        app.closeAllWindows()
        app.exit()


    head_tail = os.path.split(CVS_fname) 
  
    if len(CVS_fname) != 0:
        out_dirname = head_tail[0] + "/output/" + head_tail[1][:len( head_tail[1]) - 4] 
        if Verbosity > 1:
            print("main() - Processing file: ", CVS_fname)
            print("main() - Output directory: ", out_dirname)
        
    else:
        print("main() - Filename not specified, exiting ...")
        sys.exit(1)
    
    
    # Read the EEG data from disk
    (muse_EEG_data, EEG_Dict) = read_eeg_data(CVS_fname, date_time_now)

    get_data_description(muse_EEG_data)

#     if Verbosity > 2:
#         print("main() - EEG_Dict: ", EEG_Dict)
#         print("\n")


    # Perform auto-reject if user has selected it
#     if (gui_dict['checkBoxAutoReject'] or args.auto_reject_data): 
    if (gui_dict['checkBoxAutoReject']): 
        if Verbosity > 2:
            print("main() - Calling auto_reject_EEG_data()")
        muse_EEG_data = auto_reject_EEG_data(muse_EEG_data)

    # Perform filtering if user has selected it
    if (gui_dict['checkBoxFilter'] or args.filter_data):
        muse_EEG_data = filter_all_data(muse_EEG_data)
        # If filtering, recompute description data
        get_data_description(muse_EEG_data)
        
#         if Verbosity > 2:
#             print("main() - EEG_Dict after filtering: ", EEG_Dict)
#             print("\n")


    # If the user wants an HDF5 file written of the data 
    if (gui_dict['checkBoxHFDF5'] or args.write_hdf5_file):
        ensure_dir(out_dirname + "/hdf5_data/")
        h5_fname = out_dirname + '/hdf5_data/' + os.path.basename(CVS_fname) + '_' + date_time_now + '.hdf5'
        write_hdf5_data(muse_EEG_data, h5_fname)

    # Save session data to DB
    if (gui_dict['checkBoxDB'] or args.data_base):
        connect_to_DB(date_time_now)


    # Make plots!
    generate_plots(muse_EEG_data, CVS_fname, date_time_now)
 


    return True



if __name__ == '__main__':

    import pkg_resources
    import sys, site
    
    date_time_now = strftime('%Y-%m-%d-%H.%M.%S', gmtime())

    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--csv_file", help="CSV file to read)")
    parser.add_argument("-v", "--verbose", help="Increase output verbosity", type=int)
    parser.add_argument("-d", "--display_plots", help="Display Plots", action="store_true")
    parser.add_argument("-b", "--batch", help="Batch Mode", action="store_true")
    parser.add_argument("-dm", "--data_markers", help="Add Data Markers", action="store_true")
    parser.add_argument("-p", "--power", help="Plot Power Bands", action="store_true")
    parser.add_argument("-e", "--eeg", help="Plot EEG Data", action="store_true")
    parser.add_argument("-hdf5", "--write_hdf5_file", help="Write output data into HDF5 file", action="store_true")
    parser.add_argument("-ag", "--accel_gyro", help="Plot Acceleration and Gyro Data", action="store_true")
    parser.add_argument("-mc", "--mellow_concentration", 
                                help="Plot Mellow and Concentratio Data (Only For Mind Monitor Data)", 
                                action="store_true")
    parser.add_argument("-s", "--stats_plots", help="Plot Statistcal Data", action="store_true")
    parser.add_argument("-c", "--coherence_plots", help="Plot Coherence Data", action="store_true")
    parser.add_argument("--plot_style", 
                help="Plot Syle: 1=seaborn, 2=seaborn-pastel, 3=seaborn-ticks, 4=fast, 5=bmh", type=int)

#     parser.add_argument("--plot_3D", help="3D Display Plots", action="store_true")
#     parser.add_argument("-i", "--integrate", help="Integrate EEG Data", action="store_true")
#     parser.add_argument("-s", "--step_size", help="Integration Step Size", type=int)
#     parser.add_argument("-ps", "--power_spectrum", help="Analyze Spectrum", action="store_true")

    parser.add_argument("-r", "--auto_reject_data", help="Auto Reject EEG Data", action="store_true")
    parser.add_argument("-fd", "--filter_data", help="Filter EEG Data", action="store_true")
    parser.add_argument("-ft", "--filter_type", 
                        help="Filter Type 0=default 1=low pass, 2=bandpass", type=int)
    parser.add_argument("-lc", "--lowcut", help="Filter Low Cuttoff Frequency",  type=float)
    parser.add_argument("-hc", "--highcut", help="Filter High Cuttoff Frequency", type=float)
    parser.add_argument("-o", "--filter_order", help="Filter Order", type=int)
    parser.add_argument("-db", "--data_base", 
                            help="Send session data and statistics to database",  action="store_true")
#     parser.add_argument("-l", "--logging_level", 
#                             help="Logging verbosity: 1 = info, 2 = warning, 3 = debug", type=int)    
                  
                                                
    args = parser.parse_args()

    if args.verbose:
        print("verbose turned on")
        print(args.verbose)
        Verbosity = args.verbose
    else:
        args.verbose = 0

    if args.display_plots:
        if Verbosity > 0:
                print("display_plots:")
        print(args.display_plots)
    else:
        args.display_plots = True

    if args.plot_style:
        if Verbosity > 0:
                print("plot_style:")
        print(args.plot_style)
    else:
        args.plot_style = 0

    if args.data_markers:
        if Verbosity > 0:
                print("data_markers:")
        print(args.data_markers)
    else:
        args.data_markers = False

    if args.batch:
        if Verbosity > 0:
            print("batch:")
        print(args.batch)
        BatchMode = True
        args.display_plots = False

    if args.auto_reject_data:
        if Verbosity > 0:
            print("auto_reject_data:")
        print(args.auto_reject_data)
    else:
        args.auto_reject_data = False

    if args.filter_data:
        if Verbosity > 0:
            print("filter_data:")
            print(args.filter_data)

    if args.filter_type:
        if Verbosity > 0:
            print("filter_type:")
            print(args.filter_type)
        Filter_Type = args.filter_type

    if args.lowcut:
        if Verbosity > 0:
            print("lowcut:")
            print(args.lowcut)
        Filter_Lowcut = args.lowcut

    if args.highcut:
        if Verbosity > 0:
            print("highcut:")
            print(args.highcut)
        Filter_Highcut = args.highcut

    if args.filter_order:
        if Verbosity > 0:
            print("filter_order:")
            print(args.filter_order)
        Filter_Order = args.filter_order

                   
    if args.csv_file:
        CVS_fname = args.csv_file
        if not os.path.exists(CVS_fname):
            print("Filename not specified")
            sys.exit(1)

        if Verbosity > 0:
            print("Processing file: ", CVS_fname)
    

    if args.data_base:
        if Verbosity > 0:
            print("data_base:")
            print(args.data_base)
        Save_DB = args.data_base

# if sys.platform in ['darwin', 'linux', 'linux2', 'win32']:
#     liblo_path = pkg_resources.resource_filename('liblo', 'liblo.so')
#     dso_path = [(liblo_path, '.')]
#     print("DSO path:", dso_path)    
#     print("LIBLO path:", liblo_path)    

    if Verbosity > 2:
        print("Platform: ", sys.platform)
    
    try:
        main(date_time_now)

    except KeyboardInterrupt:
            print('Interrupted')

            try:
                sys.exit(0)
            except SystemExit:

                print('Finished')
                os._exit(0)
            

    sys.exit(0)


