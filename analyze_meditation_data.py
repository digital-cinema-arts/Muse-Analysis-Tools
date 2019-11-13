#!/usr/bin/env python3

from time import time, sleep
import numpy as np
from scipy import fftpack
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
import logging
from binascii import hexlify
import timeit
import io
from progress.bar import Bar, IncrementalBar
import json

from scipy import integrate, signal
from scipy.signal import butter, lfilter

from mpl_toolkits.mplot3d import Axes3D
import matplotlib.patches as mpatches
import matplotlib
# matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import cm

    
# Globals
Integrate_Step_Size = 4
muse_EEG_data = []
eeg_stats = []
Filter_Lowcut  = 1.0
Filter_Highcut  = 100.0
Filter_Order = 4


# Constants
SAMPLING_RATE = 250.0
FIGURE_SIZE = (8, 6)



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



# Message for the progress meter
msg_counter = 0

progress_msgs = {
            0: "The door of thatched hut\nAlso changed the owner.\nAt the Doll’s Festival.", 
            1: "Spring is passing.\nThe birds cry, and the fishes fill\nWith tears on their eyes.",
            2: "Grasses in summer.\nThe warriors’ dreams\nAll that left.",
            3: "The early summer rain.\nLeaves behind\nHikari-do.",
            4: "Ah, tranquility!\nPenetrating the very rock,\nA cicada’s voice.",
            5: "The early summer rain,\nGathering it and fast\nMogami River.",
            6: "To an old pond\nA frog leaps in.\nAnd the sound of the water.",
            7: "Saying something,\nThe lip feel cold.\nThe Autum wind.",
            8: "Sicking on journey,\nMy dream run about\nThe desolate field.",
            9: "This night so long,\ncarry me forward, onto this crest,\na cooling breeze",
            10: "The gentle hand helping me onto stage, whispers of light, silence",
            11: "Go where soul flows freely,\nstay when the breeze stills the mind\nbreathe the love within",
            12: "When the name of your soulmate\nbecomes the mantra of your dreams\nyou're home",
            13: "Accept advice",
            14: "Listen to the quiet voice",
            15: "Be less critical more often",
            16: "Don't break the silence ",
            17: "Change ambiguities to specifics",
            18: "Emphasize differences",
            19: "Fill every beat with something",
            20: "Assemble some of the elements in a group and treat the group",
            21: "First work alone, then work in unusual pairs.",
            22: "Is there something missing?",
            23: "Cascades",
            24: "Lost in useless territory",
            25: "It is quite possible (after all)",
            26: "Call your mother and ask her what to do.",
            27: "Look at the order in which you do things",
            28: "Take away as much mystery as possible. What is left?",
            29: "The most important thing is the thing most easily forgotten"
            }



#############################################################################

           # -*- coding: utf-8 -*-
"""
Muse LSL Example Auxiliary Tools

These functions perform the lower-level operations involved in buffering,
epoching, and transforming EEG data into frequency bands

@author: Cassani
"""

import os
import sys
from tempfile import gettempdir
from subprocess import call

import matplotlib.pyplot as plt
import numpy as np
from sklearn import svm
from scipy.signal import butter, lfilter, lfilter_zi


NOTCH_B, NOTCH_A = butter(4, np.array([55, 65]) / (256 / 2), btype='bandstop')


def epoch(data, samples_epoch, samples_overlap=0):
    """Extract epochs from a time series.

    Given a 2D array of the shape [n_samples, n_channels]
    Creates a 3D array of the shape [wlength_samples, n_channels, n_epochs]

    Args:
        data (numpy.ndarray or list of lists): data [n_samples, n_channels]
        samples_epoch (int): window length in samples
        samples_overlap (int): Overlap between windows in samples

    Returns:
        (numpy.ndarray): epoched data of shape
    """

    if isinstance(data, list):
        data = np.array(data)

    n_samples, n_channels = data.shape

    samples_shift = samples_epoch - samples_overlap

    n_epochs = int(
        np.floor((n_samples - samples_epoch) / float(samples_shift)) + 1)

    # Markers indicate where the epoch starts, and the epoch contains samples_epoch rows
    markers = np.asarray(range(0, n_epochs + 1)) * samples_shift
    markers = markers.astype(int)

    # Divide data in epochs
    epochs = np.zeros((samples_epoch, n_channels, n_epochs))

    for i in range(0, n_epochs):
        epochs[:, :, i] = data[markers[i]:markers[i] + samples_epoch, :]

    return epochs


def compute_band_powers(eegdata, fs):
    """Extract the features (band powers) from the EEG.

    Args:
        eegdata (numpy.ndarray): array of dimension [number of samples,
                number of channels]
        fs (float): sampling frequency of eegdata

    Returns:
        (numpy.ndarray): feature matrix of shape [number of feature points,
            number of different features]
    """
    
#     print("*** compute_band_powers() - eegdata.shape: ", eegdata.shape)
#     print("*** compute_band_powers() - eegdata: ", eegdata)


    # 1. Compute the PSD
#     winSampleLength, nbCh = eegdata.shape
    winSampleLength = len(eegdata)
    
    # Apply Hamming window
    w = np.hamming(winSampleLength)
    dataWinCentered = eegdata - np.mean(eegdata, axis=0)  # Remove offset
    dataWinCenteredHam = (dataWinCentered.T * w).T

    NFFT = nextpow2(winSampleLength)
    Y = np.fft.fft(dataWinCenteredHam, n=NFFT, axis=0) / winSampleLength
    PSD = 2 * np.abs(Y[0:int(NFFT / 2), :])
    f = fs / 2 * np.linspace(0, 1, int(NFFT / 2))

    # SPECTRAL FEATURES
    # Average of band powers
    # Delta <4
    ind_delta, = np.where(f < 4)
    meanDelta = np.mean(PSD[ind_delta, :], axis=0)
    # Theta 4-8
    ind_theta, = np.where((f >= 4) & (f <= 8))
    meanTheta = np.mean(PSD[ind_theta, :], axis=0)
    # Alpha 8-12
    ind_alpha, = np.where((f >= 8) & (f <= 12))
    meanAlpha = np.mean(PSD[ind_alpha, :], axis=0)
    # Beta 12-30
    ind_beta, = np.where((f >= 12) & (f < 30))
    meanBeta = np.mean(PSD[ind_beta, :], axis=0)

    feature_vector = np.concatenate((meanDelta, meanTheta, meanAlpha,
                                     meanBeta), axis=0)

    feature_vector = np.log10(feature_vector)

    return feature_vector


def nextpow2(i):
    """
    Find the next power of 2 for number i
    """
    n = 1
    while n < i:
        n *= 2
    return n


def compute_feature_matrix(epochs, fs):
    """
    Call compute_feature_vector for each EEG epoch
    """
    n_epochs = epochs.shape[2]

    for i_epoch in range(n_epochs):
        if i_epoch == 0:
            feat = compute_band_powers(epochs[:, :, i_epoch], fs).T
            # Initialize feature_matrix
            feature_matrix = np.zeros((n_epochs, feat.shape[0]))

        feature_matrix[i_epoch, :] = compute_band_powers(
            epochs[:, :, i_epoch], fs).T

    return feature_matrix


def get_feature_names(ch_names):
    """Generate the name of the features.

    Args:
        ch_names (list): electrode names

    Returns:
        (list): feature names
    """
    bands = ['delta', 'theta', 'alpha', 'beta']

    feat_names = []
    for band in bands:
        for ch in range(len(ch_names)):
            feat_names.append(band + '-' + ch_names[ch])

    return feat_names


def update_buffer(data_buffer, new_data, notch=False, filter_state=None):
    """
    Concatenates "new_data" into "data_buffer", and returns an array with
    the same size as "data_buffer"
    """
    if new_data.ndim == 1:
        new_data = new_data.reshape(-1, data_buffer.shape[1])

    if notch:
        if filter_state is None:
            filter_state = np.tile(lfilter_zi(NOTCH_B, NOTCH_A),
                                   (data_buffer.shape[1], 1)).T
        new_data, filter_state = lfilter(NOTCH_B, NOTCH_A, new_data, axis=0,
                                         zi=filter_state)

    new_buffer = np.concatenate((data_buffer, new_data), axis=0)
    new_buffer = new_buffer[new_data.shape[0]:, :]

    return new_buffer, filter_state


def get_last_data(data_buffer, newest_samples):
    """
    Obtains from "buffer_array" the "newest samples" (N rows from the
    bottom of the buffer)
    """
    new_buffer = data_buffer[(data_buffer.shape[0] - newest_samples):, :]

    return new_buffer


#############################################################################









def read_eeg_data(fname, date_time_now):
   

# 2019-11-06 14:16:09.099,0.73753726,0.63483715,0.39034298,0.54395723,0.029541425,0.3804217,-0.065705,0.19739334,0.31721696,0.4821059,-0.024969269,0.38310558,0.42083898,0.7230918,0.73041004,0.15750498,0.07422932,0.57002854,0.39831007,-0.10823194,822.7839,822.381,973.0769,806.6667,854.61536,0.0,100.0,0.28076171875,0.00469970703125,0.9471435546875,-1.428070068359375,3.506622314453125,4.658050537109375,1,1.0,1.0,1.0,1.0,54.17
# 
# 


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


    muse_EEG_data = pd.read_csv(fname, 
            dtype={'TimeStamp':str, 
            'Delta_TP9':np.float64, 'Delta_AF7':np.float64, 'Delta_AF8':np.float64, 'Delta_TP10':np.float64,
            'Theta_TP9':np.float64, 'Theta_AF7':np.float64, 'Theta_AF8':np.float64, 'Theta_TP10':np.float64,
            'Alpha_TP9':np.float64, 'Alpha_AF7':np.float64, 'Alpha_AF8':np.float64, 'Alpha_TP10':np.float64,
            'Beta_TP9':np.float64, 'Beta_AF7':np.float64, 'Beta_AF8':np.float64, 'Beta_TP10':np.float64,
            'Gamma_TP9':np.float64, 'Gamma_AF7':np.float64, 'Gamma_AF8':np.float64, 'Gamma_TP10':np.float64,
            'RAW_TP9':np.float64, 'RAW_AF7':np.float64, 'RAW_AF8':np.float64, 'RAW_TP10':np.float64,
            'AUX_RIGHT':np.float64,            
            'Mellow':np.float64, 'Concentration':np.float64,                            
            'Accelerometer_X':np.float64, 'Accelerometer_X':np.float64, 'Accelerometer_X':np.float64,            
            'Gyro_X':np.float64, 'Gyro_Y':np.float64, 'Gyro_Z':np.float64,
            'HeadBandOn':np.float64, 
            'HSI_TP9':np.float64, 'HSI_AF7':np.float64, 'HSI_AF8':np.float64, 'HSI_TP10':np.float64,
#             'Battery':np.float64},                            
            'Battery':np.float64, 'Elements':str},                            
            names=['TimeStamp', 
                'Delta_TP9', 'Delta_AF7', 'Delta_AF8', 'Delta_TP10', 
                'Theta_TP9', 'Theta_AF7', 'Theta_AF8', 'Theta_TP10', 
                'Alpha_TP9', 'Alpha_AF7', 'Alpha_AF8', 'Alpha_TP10', 
                'Beta_TP9', 'Beta_AF7', 'Beta_AF8', 'Beta_TP10', 
                'Gamma_TP9', 'Gamma_AF7', 'Gamma_AF8', 'Gamma_TP10', 
                'RAW_TP9', 'RAW_AF7', 'RAW_AF8', 'RAW_TP10',
                'AUX_RIGHT', 
                'Mellow', 'Concentration',
                'Accelerometer_X', 'Accelerometer_Y', 'Accelerometer_Z',
                'Gyro_X', 'Gyro_Y', 'Gyro_Z',
                'HeadBandOn', 
                'HSI_TP9', 'HSI_AF7', 'HSI_AF8', 'HSI_TP10',             
#                 'Battery'])
                'Battery', 'Elements'])


# 
#     muse_EEG_data = pd.read_csv(fname, 
#             dtype={'TimeStamp':str, 
#             'Delta_TP9':np.float64, 'Delta_AF7':np.float64, 'Delta_AF8':np.float64, 'Delta_TP10':np.float64,
#             'Theta_TP9':np.float64, 'Theta_AF7':np.float64, 'Theta_AF8':np.float64, 'Theta_TP10':np.float64,
#             'Alpha_TP9':np.float64, 'Alpha_AF7':np.float64, 'Alpha_AF8':np.float64, 'Alpha_TP10':np.float64,
#             'Beta_TP9':np.float64, 'Beta_AF7':np.float64, 'Beta_AF8':np.float64, 'Beta_TP10':np.float64,
#             'Gamma_TP9':np.float64, 'Gamma_AF7':np.float64, 'Gamma_AF8':np.float64, 'Gamma_TP10':np.float64,
#             'RAW_TP9':np.float64, 'RAW_AF7':np.float64, 'RAW_AF8':np.float64, 'RAW_TP10':np.float64,
#             'AUX_RIGHT':np.float64},                            
#             names=['TimeStamp', 
#                 'Delta_TP9', 'Delta_AF7', 'Delta_AF8', 'Delta_TP10', 
#                 'Theta_TP9', 'Theta_AF7', 'Theta_AF8', 'Theta_TP10', 
#                 'Alpha_TP9', 'Alpha_AF7', 'Alpha_AF8', 'Alpha_TP10', 
#                 'Beta_TP9', 'Beta_AF7', 'Beta_AF8', 'Beta_TP10', 
#                 'Gamma_TP9', 'Gamma_AF7', 'Gamma_AF8', 'Gamma_TP10', 
#                 'RAW_TP9', 'RAW_AF7', 'RAW_AF8', 'RAW_TP10',
#                 'AUX_RIGHT'])
#                             
# 
#     muse_EEG_data = pd.read_csv(fname, 
#             dtype={'TimeStamp':str},                            
#             names=['TimeStamp'])
#                             
#     print("Done reading EEG data")                    
# 
#     df = pd.DataFrame(muse_EEG_data, columns=['TimeStamp'])    
    raw_df = pd.DataFrame(muse_EEG_data, columns=['RAW_TP9', 'RAW_AF7', 'RAW_AF8', 'RAW_TP10'])    
#     df = np.clip(df, -1.0, 1.0)

#     print("Data description\n", raw_df.describe())                    

    delta_df = pd.DataFrame(muse_EEG_data, columns=['Delta_TP9', 'Delta_AF7', 'Delta_AF8', 'Delta_TP10'])    
#     print("Data description\n", delta_df.describe())                    

    theta_df = pd.DataFrame(muse_EEG_data, columns=['Theta_TP9', 'Theta_AF7', 'Theta_AF8', 'Theta_TP10'])    
#     print("Data description\n", theta_df.describe())                    

    alpha_df = pd.DataFrame(muse_EEG_data, columns=['Alpha_TP9', 'Alpha_AF7', 'Alpha_AF8', 'Alpha_TP10'])    
#     print("Data description\n", alpha_df.describe())                    

    beta_df = pd.DataFrame(muse_EEG_data, columns=['Beta_TP9', 'Beta_AF7', 'Beta_AF8', 'Beta_TP10'])    
#     print("Data description\n", beta_df.describe())                    

    gamma_df = pd.DataFrame(muse_EEG_data, columns=['Gamma_TP9', 'Gamma_AF7', 'Gamma_AF8', 'Gamma_TP10'])    
#     print("Data description\n", gamma_df.describe())                    


    EEG_Dict ={}

    for temp_df in (raw_df, delta_df, theta_df, alpha_df, beta_df, gamma_df):
        print("Sensor data description", temp_df.describe())
#         data_str = temp_df.mean()
        data_str = temp_df.describe()
#         print("type", type(data_str))
#         print("data_str.index", data_str.index)
        EEG_Dict.update(data_str.to_dict())
#         print("EEG_Dict: ", EEG_Dict)
#         print("data_str.to_dict()", data_str.to_dict())
    
 

    session_dict = {
        'Session Data':{
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

    session_dict.update(EEG_Dict)

                      
    print("SAMPLING_RATE: ", SAMPLING_RATE)
    print("Filter_Lowcut: ", Filter_Lowcut)
    print("Filter_Highcut: ", Filter_Highcut)
    print("filter_order: ", Filter_Order)


    sample_length = len(raw_df['RAW_AF7'])
    sample_time_sec = (sample_length/SAMPLING_RATE)
    sample_time_min = sample_time_sec/60.0

    parms_dict = {
            'Analysis Parameters':{
            "lowcut":Filter_Lowcut, "highcut": Filter_Highcut, "filter_order":Filter_Order, 
                        "sample_length":sample_length, "sample_time_sec":sample_time_sec, 
                        "sample_time_min":sample_time_min}
            }

    session_dict.update(parms_dict)
    session_json = json.dumps(session_dict, sort_keys=True)
    print(session_json)


# Save the session data to a JSON file
    session_data_fname = "./session_data/EEG_session_data-" + date_time_now + ".json"
    
    ensure_dir("./session_data/")
    data_file=open(session_data_fname,"w+")
#     pwr_data_file=open("EEG_power_data.txt","w+")

    data_file.write(session_json)
    data_file.close()
  
  
    session_json_df =  pd.read_json(session_json)
    session_csv = session_json_df.to_csv()
    
#     print(session_json_df)
#     print(session_csv)
    

    f = open(session_data_fname + ".csv", "w+")
    f.write(session_csv)
    f.close() 
    f.close()


    
 
#     for sensor_name in ('Gamma_TP9', 'Gamma_AF7', 'Gamma_AF8', 'Gamma_TP10'):
#         print("Data mean", str(temp_df[sensor_name].mean()))
        
                        
#     raw_df = raw_df.describe()
#     print("raw_df ", raw_df)                    
#     print("type(raw_df) ", type(raw_df))                    
#     
#     print("raw_df.mean() ", raw_df.mean())                    
#     print("raw_df.min() ", raw_df.min())                    
#     print("raw_df.max() ", raw_df.max())                    
#     print("raw_df.quantile() ", raw_df.quantile())                    
#     print("raw_df.sem() ", raw_df.sem())                    
#     print("raw_df.std() ", raw_df.std())                    
#     print("raw_df.var() ", raw_df.var())                    
    
#     data_to_save = "Data description\n" + raw_df.describe()




#     data_to_save = raw_df.describe()
#     print ("*********")
#     
#     EEG_Dict = {
#     'TP9':{
#     'raw_mean': str(raw_df['RAW_TP9'].mean()),
#     'raw_min': str(raw_df['RAW_TP9'].min()),
#     'raw_max': str(raw_df['RAW_TP9'].min()),
#     'raw_quantile': str(raw_df['RAW_TP9'].quantile()),
#     'raw_sem': str(raw_df['RAW_TP9'].sem())
#     }
#     }
#     
#     EEG_json = json.dumps(EEG_Dict, sort_keys=True)
#     print(EEG_json)
# 
#     global data_file
#     data_file.write(date_time_now + " " + str(data_to_save) + '\n')

    
    
#     eeg_stats['raw_df'] = raw_df
# 
#     print("eeg_stats ", eeg_stats)                    


    return(muse_EEG_data)


#     df = pd.DataFrame(muse_EEG_data, columns=['RAW_TP9', 'RAW_AF7', 'RAW_AF8', 'RAW_TP10'])    
# #     df = np.clip(df, -1.0, 1.0)
# 
#     print("Data description\n", df.describe())                    
# 
#     sys.exit(0)





#     muse_acc_avg_data_1 = pd.read_csv('muselab_recording-acc-1.csv', dtype={'time':np.float64, 'sensor':str, 
#                             'X':np.float64, 'Y':np.float64, 'Z':np.float64},
#                             names=['time', 'sensor', 'X', 'Y', 'Z'])

# 1567398695.981000, /muse/eeg, -4.8828125, 29.296875, 29.785156, 20.996094, -107.421875
# 1567398696.127000, /muse/eeg, 28.808594, 40.527344, 26.855469, 25.390625, -35.15625
# 1567398696.127000, /muse/eeg, 56.152344, 46.38672, 29.785156, 29.296875, 183.10547



# Muse Lab CSV format needs work to conver data steam into columns 


    muse_EEG_data = pd.read_csv(fname, 
                            dtype={'time':np.float64, 'sensor':str, 
                            'TP9':np.float64, 'AF7':np.float64, 'AF8':np.float64,
                            'TP10':np.float64, 'AUX':np.float64},                            
                            names=['time', 'sensor', 'TP9', 'AF7', 'AF8', 'TP10', 'AUX'])
                            
    print("Done reading EEG data")                    

    df = pd.DataFrame(muse_EEG_data, columns=['TP9', 'AF7', 'AF8', 'TP10'])    
#     df = np.clip(df, -1.0, 1.0)

    print("Data description\n", df.describe())                    

    sys.exit(0)
        
    return muse_EEG_data



    muse_EEG_data = pd.read_csv(fname, 
                            dtype={'time':np.float64, 'sensor':str, 
                            'TP9':np.float64, 'AF7':np.float64, 'AF8':np.float64,
                            'TP10':np.float64, 'AUX':np.float64},                            
                            names=['time', 'sensor', 'TP9', 'AF7', 'AF8', 'TP10', 'AUX'])
                            
    print("Done reading EEG data")                    
    
    return muse_EEG_data





def analyze_eeg_data(time_series_data, name=None):
    
#     print("*** analyze_eeg_data() - time_series_data:")
#     print(time_series_data)

#     f_s = 250.0  # Sampling rate, or number of measurements per second
    f_s = 250.0  # Sampling rate, or number of measurements per second

    bar = IncrementalBar('Processing FFT', max=int(len(time_series_data)))


    if len(time_series_data) > 0:
        ps = np.abs(np.fft.fft(time_series_data))**2

    ps= np.nan_to_num(ps)
    print("*** analyze_eeg_data() - ps:")
    print(ps)



    X = []

#     X_avg = []
#     for i in range(len(time_series_data)):
# #         X = fftpack.fft(time_series_data[i])
# #         X.append(np.abs(fftpack.fft(time_series_data[i])))
#         X.append(np.abs(time_series_data[i]))
# 
# #         freqs = fftpack.fftfreq(len(time_series_data[i])) * f_s
# #         idx = np.argsort(freqs)
#         
# #         X_avg.append(np.abs(np.fft.fft(X[i])))
#  
#         bar.next()
#     
# #         print
# #         print("*** analyze_eeg_data() - i: ", i)
# #         print("*** analyze_eeg_data() - time_series_data[i]:")
# #         print(time_series_data[i])
# #         print("*** analyze_eeg_data() - freqs:")
# #         print(freqs)
# #         print("*** analyze_eeg_data() - idx:")
# #         print(idx)
# #         print("*** analyze_eeg_data() - X:")
# #         print([X.real])
# 
#     bar.finish()
        

        
    X = fftpack.fft(time_series_data)
    freqs = fftpack.fftfreq(len(time_series_data)) * f_s

    idx = np.argsort(freqs)
    print("*** analyze_eeg_data() - freqs:")
    print(freqs)
    print("*** analyze_eeg_data() - idx:")
    print(idx)
#     print("*** analyze_eeg_data() - X:")
#     print(X.real)


    return (freqs, idx, ps)





def butter_bandpass(lowcut, highcut, fs, order=5):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
#     print("butter_bandpass: ", low, high, nyq)

    b, a = butter(order, [low, high], btype='band')
    return b, a

def butter_bandpass_filter(data, lowcut, highcut, fs, order=5):
    b, a = butter_bandpass(lowcut, highcut, fs, order=order)
    y = lfilter(b, a, data)
    return y


# TODO: Save these filter while developing other filters

# def butter_lowpass(cutoff, nyq_freq, order=4):
#     normal_cutoff = float(cutoff) / nyq_freq
#     print("normal_cutoff: ", normal_cutoff)
#     b, a = signal.butter(order, normal_cutoff, btype='lowpass')
#     return b, a
# 
# def butter_lowpass_filter(data, cutoff_freq, nyq_freq, order=4):
#     # Source: https://github.com/guillaume-chevalier/filtering-stft-and-laplace-transform
#     b, a = butter_lowpass(cutoff_freq, nyq_freq, order=order)
#     y = signal.filtfilt(b, a, data)
#     return y



def scale(x, out_range=(-1, 1), axis=None):
    domain = np.min(x, axis), np.max(x, axis)
    y = (x - (domain[1] + domain[0]) / 2) / (domain[1] - domain[0])
    return y * (out_range[1] - out_range[0]) + (out_range[1] + out_range[0]) / 2



# Required input defintions are as follows;
# time:   Time between samples
# band:   The bandwidth around the centerline freqency that you wish to filter
# freq:   The centerline frequency to be filtered
# ripple: The maximum passband ripple that is allowed in db
# order:  The filter order.  For FIR notch filters this is best set to 2 or 3,
#         IIR filters are best suited for high values of order.  This algorithm
#         is hard coded to FIR filters
# filter_type: 'butter', 'bessel', 'cheby1', 'cheby2', 'ellip'
# data:         the data to be filtered
def notch_filter(time, band, freq, ripple, order, filter_type, data):
    from scipy.signal import iirfilter
    fs   = 1/time  
    nyq  = fs/2.0
    low  = freq - band/2.0
    high = freq + band/2.0
    low  = low/nyq
    high = high/nyq
    b, a = iirfilter(order, [low, high], rp=ripple, btype='bandstop',
                     analog=False, ftype=filter_type)
    filtered_data = lfilter(b, a, data)
    return filtered_data
    
    
def butter_bandstop_filter(data, lowcut, highcut, fs, order):

        nyq = 0.5 * fs
        low = lowcut / nyq
        high = highcut / nyq

        i, u = butter(order, [low, high], btype='bandstop')
        y = lfilter(i, u, data)
        return y
        
            
    
# TODO: Filter stuff

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
    





def integrate_eeg_data(data, data_name='', data_fname=''):


    global msg_counter

# If user wants to skip the integration 
    if not args.integrate:
        print("Skipping integration")
        return data    
    else:
        print("Runnning integration on data: ", data_name)
        print("\n")
        print(progress_msgs[msg_counter])
        print("\n")
        msg_counter = msg_counter + 1
    
#     res = np.trapz(data)
#     print("trapz result of full data set: ", res)
#     print 
#     print("len(data): ", len(data))
#     print("Integrate_Step_Size: ", Integrate_Step_Size)
#     print("trapz result: ", res, (i * Integrate_Step_Size), 
#         ((i * Integrate_Step_Size) + Integrate_Step_Size))
#     print 


    bar = IncrementalBar('Processing Integration', max=int(len(data)/Integrate_Step_Size))


    integration_res = []
    for i in range(int(len(data)/Integrate_Step_Size)):
#         print("data[i * 100:(i * 100) + 100]: ", data[i * 100:(i * 100) + 100])
        integration_res.append(
            np.trapz(data[i * Integrate_Step_Size:(i * Integrate_Step_Size) + Integrate_Step_Size]))
        bar.next()

    bar.finish()
        
    
    result = np.asarray(integration_res)

    return result
    



#  *************************************

def plot_coherence(x, y, a, b, title, data_fname, plot_fname, date_time_now, analysis_parms):

    logging.info('plot_coherence() called')
    print('plot_coherence() called')

#     print("plot_coherence() - axis_x ", axis_x)
#     print("plot_coherence() - axis_y ", axis_y)
#     print("plot_coherence() - a ", a)
#     print("plot_coherence() - t ", t)
#     print("plot_coherence() - T ", T)
#     print("plot_coherence() - title ", title)
#     print("plot_coherence() - data_fname ", data_fname)
#     print("plot_coherence() - plot_fname ", plot_fname)
# 

    fig = plt.figure(num=41, figsize=(FIGURE_SIZE), dpi=72, facecolor='w', edgecolor='k')

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

    
    plt.xlabel('Amplitude uv')
    plt.ylabel('Amplitude uv')
    # plt.hlines([-a, a], 0, T, linestyles='--')
    plt.grid(True)
    plt.axis('auto')
    plt.suptitle('Algorithmic Biofeedback Control System', fontsize=12, fontweight='bold')
    plt.title(title)
    plt.legend(loc='upper left')

    create_analysis_parms_text(0.7, 0.95, plt_axes, analysis_parms)    
    create_file_date_text(-0.12, -0.11, 0.9, -0.11, plt_axes, data_fname, date_time_now)
         
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

    if args.display_plots:
        plt.show()

    plt.close()
    print("Finished writing EEG EF7 & EF8 Integrated Data - Coherance plot")
    print(plot_fname)
    print





#  *************************************

def plot_time_series_data(af7, af8, data_fname, plot_fname, date_time_now, analysis_parms):

    logging.info('plot_time_series_data() called')
    print('plot_time_series_data() called')

    x_len = np.arange(len(af7))
    
    fig = plt.figure(num=29, figsize=(FIGURE_SIZE), dpi=72, facecolor='w', edgecolor='k')

#     plt.axis([0, len(af7), 0, np.max(np.nan_to_num(af8))])
    plt.axis([0, len(af7), 0, 1000.0])
    plt_axes = plt.gca()
#     plt_axes.set_xlim([0, len(af7)])
#     plt_axes.set_ylim([-1000, 1000])
 
    plt.scatter(x_len, af8, alpha=0.7, s=1, color='r', label='AF7')
    plt.scatter(x_len, af7, alpha=0.7, s=1, color='g', label='AF8')
    plt.plot(x_len, af8, alpha=0.7, ms=1, color='r')
    plt.plot(x_len, af7, alpha=0.7, ms=1, color='g')
    plt.xlabel('Samples')
    plt.ylabel('Amplitude uv')
    # plt.hlines([-a, a], 0, T, linestyles='--')
 
    plt.axis('tight')
    plt.grid(True)
    plt.suptitle('Algorithmic Biofeedback Control System', fontsize=12, fontweight='bold')
    plt.title("EEG EF7 & EF8 Integrated Data - Coherance")
    plt.legend(loc='upper left')

    create_analysis_parms_text(0.7, 0.95, plt_axes, analysis_parms)    
    create_file_date_text(-0.1, -0.1, 0.85, -0.1, plt_axes, data_fname, date_time_now)

    plt.savefig(plot_fname, dpi=300)
   
    if args.display_plots:
        plt.show()
  
    plt.close()
    print("Finished writing integrated time series data plot ")
    print(plot_fname)
    print




  


def plot_scatter_xy(x, y, data_fname, plot_fname):
 
    logging.info('plot_scatter_xy() called')
    print('plot_scatter_xy() called')


    fig = plt.figure(num=63, figsize=(FIGURE_SIZE), dpi=72, facecolor='w', edgecolor='k')

#     plt.axis([0, len(x), 0, len(y)])
#     plt.axis([0, np.max(np.nan_to_num(x)), 0, np.max(np.nan_to_num(y))])

    plt.axis([0, len(x), 0, len(y)])

    x = scale(x, out_range=(-1, 1))
    y = scale(y, out_range=(-1, 1))


    plt.scatter(y, x, s=1, color='r', alpha=0.7, label='AF7 Amplitude - uv')
    plt.scatter(x, y, s=1, color='g', alpha=0.7, label='AF8 Amplitude - uv')
    plt.xlabel('0')
    plt.ylabel('1')
    # plt.hlines([-a, a], 0, T, linestyles='--')
    plt.grid(True)
    plt.axis('auto')
    plt.suptitle('Algorithmic Biofeedback Control System', fontsize=12, fontweight='bold')
    plt.title("X & Y")
    plt.legend(loc='upper left')

    plt.savefig(plot_fname, dpi=300)

    if args.display_plots:
        plt.show()

    plt.close()
    print("Finished writing X - Y scatter plot ")
    print(plot_fname)
    print








def plot_histogram(af7, af8, data_fname, plot_fname):

    logging.info('plot_histogram() called')
    print('plot_histogram() called')

    x = af7
    mu = np.mean(x)
    median = np.median(x)
    sigma = np.std(x)
    textstr = '\n'.join((
        r'$\mu=%.2f$' % (mu, ),
        r'$\mathrm{median}=%.2f$' % (median, ),
        r'$\sigma=%.2f$' % (sigma, )))

#     print("textstr: ", textstr)


    N_points = 100000
    n_bins = 20

    # Generate a normal distribution, center at x=0 and y=5
    x = np.random.randn(N_points)
    y = .4 * x + np.random.randn(100000) + 5
    
#     x = af7_integration_res
#     y = af8_integration_res
    

    fig, axs = plt.subplots(1, num=72, figsize=(FIGURE_SIZE),  sharey=True, tight_layout=True)

    # We can set the number of bins with the `bins` kwarg
    axs[0].hist(x, bins=n_bins)
    axs[1].hist(y, bins=n_bins)



#     plt.hist(x, 50)
    props = dict(boxstyle='round', facecolor='wheat', alpha=1.0)
    
    ax = plt.axis()
        
    plt.text(ax[1] * 0.5, ax[3] * 0.8, textstr, fontsize=10,
        verticalalignment='top', bbox=props)
    plt.hlines([-a, a], 0, T, linestyles='--')
    plt.grid(True)
    plt.axis('auto')
    plt.suptitle('Algorithmic Biofeedback Control System', fontsize=12, fontweight='bold')
    plt.title("EEG EF7 & EF8 Raw Data - Coherance")

    plt.savefig(plot_fname, dpi=300)
           
    if args.display_plots:
        plt.show()

    plt.close()
    print("Finished writing raw data histogram plot ")
    print(plot_fname)
    print

#     print("index: ", index)
#     print("df: ", df)





def plot_semilog_bandpass(af7, af8, lowcut, highcut, fs, data_fname, plot_fname):

    logging.info('plot_semilog_bandpass() called')
    print('plot_semilog_bandpass() called')


    fig = plt.figure(num=18, figsize=(FIGURE_SIZE), dpi=72, facecolor='w', edgecolor='k')
    plt.semilogx(af7, af8, color='g', alpha=0.7, ls='dotted', label='Semilog plot Filtered')
    plt.xlabel('AF7')
    plt.ylabel('AF8')
    # plt.hlines([-a, a], 0, T, linestyles='--')
    plt.grid(True)
    plt.axis('auto')
    plt.suptitle('Algorithmic Biofeedback Control System', fontsize=12, fontweight='bold')

    plt.title("EEG EF7 & EF8 Semilog Plot of Bandpass Data " + str(lowcut) + " " + str(highcut) + " " + str(fs))
    plt.legend(loc='upper left')

    plt.savefig(plot_fname, dpi=300)

    if args.display_plots:
        plt.show()

    plt.close()
    print("Finished writing semilog bandpass data plot ")
    print(plot_fname)
    print




#  ****
def plot_data_combined(tp9_delta_int, af7_delta_int, af8_delta_int, tp10_delta_int, 
                lowcut, highcut, fs, point_sz, 
                title, data_fname, plot_fname, date_time_now, analysis_parms):

    logging.info('plot_data_combined() called')
    print('plot_data_combined() called')


    x_axis = np.arange(len(tp9_delta_int))
#     print("x_axis " , x_axis)

    fig = plt.figure(num=22, figsize=(FIGURE_SIZE), dpi=72, facecolor='w', edgecolor='k')

    plt_axes = plt.gca()

#     plt.semilogx(x_axis, af7_delta_int, color='y', alpha=0.7, ls='dotted', label='Semilog plot Filtered')

    plt.axis([0, len(tp9_delta_int/fs/60), 0, 1])

    plt.plot(tp9_delta_int, color='b', alpha=0.7, label='TP9 ')
    plt.plot(af7_delta_int, color='g', alpha=0.7, label='AF7 ')
    plt.plot(af8_delta_int, color='r', alpha=0.7, label='AF8 ')
    plt.plot(tp10_delta_int, color='c', alpha=0.7, label='TP10 ')

    plt.scatter(x_axis, tp9_delta_int, s=point_sz, color='b', alpha=1.0)
    plt.scatter(x_axis, af7_delta_int, s=point_sz, color='g', alpha=1.0)
    plt.scatter(x_axis, af8_delta_int, s=point_sz, color='r', alpha=1.0)
    plt.scatter(x_axis, tp10_delta_int, s=point_sz, color='c', alpha=1.0)

    plt.xlabel('Samples')
    plt.ylabel('Amplitude')
    # plt.hlines([-a, a], 0, T, linestyles='--')
    plt.grid(True)
    plt.axis('auto')
    plt.suptitle('Algorithmic Biofeedback Control System', fontsize=12, fontweight='bold')

    plt.title(title + " " + str(lowcut) + " " + str(highcut) + " " + str(fs))
#     plt.title("Delta" + str(lowcut) + " " + str(highcut) + " " + str(fs))
    plt.legend(loc='upper left')
    create_analysis_parms_text(0.7, 0.95, plt_axes, analysis_parms)    
    create_file_date_text(-0.12, -0.1, 0.8, -0.1, plt_axes, data_fname, date_time_now)

    plt.savefig(plot_fname, dpi=300)

    if args.display_plots:
        plt.show()

    plt.close()

    print("Finished writing " + title + " data plot ")
    print(plot_fname)
    print





def plot_data_avg_power(delta_avg, theta_avg, alpha_avg, beta_avg, gamma_avg, 
                lowcut, highcut, fs, point_sz, 
                title, data_fname, plot_fname):

    logging.info('plot_data_avg_power() called')
    print('plot_data_avg_power() called')

#
#   Generate a scatter plot of the bandpass filtered data    
#

    x_axis = np.arange(len(delta_avg))
#     print("x_axis " , x_axis)

    fig = plt.figure(num=88, figsize=(FIGURE_SIZE), dpi=72, facecolor='w', edgecolor='k')

#     plt.semilogx(x_axis, af7_delta_int, color='y', alpha=0.7, ls='dotted', label='Semilog plot Filtered')

    max = np.max(delta_avg)
    print("max " , max)
    
    plt.axis([0, len(delta_avg), 0, max])

    plt.plot(delta_avg, color='b', alpha=0.7, label='Delta')
    plt.plot(theta_avg, color='g', alpha=0.7, label='Theta')
    plt.plot(alpha_avg, color='r', alpha=0.7, label='Alpha')
    plt.plot(beta_avg, color='c', alpha=0.7, label='Beta')
    plt.plot(beta_avg, color='m', alpha=0.7, label='Gamma')

    plt.scatter(x_axis, delta_avg, s=point_sz, color='b', alpha=1.0)
    plt.scatter(x_axis, theta_avg, s=point_sz, color='g', alpha=1.0)
    plt.scatter(x_axis, alpha_avg, s=point_sz, color='r', alpha=1.0)
    plt.scatter(x_axis, beta_avg, s=point_sz, color='c', alpha=1.0)
    plt.scatter(x_axis, beta_avg, s=point_sz, color='m', alpha=1.0)

    plt.xlabel('Samples')
    plt.ylabel('Amplitude')
    # plt.hlines([-a, a], 0, T, linestyles='--')
    plt.grid(True)
    plt.axis('auto')
    plt.suptitle('Algorithmic Biofeedback Control System', fontsize=12, fontweight='bold')

    plt.title(title + " " + str(lowcut) + " " + str(highcut) + " " + str(fs))
#     plt.title("Delta" + str(lowcut) + " " + str(highcut) + " " + str(fs))
    plt.legend(loc='upper left')
#     fname = 'eeg_semilog_bandpass_data.jpg'       

    plt.savefig(plot_fname, dpi=300)

    if args.display_plots:
        plt.show()

    plt.close()

    print("Finished writing " + title + " data plot ")
    print(plot_fname)
    print





def plot_sensors_power_band(tp9, af7, af8, tp10, 
                        lowcut, highcut, fs, point_sz, title, 
                        data_fname, plot_fname, date_time_now, analysis_parms):

    logging.info('plot_sensors_power_band() called')
    print('plot_sensors_power_band() called')

    print("tp9 " , tp9)
  

    
    fig = plt.figure(num=33, figsize=(FIGURE_SIZE), dpi=72, facecolor='w', edgecolor='k')

#     plt.axis([0, len(tp9), 0, 1])
    plt_axes = plt.gca()
  
    x_axis = np.arange(len(tp9))
    print("x_axis " , x_axis)
    print("len(tp9) " , len(tp9))
    print("args.step_size " , args.step_size)
    print("int(len(tp9)/Integrate_Step_Size " , int(len(tp9)/Integrate_Step_Size))



#     if args.integrate:
#         x_len = int(len(tp9)/Integrate_Step_Size)
# #         x_axis = np.linspace(0.0, x_len)
#         x_axis = np.arange(0.0, x_len)
#     else:
# #         x_axis = np.linspace(0.0, len(tp9))
#         x_axis = np.arange(0.0, len(tp9))



    x_axis = np.arange(0.0, len(tp9))

    x1 = np.linspace(0.0, len(tp9))

    point_sz = 2
    
#     xmin = 0.
#     xmax = len(tp9)
#     ymin = -10.
#     ymax = 100
#     
#     plt_axes.set(xlim=(xmin, xmax), ylim=(ymin, ymax))
 
#     plt_axes.set_ylim([-10.0, 250.0])
#     plt_axes.set_xlim([-10.0, 150])
  
#     print("x1 " , x1)

#     plt.semilogx(x_axis, af7_delta_int, color='y', alpha=0.7, ls='dotted', label='Semilog plot Filtered')

#     plt.scatter(x1, tp9, s=point_sz, color='b', alpha=1.0, label='TP9')
#     plt.scatter(x1, af7, s=point_sz, color='g', alpha=1.0, label='AF7')
#     plt.scatter(x1, af8, s=point_sz, color='r', alpha=1.0, label='AF8')
#     plt.scatter(x1, tp10, s=point_sz, color='c', alpha=1.0, label='TP10')

#     plt.scatter(x_axis, tp9, s=point_sz, color='b', alpha=1.0, label='TP9')
#     plt.scatter(x_axis, af7, s=point_sz, color='g', alpha=1.0, label='AF7')
#     plt.scatter(x_axis, af8, s=point_sz, color='r', alpha=1.0, label='AF8')
#     plt.scatter(x_axis, tp10, s=point_sz, color='c', alpha=1.0, label='TP10')
    plt.plot(x_axis, tp9, color='m', alpha=0.5, ms=point_sz, marker='o', label='TP9')
    plt.plot(x_axis, af7, color='b', alpha=0.5, ms=point_sz, marker='+',label='AF7')
    plt.plot(x_axis, af8, color='g', alpha=0.5, ms=point_sz, marker='*',label='AF8')
    plt.plot(x_axis, tp10, color='#FF00FF', alpha=0.7, ms=point_sz, marker='^', label='TP10')

#     plt.plot(tp9, color='m', alpha=0.7, label='TP9')
#     plt.plot(af7, color='b', alpha=0.7, label='AF7')
#     plt.plot(af8, color='g', alpha=0.7, label='AF8')
#     plt.plot(tp10, color='#FF00FF', alpha=0.7, label='TP10')

 

    plt.xlabel('Time')
    plt.ylabel('Amplitude')
    # plt.hlines([-a, a], 0, T, linestyles='--')
    plt.grid(True)
    plt.suptitle('Algorithmic Biofeedback Control System', fontsize=12, fontweight='bold')

    plt.title(title)
#     plt.title("Delta" + str(lowcut) + " " + str(highcut) + " " + str(fs))
    plt.legend(loc='upper left')
    plt.axis('auto')


    create_analysis_parms_text(0.75, 1.02, plt_axes, analysis_parms)
    create_file_date_text(-0.1, -0.11, 0.9, -0.11, plt_axes, data_fname, date_time_now)


    plt.savefig(plot_fname, dpi=300)

    if args.display_plots:
        plt.show()

    plt.close()

    print("Finished writing " + title + " data plot ")
    print(plot_fname)
    print




# TODO:  Making multiple windows

def plot_all_power_bands(delta, theta, alpha, beta, gamma,
                lowcut, highcut, fs, point_sz, title, 
                data_fname, plot_fname, date_time_now, analysis_parms):

    logging.info('plot_all_power_bands() called')
    print('plot_all_power_bands() called')

    x1 = np.arange(0.0, len(delta))
    x2 = np.arange(0.0, len(theta))
    x3 = np.arange(0.0, len(alpha))
    x4 = np.arange(0.0, len(beta))
    x5 = np.arange(0.0, len(gamma))

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


    l0 = axs[0].plot(x5, gamma,  ms=1, color='#00AAFF', alpha=0.7, label='Gamma')
    axs[0].legend(loc='upper right', prop={'size': 6})     
    axs[0].grid(True)
#     axs[0].hlines([-a, a], 0, T, linestyles='--')

    l1 = axs[1].plot(x4, beta,  ms=1, color='#9FFF00', alpha=0.5, label='Beta')
    axs[1].legend(loc='upper right', prop={'size': 6})
    axs[1].grid(True)
#     axs[1].hlines([-a, a], 0, T, linestyles='--')

    l2 = axs[2].plot(x3, alpha,  ms=1, color='#0000FF', alpha=0.5, label='Alpha')
    axs[2].legend(loc='upper right', prop={'size': 6})
    axs[2].grid(True)
#     axs[2].hlines([-a, a], 0, T, linestyles='--')

    l3 = axs[3].plot(x2, theta,  ms=1, color='#6622AA', alpha=0.5, label='Theta')
    axs[3].legend(loc='upper right', prop={'size': 6})
    axs[3].grid(True)
#     axs[3].hlines([-a, a], 0, T, linestyles='--')

    l4 = axs[4].plot(x1, delta,  ms=1, color='#FF8800', alpha=0.5, label='Delta')
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
    create_file_date_text(-0.12, -0.5, 0.9, -0.5, plt_axes, data_fname, date_time_now)

    
#     plt.legend(loc='upper left')

    plt.savefig(plot_fname, dpi=300)

    if args.display_plots:
        plt.show()

    plt.close()

    print("Finished writing " + title + " data plot ")
    print(plot_fname)
    print





# TODO:  Making multiple windows correctly

# *****************************************

def plot_combined_power_bands(delta_raw, theta_raw, alpha_raw, beta_raw, gamma_raw,
                delta, theta, alpha, beta, gamma,
                lowcut, highcut, fs, point_sz, title, 
                data_fname, plot_fname, date_time_now, analysis_parms):

    logging.info('plot_combined_power_bands() called')
    print('plot_combined_power_bands() called')

    x1 = np.arange(0.0, len(delta))
    x2 = np.arange(0.0, len(theta))
    x3 = np.arange(0.0, len(alpha))
    x4 = np.arange(0.0, len(beta))
    x5 = np.arange(0.0, len(gamma))

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


    l0 = axs[0].plot(x5, gamma_raw, ms=1, color='#00AAFF', alpha=0.7, label='Gamma')
    l00 = axs[0].scatter(x5, gamma, s=1, color='#FFAAFF', alpha=0.7)
    axs[0].legend(loc='upper right', prop={'size': 6})     
    axs[0].grid(True)
#     axs[0].set_xlim([0,2])
    axs[0].set_ylim(y_limits)
    
#     axs[0].hlines([-a, a], 0, T, linestyles='--')

    l1 = axs[1].plot(x4, beta_raw, ms=1, color='#33FF33', alpha=0.7, label='Beta')
    l11 = axs[1].scatter(x5, beta, s=1, color='#33FFFF', alpha=0.7)
    axs[1].legend(loc='upper right', prop={'size': 6})
    axs[1].grid(True)
    axs[1].set_ylim(y_limits)
#     axs[1].hlines([-a, a], 0, T, linestyles='--')

    l2 = axs[2].plot(x3, alpha_raw, ms=1, color='#F000FF', alpha=0.7, label='Alpha')
    l22 = axs[2].scatter(x5, alpha, s=1, color='#00FFFF', alpha=0.7)
    axs[2].legend(loc='upper right', prop={'size': 6})
    axs[2].grid(True)
    axs[2].set_ylim(y_limits)    
#     axs[2].hlines([-a, a], 0, T, linestyles='--')

    l3 = axs[3].plot(x2, theta_raw, ms=1, color='#FF22AA', alpha=0.7, label='Theta')
    l33 = axs[3].scatter(x5, theta, s=1, color='#002200', alpha=0.7)
    axs[3].legend(loc='upper right', prop={'size': 6})
    axs[3].grid(True)
    axs[3].set_ylim(y_limits)
#     axs[3].hlines([-a, a], 0, T, linestyles='--')

    l4 = axs[4].plot(x1, delta_raw, ms=1, color='#FF0000', alpha=0.7, label='Delta')
    l44 = axs[4].scatter(x5, delta, s=1, color='#FF44FF', alpha=0.7)
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
    create_file_date_text(-0.12, -0.5, 0.9, -0.5, plt_axes, data_fname, date_time_now)


#     plt.legend(loc='upper left')
#     fname = 'eeg_semilog_bandpass_data.jpg'       

    plt.savefig(plot_fname, dpi=300)

    if args.display_plots:
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



# *******************************

def plot_3D(muse_EEG_data, filt_df, data_fname, plot_fname, date_time_now, analysis_parms):
  
    logging.info('plot_3D() called')
    print('plot_3D() called')
  
    df = pd.DataFrame(muse_EEG_data, columns=['RAW_TP9', 'RAW_AF7', 'RAW_AF8', 'RAW_TP10']) 

#     af7_filt_band = np.nan_to_num(af7_filt_band)
#     af8_filt_band = np.nan_to_num(af8_filt_band)
#     tp9_filt_band = np.nan_to_num(tp9_filt_band)
#     tp10_filt_band = np.nan_to_num(tp10_filt_band)
    
    af7_filt_band = np.nan_to_num(filt_df['FILT_AF7'])
    af8_filt_band = np.nan_to_num(filt_df['FILT_AF8'])
    tp9_filt_band = np.nan_to_num(filt_df['FILT_TP9'])
    tp10_filt_band = np.nan_to_num(filt_df['FILT_TP10'])
    

#     print("*********************************************************************")
#     print("*********************************************************************")
#         
#     print("type filt_df", type(filt_df['FILT_AF7']))
#     descr_data = filt_df['FILT_AF7'].describe(percentiles=[.4, .5, .6])
#     print("type", type(descr_data))
#     print(descr_data)
#     print(descr_data['count'])
#     print(descr_data['min'])
#     print(descr_data['max'])
#     print(descr_data['std'])
#     print(descr_data['mean'])
#     print(descr_data['40%'])
#     print(descr_data['50%'])
#     print(descr_data['60%'])
#     print(filt_df['FILT_AF7'].quantile())
# 
#     print("*********************************************************************")
#     print("*********************************************************************")


    fig = plt.figure(num=14, figsize=(FIGURE_SIZE), dpi=72, facecolor='w', edgecolor='k')
    
    ax = fig.gca(projection='3d')


#     xs = df['RAW_TP9']
#     xs = np.arange(len(df['RAW_TP9']))
#     tp_ys = df['RAW_TP9']
#     tp_zs = df['RAW_TP10']
#     af_ys = df['RAW_AF7']
#     af_zs = df['RAW_AF8']

    xs = np.arange(len(af7_filt_band))
    tp_ys = tp9_filt_band
    tp_zs = tp10_filt_band
    af_ys = af7_filt_band
    af_zs = af8_filt_band

#     tp_ys = np.clip(tp_ys, descr_data['40%'], descr_data['60%'])
#     tp_zs = np.clip(tp_zs, descr_data['40%'], descr_data['60%'])
#     af_ys = np.clip(af_ys, descr_data['40%'], descr_data['60%'])
#     af_zs = np.clip(af_zs, descr_data['40%'], descr_data['60%'])

#     tp_ys = tp_ys[tp_ys < descr_data['40%']]
#     tp_ys = tp_ys[tp_ys > descr_data['60%']]

#     tp_zs = np.clip(tp_zs, descr_data['40%'], descr_data['60%'])
#     af_ys = np.clip(af_ys, descr_data['40%'], descr_data['60%'])
#     af_zs = np.clip(af_zs, descr_data['40%'], descr_data['60%'])


# arr = arr[arr != 6]

#     for zdir, x, y, z in zip(zdirs, xs, af_ys, af_zs):
#         label = '(%d, %d, %d), dir=%s' % (x, y, z, zdir)
#         ax.text(x, y, z, label, zdir)

#     ax.scatter(xs, ys, zs, c='r', marker='o')
    ax.scatter(tp_zs, tp_ys, tp_zs, s=1, c='g', label='Data ')
    ax.scatter(af_ys, tp_ys, af_zs, s=1, c='r', label='Data 2')

# .plot_wireframe
# plot_surface
# plot_trisurf
# contour
# contourf
# quiver(

    ax.text(9, 0, 0, "Coherence", color='red')

    # Placement 0, 0 would be the bottom left, 1, 1 would be the top right.
#     ax.text2D(0.05, 0.95, "Raw AF7 & AF8", transform=ax.transAxes)
#     ax.text2D(0.05, 0.95, "Raw AF7 & AF8", transform=ax.transAxes)



    # Tweaking display region and labels
    ax.set_xlim(0, np.max(xs))
    ax.set_ylim(np.min(af_ys) - 20., np.max(af_ys) + 20.)
    ax.set_zlim(np.min(af_zs) - 20., np.max(af_zs) + 20.)

#     ax.set_xlim(0, np.max(xs))
#     ax.set_ylim(descr_data['40%'], descr_data['60%'])
#     ax.set_zlim(descr_data['40%'], descr_data['60%'])


#     ax.set_zlim(0, np.max(zs))
#     ax.set_xlim(0, 10)
#     ax.set_ylim(0, 10)
#     ax.set_zlim(0, 10)

    ax.set_xlabel('Samples')
    ax.set_ylabel('RAW_AF7')
    ax.set_zlabel('RAW_AF8')

    plt.savefig(plot_fname, dpi=300)

    if args.display_plots:
        plt.show()

    plt.close()

#     plt.pause(10)





def plot_power_3D(muse_EEG_data, pwr_df, data_fname, plot_fname, date_time_now, analysis_parms):
 
    logging.info('plot_power_3D() called')
    print('plot_power_3D() called')

  
#     df = pd.DataFrame(muse_EEG_data, columns=['RAW_TP9', 'RAW_AF7', 'RAW_AF8', 'RAW_TP10']) 

#          power_d = {'PWR_DELTA': all_delta, 'PWR_THETA': all_theta, 
#                     'PWR_ALPHA': all_alpha, 'PWR_BETA': all_beta, 'PWR_GAMMA': all_gamma}
  
#     all_delta = np.nan_to_num(pwr_df['PWR_DELTA'])
#     all_theta = np.nan_to_num(pwr_df['PWR_THETA'])
#     all_alpha = np.nan_to_num(pwr_df['PWR_ALPHA'])
#     all_beta = np.nan_to_num(pwr_df['PWR_BETA'])
#     all_gamma = np.nan_to_num(pwr_df['PWR_GAMMA'])

   
    all_delta = np.nan_to_num(pwr_df['PWR_DELTA'])
    all_theta = np.nan_to_num(pwr_df['PWR_THETA'])
    all_alpha = np.nan_to_num(pwr_df['PWR_ALPHA'])
    all_beta = np.nan_to_num(pwr_df['PWR_BETA'])
    all_gamma = np.nan_to_num(pwr_df['PWR_GAMMA'])
    
    
#     print("*********************************************************************")
#     print("*********************************************************************")
#         
#     print("type filt_df", type(pwr_df['PWR_DELTA']))
#     descr_data = pwr_df['PWR_DELTA'].describe(percentiles=[.4, .5, .6])
#     print("type", type(descr_data))
#     print(descr_data)
#     print(descr_data['count'])
#     print(descr_data['min'])
#     print(descr_data['max'])
#     print(descr_data['std'])
#     print(descr_data['mean'])
#     print(descr_data['40%'])
#     print(descr_data['50%'])
#     print(descr_data['60%'])
#     print(pwr_df['PWR_GAMMA'].quantile())
# 
#     print("*********************************************************************")
#     print("*********************************************************************")
 
     
    fig = plt.figure(num=15, figsize=(FIGURE_SIZE), dpi=72, facecolor='w', edgecolor='k')

    ax = fig.gca(projection='3d')
#     ax = fig.add_subplot(111, projection='3d')
  
    xs = np.arange(len(all_delta))

#     print("len(all_delta) ", len(all_delta))
#     print("len(all_theta) ", len(all_theta))
#     print("len(all_alpha) ", len(all_alpha))
#     print("len(all_beta) ", len(all_beta))
#     print("len(all_gamma) ", len(all_gamma))
    
    
#     ax.scatter(xs, ys, zs, c='r', marker='o')
#     ax.scatter(xs, af_ys, af_zs, s=1, c='r', label='AF')
    ax.scatter(all_beta, all_delta, all_theta, s=3, c='g', label='One')
    ax.scatter(all_alpha, all_delta, all_gamma, s=3, c='r', label='Two')

#     X = np.arange(-5, 5, 0.25)
#     Y = np.arange(-5, 5, 0.25)

#     X = np.arange(0, len(all_delta), 2.5)
#     Y = np.arange(0, len(all_theta), 2.5)
# 
# 
#     X, Y = np.meshgrid(X, Y)
# 
#     R = np.sqrt(X**2 + Y**2)
#     Z = np.sin(R)
#     print("R ", R)
#     print("Z ", Z)



#     R = np.sqrt(all_delta**2 + all_theta**2)
#     Z = np.sin(R)
#     print(" R ", R)
#     print(" Z ", Z)
#     print("all_delta ", all_delta)
#     print("all_theta ", all_theta)


#     all_delta, all_theta = np.meshgrid(all_delta, all_theta)
#     all_alpha, all_beta = np.meshgrid(all_alpha, all_beta)
#     print("all_delta ", all_delta)
#     print("all_theta ", all_theta)
# 
#  
#     ax.plot_surface(all_delta, all_theta, all_alpha, cmap=cm.coolwarm,
#                        linewidth=0, antialiased=False)

#     ax.plot_wireframe(all_delta, all_theta, all_alpha, cmap=cm.coolwarm,
#                        linewidth=1, antialiased=False)
 
#     u = np.sin(np.pi * all_delta) * np.cos(np.pi * all_theta) * np.cos(np.pi * all_alpha)
#     v = -np.cos(np.pi * all_delta) * np.sin(np.pi * all_theta) * np.cos(np.pi * all_alpha)
#     w = (np.sqrt(2.0 / 3.0) * np.cos(np.pi * all_delta) * np.cos(np.pi * all_theta) *
#          np.sin(np.pi * all_alpha))
#    
#     ax.quiver(all_delta, all_theta, all_alpha, u, v, w, length=0.1, normalize=True)
    
#     ax.plot_trisurf(all_delta, all_theta, all_alpha)
#     ax.contour(all_delta, all_theta, all_alpha)
#     ax.contourf(all_delta, all_theta, all_alpha)
    

  
# Plot the surface.
# surf = ax.plot_surface(X, Y, Z, cmap=cm.coolwarm,
#                        linewidth=0, antialiased=False)



# Make the grid
# x, y, z = np.meshgrid(np.arange(-0.8, 1, 0.2),
#                       np.arange(-0.8, 1, 0.2),
#                       np.arange(-0.8, 1, 0.8))
# 
# # Make the direction data for the arrows
# u = np.sin(np.pi * x) * np.cos(np.pi * y) * np.cos(np.pi * z)
# v = -np.cos(np.pi * x) * np.sin(np.pi * y) * np.cos(np.pi * z)
# w = (np.sqrt(2.0 / 3.0) * np.cos(np.pi * x) * np.cos(np.pi * y) *
#      np.sin(np.pi * z))
# 
# ax.quiver(x, y, z, u, v, w, length=0.1, normalize=True)
# 
# 
# 

    ax.text(9, 0, 0, "Coherence", color='red')

    # Tweaking display region and labels
#     ax.set_xlim(0, np.max(xs))
    ax.set_xlim(np.min(all_theta) - 1., np.max(all_theta) + 1.)
    ax.set_ylim(np.min(all_theta) - 1., np.max(all_theta) + 1.)
    ax.set_zlim(np.min(all_delta) - 1., np.max(all_delta) + 1.)

#     ax.set_xlim(0, np.max(xs))
#     ax.set_ylim(descr_data['40%'], descr_data['60%'])
#     ax.set_zlim(descr_data['40%'], descr_data['60%'])
#     ax.set_zlim(0, np.max(zs))
#     ax.set_xlim(0, 10)
#     ax.set_ylim(0, 10)
#     ax.set_zlim(0, 10)

    ax.set_xlabel('Data 0')
    ax.set_ylabel('Data 1')
    ax.set_zlabel('Data 2')

    plt.savefig(plot_fname, dpi=300)

    if args.display_plots:
        plt.show()

    plt.close()






def plot_accel_gryo_data(acc_gyro_df, title, data_fname, plot_fname, date_time_now, analysis_parms):

    logging.info('plot_accel_gryo_data() called')
    print('plot_accel_gryo_data() called')

# ['Accelerometer_X', 'Accelerometer_Y', 'Accelerometer_Z', 'Gyro_X', 'Gyro_Y', 'Gyro_Z']
                  
    x_axis = np.arange(len(acc_gyro_df['Accelerometer_X']))

#     plt.figure(num=16, figsize=(FIGURE_SIZE), dpi=72, facecolor='w', edgecolor='k')

    fig, axs = plt.subplots(6, num=24, figsize=(FIGURE_SIZE), sharex=True, sharey=True, gridspec_kw={'hspace': 0})
#     fig.subplots_adjust(top=0.85)

    plt_axes = plt.gca()
    plt.axis('auto')

    plt.ylabel('Accelerometer')
            
    l0 = axs[0].plot(x_axis, acc_gyro_df['Accelerometer_X'], ms=1, color='#00AAFF', alpha=0.8, label='X')
    axs[0].legend(loc='upper right', prop={'size': 6})     
    axs[0].grid(True)

    l1 = axs[1].plot(x_axis, acc_gyro_df['Accelerometer_Y'], ms=1, color='#33FF33', alpha=0.8, label='Y')
    axs[1].legend(loc='upper right', prop={'size': 6})
    axs[1].grid(True)

    l2 = axs[2].plot(x_axis, acc_gyro_df['Accelerometer_Z'], ms=1, color='#FF8800', alpha=0.8, label='Z')
    axs[2].legend(loc='upper right', prop={'size': 6})
    axs[2].grid(True)

    l3 = axs[3].plot(x_axis, acc_gyro_df['Gyro_X'], ms=1, color='#00AAFF', alpha=0.8, label='X')
    axs[3].legend(loc='upper right', prop={'size': 6})     
    axs[3].grid(True)

    l4 = axs[4].plot(x_axis, acc_gyro_df['Gyro_Y'], ms=1, color='#33FF33', alpha=0.8, label='Y')
    axs[4].legend(loc='upper right', prop={'size': 6})
    axs[4].grid(True)

    l5 = axs[5].plot(x_axis, acc_gyro_df['Gyro_Z'], ms=1, color='#FF8800', alpha=0.8, label='Z')
    axs[5].legend(loc='upper right', prop={'size': 6})
    axs[5].grid(True)

    plt.suptitle('Algorithmic Biofeedback Control System', fontsize=12, fontweight='bold')
#     plt.title(title)
       
    create_file_date_text(-0.1, -0.5, 0.85, -0.5, plt_axes, data_fname, date_time_now)
    create_analysis_parms_text(0.7, 6.07, plt_axes, analysis_parms)

    plt.savefig(plot_fname, dpi=300)

    if args.display_plots:
        plt.show()
 
    plt.close()

    print("Finished writing accel/gyro data plot ")
    print(plot_fname)
    print



   
def plot_filter_data(x, y, title, data_fname, plot_fname, date_time_now, analysis_parms):

    logging.info('plot_filter_data() called')
    print('plot_filter_data() called')


    x_axis = np.arange(len(x))

#     plt.clf()
    plt_axes = plt.gca()

    plt.figure(num=31, figsize=(FIGURE_SIZE), dpi=72, facecolor='w', edgecolor='k')
    plt.scatter(x_axis, x, s=1, color='g', alpha=1.0, label='X')
    plt.scatter(x_axis, y, s=1, color='r', alpha=1.0, label='Y')
    plt.xlabel('X')
    plt.ylabel('Y')
    
#     matplotlib.pyplot.hlines(y, xmin, xmax, colors='k', linestyles='solid', label='', *, data=None, **kwargs)
    
#     plt.hlines([-a, a], 0, T, linestyles='--')
    
    
    plt.grid(True)
    plt.axis('auto')
    plt.suptitle('Algorithmic Biofeedback Control System', fontsize=12, fontweight='bold')
    plt.title(title)
    plt.legend(loc='upper left')
       
#     plt.text(-0.12, -0.11, "file: " + data_fname, 
#         transform=axes.transAxes, fontsize=5, style='italic',
#         bbox={'facecolor':'blue', 'alpha':0.1, 'pad':4})
# 
#     plt.text(0.9, -0.11, "Date: " + date_time_now, 
#         transform=axes.transAxes, fontsize=5, style='italic',
#         bbox={'facecolor':'blue', 'alpha':0.1, 'pad':4})
         
    create_analysis_parms_text(0.75, 1.02, plt_axes, analysis_parms)
    create_file_date_text(-0.12, -0.11, 0.9, -0.11, plt_axes, data_fname, date_time_now)

    plt.savefig(plot_fname, dpi=300)

    if args.display_plots:
        plt.show()

    plt.close()
    print("Finished writing filter data plot ")
    print(plot_fname)
    print

# pyplot.hlines(y, xmin, xmax, colors='k', linestyles='solid', label='', *, data=None, **kwargs)[source]




def plot_noise_data(x_len, data, title, data_fname, plot_fname, date_time_now):

    logging.info('plot_noise_data() called')
    print('plot_noise_data() called')

    x_axis = np.arange(x_len)

#     plt.clf()
    axes = plt.gca()

    plt.figure(num=35, figsize=(FIGURE_SIZE), dpi=72, facecolor='w', edgecolor='k')
#     plt.plot(x_axis, data, ms=1, color='r', alpha=0.8, label='Data')
    plt.scatter(x_axis, data, s=1, color='g', alpha=1.0, label='Data')
    plt.xlabel('X')
    plt.ylabel('Y')
    
#     matplotlib.pyplot.hlines(y, xmin, xmax, colors='k', linestyles='solid', label='', *, data=None, **kwargs)
    
#     plt.hlines([-a, a], 0, T, linestyles='--')
    
    
    plt.grid(True)
    plt.axis('auto')
    plt.suptitle('Algorithmic Biofeedback Control System', fontsize=12, fontweight='bold')
    plt.title(title)
    plt.legend(loc='upper left')
                
    plt.savefig(plot_fname, dpi=300)

    if args.display_plots:
        plt.show()

    plt.close()
    print("Finished writing filter data plot ")
    print(plot_fname)
    print

# pyplot.hlines(y, xmin, xmax, colors='k', linestyles='solid', label='', *, data=None, **kwargs)[source]



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

    ensure_dir("./plots/")

    df = pd.DataFrame(muse_EEG_data, columns=['RAW_TP9', 'RAW_AF7', 'RAW_AF8', 'RAW_TP10'])    
#     df = np.clip(df, -100.0, 100.0)


    IPython_default = plt.rcParams.copy()
#     print("IPython_default: ", IPython_default)


                      
    print("SAMPLING_RATE: ", SAMPLING_RATE)
    print("Filter_Lowcut: ", Filter_Lowcut)
    print("Filter_Highcut: ", Filter_Highcut)
    print("Filter_Order: ", Filter_Order)



    sample_length = len(df['RAW_AF7'])
    sample_time_sec = (sample_length/SAMPLING_RATE)
    sample_time_min = sample_time_sec/60.0

    T = 0.05
#     T = sample_time_sec
    nsamples = T * SAMPLING_RATE
    t = np.linspace(0, T, nsamples, endpoint=False)
    a = 0.02
    
    analysis_parms = {"lowcut":Filter_Lowcut, "highcut": Filter_Highcut, "filter_order":Filter_Order, 
                        "sample_length":sample_length, "sample_time_sec":sample_time_sec, 
                        "sample_time_min":sample_time_min}
    
    
    print("T: ", T)
    print("nsamples: ", nsamples)
    print("t: ", t)
    print("a: ", a)
    
    print("sample_length: ", sample_length)
    print("sample_time_sec: ", sample_time_sec)
    print("sample_time_min: ", sample_time_min)
    print


    if args.power_spectrum:
    
        (freqs, idx, ps) = analyze_eeg_data(df['RAW_AF7'])
        x_data = np.arange(sample_length)

        plot_filter_data(idx, freqs, "FFT", data_fname, 
            './plots/70-ABCS_FFT_' + date_time_now + '.jpg', date_time_now, analysis_parms)

        plot_filter_data(x_data, ps, "FFT", data_fname,
            './plots/71-ABCS_PS_' + date_time_now + '.jpg', date_time_now, analysis_parms)

 
 
# Integrate AF7 & AF8 data
    tp9_integration_res = integrate_eeg_data(df['RAW_TP9'], 'RAW_TP9', data_fname)
    af8_integration_res = integrate_eeg_data(df['RAW_AF8'], 'RAW_AF8', data_fname)
    af7_integration_res = integrate_eeg_data(df['RAW_AF7'], 'RAW_AF7', data_fname)
    tp10_integration_res = integrate_eeg_data(df['RAW_TP10'], 'RAW_TP10', data_fname)
    
    # Scale integrated data
#     af7_integration_res = scale(af7_integration_res, out_range=(-100, 100))
#     af8_integration_res = scale(af8_integration_res, out_range=(-100, 100))

    
#     af7_avg = np.average(df['RAW_AF7'])
#     af8_avg = np.average(df['RAW_AF8'])
#     print("AF7 & AF8 averaged: ", af7_avg, af8_avg)
#     print

    
# Generate plots 


    if args.eeg:    

#         plot_scatter_xy(df['RAW_AF7'], df['RAW_AF8'], data_fname, 
#                 plot_fname = './plots/101-ABCS_eeg_raw_xy_data_' + date_time_now + '.jpg')


        if args.integrate:
            plot_coherence(af7_integration_res, af8_integration_res,
                            tp9_integration_res, tp10_integration_res,
                            "EF7 & EF8 Integrated Data - Coherance", data_fname,   
                    './plots/0-ABCS_eeg_int_coherence_' + date_time_now + '.jpg', date_time_now, analysis_parms)

#             plot_scatter_xy(af7_integration_res, af8_integration_res, data_fname, 
#                     plot_fname = './plots/100-ABCS_eeg_xy_data_' + date_time_now + '.jpg')

            plot_time_series_data(af7_integration_res, af8_integration_res, data_fname, 
                './plots/2-ABCS_eeg_AF7_AF8_time_series_data_' + date_time_now + '.jpg',
                date_time_now, analysis_parms)

            plot_time_series_data(tp9_integration_res, tp10_integration_res, data_fname, 
                './plots/2-ABCS_eeg_TP9_TP10_time_series_data_' + date_time_now + '.jpg',
                date_time_now, analysis_parms)



        plot_coherence(df['RAW_AF7'], df['RAW_AF8'], df['RAW_TP9'], df['RAW_TP10'],
            "EF7 & EF8 Raw Data - Coherance", data_fname,
            './plots/1-ABCS_eeg_raw_coherence_data_' + date_time_now + '.jpg', date_time_now, analysis_parms)


#         plot_cumsum_data(af7_integration_res, af8_integration_res, data_fname, 
#             plot_fname = './plots/3-ABCS_eeg_integrate_cumsum_data_' + date_time_now + '.jpg')
# 

#         plot_scatter_data(df, data_fname, 
#             plot_fname = './plots/4-ABCS_eeg_scatter_data_' + date_time_now + '.jpg')


#     plot_histogram(af7_integration_res, af8_integration_res, data_fname, 
#         plot_fname = '5-ABCS_eeg_histogram_' + date_time_now + '.jpg')



#     data_len = len(df['RAW_AF7'])
# #     x_axis = np.arange(data_len)
#     print("data_len ", data_len)
#     print
#    
#     noise = 2 * np.random.random(data_len) - 1 # uniformly distributed between -1 and 1
#     print("noise ", noise)
# 
#     plot_noise_data(data_len, noise, "Noise", "N/A", 
#         './plots/90-ABCS_noise_' + date_time_now + '.jpg', date_time_now)
# 
#     noise_bandpass = butter_bandpass_filter(noise, Filter_Lowcut, Filter_Highcut, SAMPLING_RATE, Filter_Order)
#     plot_noise_data(data_len, noise_bandpass, "Noise/Bandpass", "N/A", 
#         './plots/91-ABCS_noise_bandpass_' + date_time_now + '.jpg', date_time_now)
# 
# 
#     Filter_Order = 24 
#     
#     noise_lowpass = butter_lowpass_filter(noise, Filter_Highcut, SAMPLING_RATE, Filter_Order)
#     plot_noise_data(data_len, noise_bandpass, "Noise/Lowpass", "N/A", 
#         './plots/92-ABCS_noise_lowpass_' + date_time_now + '.jpg', date_time_now)
# 
#     noise_lowpass = butter_lowpass_filter(noise_lowpass, Filter_Highcut, SAMPLING_RATE, Filter_Order)
#     plot_noise_data(data_len, noise_bandpass, "Noise/Lowpass", "N/A", 
#         './plots/92-ABCS_noise_lowpass2_' + date_time_now + '.jpg', date_time_now)
# 
#     noise_lowpass = butter_lowpass_filter(noise_lowpass, Filter_Highcut, SAMPLING_RATE, Filter_Order)
#     plot_noise_data(data_len, noise_bandpass, "Noise/Lowpass", "N/A", 
#         './plots/92-ABCS_noise_lowpass3_' + date_time_now + '.jpg', date_time_now)
# 
#     noise_lowpass = butter_lowpass_filter(noise_lowpass, Filter_Highcut, SAMPLING_RATE, Filter_Order)
#     plot_noise_data(data_len, noise_bandpass, "Noise/Lowpass", "N/A", 
#         './plots/92-ABCS_noise_lowpass4_' + date_time_now + '.jpg', date_time_now)
# 
# 



# Filtered plots

    if args.filter_data:

        print("Runnning filters on raw AF7 & AF8 data")
        print

        # Run bandpass filters
        tp9_filt_band = butter_bandpass_filter(df['RAW_TP9'], Filter_Lowcut, Filter_Highcut, SAMPLING_RATE, Filter_Order)
        af8_filt_band = butter_bandpass_filter(df['RAW_AF8'], Filter_Lowcut, Filter_Highcut, SAMPLING_RATE, Filter_Order)
        af7_filt_band = butter_bandpass_filter(df['RAW_AF7'], Filter_Lowcut, Filter_Highcut, SAMPLING_RATE, Filter_Order)
        tp10_filt_band = butter_bandpass_filter(df['RAW_TP10'], Filter_Lowcut, Filter_Highcut, SAMPLING_RATE, Filter_Order)


        tp9_filt_lowpass = butter_lowpass_filter(df['RAW_TP9'], Filter_Highcut, SAMPLING_RATE, Filter_Order)
        af8_filt_lowpass = butter_lowpass_filter(df['RAW_AF8'], Filter_Highcut, SAMPLING_RATE, Filter_Order)
        af7_filt_lowpass = butter_lowpass_filter(df['RAW_AF7'], Filter_Highcut, SAMPLING_RATE, Filter_Order)
        tp10_filt_lowpass = butter_lowpass_filter(df['RAW_TP10'], Filter_Highcut, SAMPLING_RATE, Filter_Order)

#         af7_filt_lowpass = butter_lowpass_filter(af7_filtered, Filter_Highcut, (0.5 * SAMPLING_RATE), Filter_Order)
#         af8_filt_lowpass = butter_lowpass_filter(af8_filtered, Filter_Highcut, (0.5 * SAMPLING_RATE), Filter_Order)


        tp9_filt_band_low = butter_bandpass_filter(tp9_filt_lowpass, 
                                Filter_Lowcut, Filter_Highcut, SAMPLING_RATE, Filter_Order)
        af8_filt_band_low = butter_bandpass_filter(af8_filt_lowpass, 
                                Filter_Lowcut, Filter_Highcut, SAMPLING_RATE, Filter_Order)
        af7_filt_band_low = butter_bandpass_filter(af7_filt_lowpass, 
                                Filter_Lowcut, Filter_Highcut, SAMPLING_RATE, Filter_Order)
        tp10_filt_band_low = butter_bandpass_filter(tp10_filt_lowpass, 
                                Filter_Lowcut, Filter_Highcut, SAMPLING_RATE, Filter_Order)




    # Generated filtered data plots
    if args.filter_data:    

# TODO figure out log plots
#         plot_semilog_bandpass(af7_filtered, af8_filtered, Filter_Lowcut, Filter_Highcut, SAMPLING_RATE, data_fname, 
#             plot_fname = './plots/6-ABCS_semilog_bandpass_' + date_time_now + '.jpg')



#         plot_filter_data(af8_filt_band, af8_filt_band,
#             "EF7 & EF8 Bandpass Data", data_fname, 
#             './plots/7-ABCS_bandpass_' + date_time_now + '.jpg', date_time_now, analysis_parms)
# 
#         plot_filter_data(af7_filt_lowpass, af8_filt_lowpass,
#         "EF7 & EF8 Low Pass Data", data_fname, 
#             './plots/8-ABCS_lowpass_' + date_time_now + '.jpg', date_time_now, analysis_parms)
# 
#         plot_filter_data(af7_filt_band_low, af8_filt_band_low,  
#             "EF7 & EF8 Bandpass/Low Pass Data",
#              data_fname, './plots/9-ABCS_band_low_' + date_time_now + '.jpg', date_time_now, analysis_parms)



        plot_time_series_data(af8_filt_band, af8_filt_band, data_fname,
            './plots/7-ABCS_bandpass_' + date_time_now + '.jpg', date_time_now, analysis_parms)

        plot_time_series_data(af7_filt_lowpass, af8_filt_lowpass, data_fname,
            './plots/8-ABCS_lowpass_' + date_time_now + '.jpg', date_time_now, analysis_parms)

        plot_time_series_data(af7_filt_band_low, af8_filt_band_low, data_fname,
             './plots/9-ABCS_band_low_' + date_time_now + '.jpg', date_time_now, analysis_parms)




        plot_coherence(af7_filt_band, af8_filt_band, tp9_filt_band, tp10_filt_band,
            "EF7 & EF8 Bandpass Filtered - Coherance", data_fname,
            './plots/9-ABCS_eeg_bandpass_coherence_data_' + date_time_now + '.jpg', date_time_now, analysis_parms)

        plot_coherence(af7_filt_lowpass, af8_filt_lowpass, tp9_filt_band, tp10_filt_band,
            "EF7 & EF8 Lowpass Filtered - Coherance", data_fname,
            './plots/9-ABCS_eeg_bandpass_coherence_data_' + date_time_now + '.jpg', date_time_now, analysis_parms)

        plot_coherence(af8_filt_band_low, af8_filt_band_low, tp9_filt_band, tp10_filt_band,
            "EF7 & EF8 Band/Lowpass Filtered - Coherance", data_fname,
            './plots/9-ABCS_eeg_low_bandpass_coherence_data_' + date_time_now + '.jpg', date_time_now, analysis_parms)




        if False:
#         if args.plot_3D:

            filt_d = {'FILT_AF7': af7_filt_band, 'FILT_AF8': af8_filt_band, 
                        'FILT_TP9': tp9_filt_band, 'FILT_TP10': tp10_filt_band}

    #         filt_df = DataFrame([data, index, columns, dtype, copy])
            filt_df = pd.DataFrame(filt_d, dtype=np.float64)

            pause_and_prompt(0.1, "Plotting 3D")

            plot_3D(muse_EEG_data, filt_df, data_fname,
                './plots/77-ABCS_3D_' + date_time_now + '.jpg', date_time_now, analysis_parms)

        
        

# Delta_TP9,Delta_AF7,Delta_AF8,Delta_TP10,
# Theta_TP9,Theta_AF7,Theta_AF8,Theta_TP10,
# Alpha_TP9,Alpha_AF7,Alpha_AF8,Alpha_TP10,
# Beta_TP9,Beta_AF7,Beta_AF8,Beta_TP10,
# Gamma_TP9,Gamma_AF7,Gamma_AF8,Gamma_TP10,
# RAW_TP9,RAW_AF7,RAW_AF8,RAW_TP10,AUX_RIGHT,
# Mellow,Concentration,

    raw_df = pd.DataFrame(muse_EEG_data, columns=['RAW_TP9', 'RAW_AF7', 'RAW_AF8', 'RAW_TP10'])    
#     df = np.clip(df, -1.0, 1.0)

#     print("Data description\n", raw_df.describe())                    

    delta_df = pd.DataFrame(muse_EEG_data, columns=['Delta_TP9', 'Delta_AF7', 'Delta_AF8', 'Delta_TP10'])    
#     print("Data description\n", delta_df.describe())                    
    theta_df = pd.DataFrame(muse_EEG_data, columns=['Theta_TP9', 'Theta_AF7', 'Theta_AF8', 'Theta_TP10'])    
#     print("Data description\n", theta_df.describe())                    
    alpha_df = pd.DataFrame(muse_EEG_data, columns=['Alpha_TP9', 'Alpha_AF7', 'Alpha_AF8', 'Alpha_TP10'])    
#     print("Data description\n", alpha_df.describe())                    
    beta_df = pd.DataFrame(muse_EEG_data, columns=['Beta_TP9', 'Beta_AF7', 'Beta_AF8', 'Beta_TP10'])    
#     print("Data description\n", beta_df.describe())                    
    gamma_df = pd.DataFrame(muse_EEG_data, columns=['Gamma_TP9', 'Gamma_AF7', 'Gamma_AF8', 'Gamma_TP10'])    
#     print("Data description\n", gamma_df.describe())                    




# Integrate data

    tp9_delta_int = integrate_eeg_data(delta_df['Delta_TP9'], 'Delta_TP9', data_fname)
    af7_delta_int = integrate_eeg_data(delta_df['Delta_AF7'], 'Delta_AF7', data_fname)
    af8_delta_int = integrate_eeg_data(delta_df['Delta_AF8'], 'Delta_AF8', data_fname)
    tp10_delta_int = integrate_eeg_data(delta_df['Delta_TP10'], 'Delta_TP10', data_fname)

    tp9_theta_int = integrate_eeg_data(theta_df['Theta_TP9'], 'Theta_TP9', data_fname)
    af7_theta_int = integrate_eeg_data(theta_df['Theta_AF7'], 'Theta_AF7', data_fname)
    af8_theta_int = integrate_eeg_data(theta_df['Theta_AF8'], 'Theta_AF8', data_fname)
    tp10_theta_int = integrate_eeg_data(theta_df['Theta_TP10'], 'Theta_TP10', data_fname)

    tp9_alpha_int = integrate_eeg_data(alpha_df['Alpha_TP9'], 'Alpha_TP9', data_fname)
    af7_alpha_int = integrate_eeg_data(alpha_df['Alpha_AF7'], 'Alpha_AF7', data_fname)
    af8_alpha_int = integrate_eeg_data(alpha_df['Alpha_AF8'], 'Alpha_AF8', data_fname)
    tp10_alpha_int = integrate_eeg_data(alpha_df['Alpha_TP10'], 'Alpha_TP10', data_fname)

    tp9_beta_int = integrate_eeg_data(beta_df['Beta_TP9'], 'Beta_TP9', data_fname)
    af7_beta_int = integrate_eeg_data(beta_df['Beta_AF7'], 'Beta_AF7', data_fname)
    af8_beta_int = integrate_eeg_data(beta_df['Beta_AF8'], 'Beta_AF8', data_fname)
    tp10_beta_int = integrate_eeg_data(beta_df['Beta_TP10'], 'Beta_TP10', data_fname)

    tp9_gamma_int = integrate_eeg_data(gamma_df['Gamma_TP9'], 'Gamma_TP9', data_fname)
    af7_gamma_int = integrate_eeg_data(gamma_df['Gamma_AF7'], 'Gamma_AF7', data_fname)
    af8_gamma_int = integrate_eeg_data(gamma_df['Gamma_AF8'], 'Gamma_AF8', data_fname)
    tp10_gamma_int = integrate_eeg_data(gamma_df['Gamma_TP10'], 'Gamma_TP10', data_fname)

    
#     af7_delta_int = scale(af7_delta_int, out_range=(-100, 100))
#     af8_delta_int = scale(af8_delta_int, out_range=(-100, 100))


    if args.filter_data:
        print("Runnning filters on power band data")
        print

        run_bandpass = True
        
        # Run bandpass filters
        if run_bandpass:
            tp9_delta_filtered = butter_bandpass_filter(tp9_delta_int, 
                Filter_Lowcut, Filter_Highcut, SAMPLING_RATE, Filter_Order)
            af7_delta_filtered = butter_bandpass_filter(af7_delta_int, 
                Filter_Lowcut, Filter_Highcut, SAMPLING_RATE, Filter_Order)
            af8_delta_filtered = butter_bandpass_filter(af8_delta_int, 
                Filter_Lowcut, Filter_Highcut, SAMPLING_RATE, Filter_Order)
            tp10_delta_filtered = butter_bandpass_filter(tp10_delta_int, 
                Filter_Lowcut, Filter_Highcut, SAMPLING_RATE, Filter_Order)

            tp9_theta_filtered = butter_bandpass_filter(tp9_theta_int, 
                Filter_Lowcut, Filter_Highcut, SAMPLING_RATE, Filter_Order)
            af7_theta_filtered = butter_bandpass_filter(af7_theta_int, 
                Filter_Lowcut, Filter_Highcut, SAMPLING_RATE, Filter_Order)
            af8_theta_filtered = butter_bandpass_filter(af8_theta_int, 
                Filter_Lowcut, Filter_Highcut, SAMPLING_RATE, Filter_Order)
            tp10_theta_filtered = butter_bandpass_filter(tp10_theta_int, 
                Filter_Lowcut, Filter_Highcut, SAMPLING_RATE, Filter_Order)

            tp9_alpha_filtered = butter_bandpass_filter(tp9_alpha_int, 
                Filter_Lowcut, Filter_Highcut, SAMPLING_RATE, Filter_Order)
            af7_alpha_filtered = butter_bandpass_filter(af7_alpha_int, 
                Filter_Lowcut, Filter_Highcut, SAMPLING_RATE, Filter_Order)
            af8_alpha_filtered = butter_bandpass_filter(af8_alpha_int, 
                Filter_Lowcut, Filter_Highcut, SAMPLING_RATE, Filter_Order)
            tp10_alpha_filtered = butter_bandpass_filter(tp10_alpha_int, 
                Filter_Lowcut, Filter_Highcut, SAMPLING_RATE, Filter_Order)

            tp9_beta_filtered = butter_bandpass_filter(tp9_beta_int, 
                Filter_Lowcut, Filter_Highcut, SAMPLING_RATE, Filter_Order)
            af7_beta_filtered = butter_bandpass_filter(af7_beta_int, 
                Filter_Lowcut, Filter_Highcut, SAMPLING_RATE, Filter_Order)
            af8_beta_filtered = butter_bandpass_filter(af8_beta_int, 
                Filter_Lowcut, Filter_Highcut, SAMPLING_RATE, Filter_Order)
            tp10_beta_filtered = butter_bandpass_filter(tp10_beta_int, 
                Filter_Lowcut, Filter_Highcut, SAMPLING_RATE, Filter_Order)

            tp9_gamma_filtered = butter_bandpass_filter(tp9_gamma_int, 
                Filter_Lowcut, Filter_Highcut, SAMPLING_RATE, Filter_Order)
            af7_gamma_filtered = butter_bandpass_filter(af7_gamma_int, 
                Filter_Lowcut, Filter_Highcut, SAMPLING_RATE, Filter_Order)
            af8_gamma_filtered = butter_bandpass_filter(af8_gamma_int, 
                Filter_Lowcut, Filter_Highcut, SAMPLING_RATE, Filter_Order)
            tp10_gamma_filtered = butter_bandpass_filter(tp10_gamma_int, 
                Filter_Lowcut, Filter_Highcut, SAMPLING_RATE, Filter_Order)


        # Run low pass filters
        run_lowpass = False
        if run_lowpass:

            tp9_delta_filtered = butter_lowpass_filter(tp9_delta_int, 
                Filter_Highcut, (SAMPLING_RATE), Filter_Order)
            af7_delta_filtered = butter_lowpass_filter(af7_delta_int, 
                Filter_Highcut, (SAMPLING_RATE), Filter_Order)
            af8_delta_filtered = butter_lowpass_filter(af8_delta_int, 
                Filter_Highcut, (SAMPLING_RATE), Filter_Order)
            tp10_delta_filtered = butter_lowpass_filter(tp10_delta_int, 
                Filter_Highcut, (SAMPLING_RATE), Filter_Order)

            tp9_theta_filtered = butter_lowpass_filter(tp9_theta_int, 
                Filter_Highcut, (SAMPLING_RATE), Filter_Order)
            af7_theta_filtered = butter_lowpass_filter(af7_theta_int, 
                Filter_Highcut, (SAMPLING_RATE), Filter_Order)
            af8_theta_filtered = butter_lowpass_filter(af8_theta_int, 
                Filter_Highcut, (SAMPLING_RATE), Filter_Order)
            tp10_theta_filtered = butter_lowpass_filter(tp10_theta_int, 
                Filter_Highcut, (SAMPLING_RATE), Filter_Order)

            tp9_alpha_filtered = butter_lowpass_filter(tp9_alpha_int, 
                Filter_Highcut, (SAMPLING_RATE), Filter_Order)
            af7_alpha_filtered = butter_lowpass_filter(af7_alpha_int, 
                Filter_Highcut, (SAMPLING_RATE), Filter_Order)
            af8_alpha_filtered = butter_lowpass_filter(af8_alpha_int, 
                Filter_Highcut, (SAMPLING_RATE), Filter_Order)
            tp10_alpha_filtered = butter_lowpass_filter(tp10_alpha_int, 
                Filter_Highcut, (SAMPLING_RATE), Filter_Order)

            tp9_beta_filtered = butter_lowpass_filter(tp9_beta_int, 
                Filter_Highcut, (SAMPLING_RATE), Filter_Order)
            af7_beta_filtered = butter_lowpass_filter(af7_beta_int, 
                Filter_Highcut, (SAMPLING_RATE), Filter_Order)
            af8_beta_filtered = butter_lowpass_filter(af8_beta_int, 
                Filter_Highcut, (SAMPLING_RATE), Filter_Order)
            tp10_beta_filtered = butter_lowpass_filter(tp10_beta_int, 
                Filter_Highcut, (SAMPLING_RATE), Filter_Order)

            tp9_gamma_filtered = butter_lowpass_filter(tp9_gamma_int, 
            Filter_Highcut, (SAMPLING_RATE), Filter_Order)
            af7_gamma_filtered = butter_lowpass_filter(af7_gamma_int, 
                Filter_Highcut, (SAMPLING_RATE), Filter_Order)
            af8_gamma_filtered = butter_lowpass_filter(af8_gamma_int, 
                Filter_Highcut, (SAMPLING_RATE), Filter_Order)
            tp10_gamma_filtered = butter_lowpass_filter(tp10_gamma_int, 
                Filter_Highcut, (SAMPLING_RATE), Filter_Order)




    # Generated filtered data plots

    if args.integrate:
    
        point_sz = 1
        
        plot_data_combined(tp9_delta_int, af7_delta_int, af8_delta_int, tp10_delta_int, 
                    Filter_Lowcut, Filter_Highcut, SAMPLING_RATE, point_sz, "Delta", data_fname, 
            './plots/20-ABCS_delta_int_' + date_time_now + '.jpg', date_time_now, analysis_parms)

        plot_data_combined(tp9_theta_int, af7_theta_int, af8_theta_int, tp10_theta_int, 
                    Filter_Lowcut, Filter_Highcut, SAMPLING_RATE, point_sz, "Theta", data_fname, 
            './plots/21-ABCS_theta_int_' + date_time_now + '.jpg', date_time_now, analysis_parms)

        plot_data_combined(tp9_alpha_int, af7_alpha_int, af8_alpha_int, tp10_alpha_int, 
                    Filter_Lowcut, Filter_Highcut, SAMPLING_RATE, point_sz, "Alpha", data_fname, 
            './plots/22-ABCS_alpha_int_' + date_time_now + '.jpg', date_time_now, analysis_parms)

        plot_data_combined(tp9_beta_int, af7_beta_int, af8_beta_int, tp10_beta_int, 
                    Filter_Lowcut, Filter_Highcut, SAMPLING_RATE, point_sz, "Beta", data_fname, 
            './plots/23-ABCS_beta_int_' + date_time_now + '.jpg', date_time_now, analysis_parms)

        plot_data_combined(tp9_gamma_int, af7_gamma_int, af8_gamma_int, tp10_gamma_int, 
                    Filter_Lowcut, Filter_Highcut, SAMPLING_RATE, point_sz, "Gamma", data_fname, 
            './plots/24-ABCS_gamma_int_' + date_time_now + '.jpg', date_time_now, analysis_parms)



    if args.filter_data:
        point_sz = 1

# TODO Save


        plot_sensors_power_band(tp9_delta_filtered, af7_delta_filtered, af8_delta_filtered, tp10_delta_filtered, 
                    Filter_Lowcut, Filter_Highcut, SAMPLING_RATE,point_sz,'Delta Filtered', data_fname, 
            './plots/25-ABCS_delta_flitered_' + date_time_now + '.jpg', date_time_now, analysis_parms)

        plot_sensors_power_band(tp9_theta_filtered, af7_theta_filtered, af8_theta_filtered, tp10_theta_filtered, 
                    Filter_Lowcut, Filter_Highcut, SAMPLING_RATE,point_sz,'Theta Filtered', data_fname, 
            './plots/26-ABCS_theta_flitered_' + date_time_now + '.jpg', date_time_now, analysis_parms)

        plot_sensors_power_band(tp9_alpha_filtered, af7_alpha_filtered, af8_alpha_filtered, tp10_alpha_filtered, 
                    Filter_Lowcut, Filter_Highcut, SAMPLING_RATE,point_sz,'Alpha Filtered', data_fname, 
           './plots/27-ABCS_alpha_flitered_' + date_time_now + '.jpg', date_time_now, analysis_parms)

        plot_sensors_power_band(tp9_beta_filtered, af7_beta_filtered, af8_beta_filtered, tp10_beta_filtered, 
                    Filter_Lowcut, Filter_Highcut, SAMPLING_RATE,point_sz,'Beta Filtered', data_fname, 
           './plots/28-ABCS_beta_filtered_' + date_time_now + '.jpg', date_time_now, analysis_parms)

        plot_sensors_power_band(tp9_gamma_filtered, af7_gamma_filtered, af8_gamma_filtered, tp10_gamma_filtered, 
                    Filter_Lowcut, Filter_Highcut, SAMPLING_RATE,point_sz,'Gamma Filtered', data_fname, 
            './plots/29-ABCS_gamma_filtered_' + date_time_now + '.jpg', date_time_now, analysis_parms)


#         plot_sensors_power_band(tp9_delta_filtered, af7_delta_filtered, af8_delta_filtered, tp10_delta_filtered, 
#                     Filter_Lowcut, Filter_Highcut, SAMPLING_RATE,point_sz,'Delta Filtered', data_fname, 
#             './plots/25-ABCS_delta_flitered_' + date_time_now + '.jpg', date_time_now, analysis_parms)
# 
#         plot_sensors_power_band(tp9_theta_filtered, af7_theta_filtered, af8_theta_filtered, tp10_theta_filtered, 
#                     Filter_Lowcut, Filter_Highcut, SAMPLING_RATE,point_sz,'Theta Filtered', data_fname, 
#             './plots/26-ABCS_theta_flitered_' + date_time_now + '.jpg', date_time_now, analysis_parms)
# 
#         plot_sensors_power_band(tp9_alpha_filtered, af7_alpha_filtered, af8_alpha_filtered, tp10_alpha_filtered, 
#                     Filter_Lowcut, Filter_Highcut, SAMPLING_RATE,point_sz,'Alpha Filtered', data_fname, 
#            './plots/27-ABCS_alpha_flitered_' + date_time_now + '.jpg', date_time_now, analysis_parms)
# 
#         plot_sensors_power_band(tp9_beta_filtered, af7_beta_filtered, af8_beta_filtered, tp10_beta_filtered, 
#                     Filter_Lowcut, Filter_Highcut, SAMPLING_RATE,point_sz,'Beta Filtered', data_fname, 
#            './plots/28-ABCS_beta_filtered_' + date_time_now + '.jpg', date_time_now, analysis_parms)
# 
#         plot_sensors_power_band(tp9_gamma_filtered, af7_gamma_filtered, af8_gamma_filtered, tp10_gamma_filtered, 
#                     Filter_Lowcut, Filter_Highcut, SAMPLING_RATE,point_sz,'Gamma Filtered', data_fname, 
#             './plots/29-ABCS_gamma_filtered_' + date_time_now + '.jpg', date_time_now, analysis_parms)
# 



        all_delta = (tp9_delta_filtered + af7_delta_filtered + af8_delta_filtered + tp10_delta_filtered) / 4.0
        all_theta = (tp9_theta_filtered + af7_theta_filtered + af8_theta_filtered + tp10_theta_filtered) / 4.0
        all_alpha = (tp9_alpha_filtered + af7_alpha_filtered + af8_alpha_filtered + tp10_alpha_filtered) / 4.0
        all_beta = (tp9_beta_filtered + af7_beta_filtered + af8_beta_filtered + tp10_beta_filtered) / 4.0
        all_gamma = (tp9_gamma_filtered + af7_gamma_filtered + af8_gamma_filtered + tp10_gamma_filtered) / 4.0



# TODO Save
        plot_all_power_bands(all_delta, all_theta, all_alpha, all_beta, all_gamma,
                    Filter_Lowcut, Filter_Highcut, SAMPLING_RATE, point_sz,'Power Bands (Filtered)', data_fname,
                    './plots/51-ABCS_power_flitered_' + date_time_now + '.jpg', date_time_now, analysis_parms)



        all_delta_int = (tp9_delta_int + af7_delta_int + af8_delta_int + tp10_delta_int) / 4.0
        all_theta_int = (tp9_theta_int + af7_theta_int + af8_theta_int + tp10_theta_int) / 4.0
        all_alpha_int = (tp9_alpha_int + af7_alpha_int + af8_alpha_int + tp10_alpha_int) / 4.0
        all_beta_int = (tp9_beta_int + af7_beta_int + af8_beta_int + tp10_beta_int) / 4.0
        all_gamma_int = (tp9_gamma_int + af7_gamma_int + af8_gamma_int + tp10_gamma_int) / 4.0

        if args.integrate:
            plot_title = 'Power Bands (Integrated)'
        else:
            plot_title = 'Power Bands (Raw)'


# TODO Save
        plot_all_power_bands(all_delta_int, all_theta_int, all_alpha_int, all_beta_int, all_gamma_int,
                    Filter_Lowcut, Filter_Highcut, SAMPLING_RATE, point_sz, plot_title, data_fname, 
                    './plots/52-ABCS_power_int_' + date_time_now + '.jpg', date_time_now, analysis_parms)



        all_delta_filtered = (tp9_delta_filtered + af7_delta_filtered + af8_delta_filtered + tp10_delta_filtered) / 4.0
        all_theta_filtered = (tp9_theta_filtered + af7_theta_filtered + af8_theta_filtered + tp10_theta_filtered) / 4.0
        all_alpha_filtered = (tp9_alpha_filtered + af7_alpha_filtered + af8_alpha_filtered + tp10_alpha_filtered) / 4.0
        all_beta_filtered = (tp9_beta_filtered + af7_beta_filtered + af8_beta_filtered + tp10_beta_filtered) / 4.0
        all_gamma_filtered = (tp9_gamma_filtered + af7_gamma_filtered + af8_gamma_filtered + tp10_gamma_filtered) / 4.0



# TODO Save
        plot_combined_power_bands(all_delta, all_theta, all_alpha, all_beta, all_gamma,
                    all_delta_filtered, all_theta_filtered, all_alpha_filtered, all_beta_filtered, all_gamma_filtered,
                    Filter_Lowcut, Filter_Highcut, SAMPLING_RATE, point_sz,'Power Bands (Filtered)', data_fname,
                    './plots/55-ABCS_power_bands_' + date_time_now + '.jpg', date_time_now, analysis_parms)




# np.mean( np.array([ old_set, new_set ]), axis=0 )


#         delta_avg = np.average([tp9_delta_filtered, af7_delta_filtered, af8_delta_filtered, tp10_delta_filtered])
#         theta_avg = np.average([tp9_theta_filtered, af7_theta_filtered, af8_theta_filtered, tp10_theta_filtered])
#         alpha_avg = np.average([tp9_alpha_filtered, af7_alpha_filtered, af8_alpha_filtered, tp10_alpha_filtered])
#         beta_avg = np.average([tp9_beta_filtered, af7_beta_filtered, af8_beta_filtered, tp10_beta_filtered])
#         gamma_avg = np.average([tp9_gamma_filtered, af7_gamma_filtered, af8_gamma_filtered, tp10_gamma_filtered])

        delta_avg = np.mean([tp9_delta_filtered, af7_delta_filtered, 
            af8_delta_filtered, tp10_delta_filtered], axis=0 )
        theta_avg = np.mean([tp9_theta_filtered, af7_theta_filtered, 
            af8_theta_filtered, tp10_theta_filtered], axis=0 )
        alpha_avg = np.mean([tp9_alpha_filtered, af7_alpha_filtered, 
            af8_alpha_filtered, tp10_alpha_filtered], axis=0 )
        beta_avg = np.mean([tp9_beta_filtered, af7_beta_filtered, 
            af8_beta_filtered, tp10_beta_filtered], axis=0 )
        gamma_avg = np.mean([tp9_gamma_filtered, af7_gamma_filtered, 
            af8_gamma_filtered, tp10_gamma_filtered], axis=0 )


        delta_avg = np.nan_to_num(delta_avg)
        theta_avg = np.nan_to_num(theta_avg)
        alpha_avg = np.nan_to_num(alpha_avg)
        beta_avg = np.nan_to_num(beta_avg)
        gamma_avg = np.nan_to_num(gamma_avg)



#         delta_avg = (tp9_delta_filtered + af7_delta_filtered + af8_delta_filtered + tp10_delta_filtered) / 4.0

#         print("Averages of power band data")
#         print(delta_avg, theta_avg, alpha_avg, beta_avg, gamma_avg)
#         print(delta_avg)

        
#         plot_data_avg_power(delta_avg, theta_avg, alpha_avg, beta_avg, gamma_avg, 
#             Filter_Lowcut, Filter_Highcut, SAMPLING_RATE, 2, "Averages", data_fname, 
#             plot_fname = './plots/30-ABCS_power_' + date_time_now + '.jpg')




    acc_gyro_df = pd.DataFrame(muse_EEG_data, 
        columns=['Accelerometer_X', 'Accelerometer_Y', 'Accelerometer_Z',
                  'Gyro_X', 'Gyro_Y', 'Gyro_Z'])    

    plot_accel_gryo_data(acc_gyro_df, "Accelerometer/Gyro", data_fname, 
                    './plots/60-ABCS_accel_gyro_' + date_time_now + '.jpg', date_time_now, analysis_parms)



    if args.plot_3D:

        power_d = {'PWR_DELTA': all_delta, 'PWR_THETA': all_theta, 
                    'PWR_ALPHA': all_alpha, 'PWR_BETA': all_beta, 'PWR_GAMMA': all_gamma}

#         filt_df = DataFrame([data, index, columns, dtype, copy])
        power_df = pd.DataFrame(power_d, dtype=np.float64)


        pause_and_prompt(0.1, "Plotting 3D Power")

        plot_power_3D(muse_EEG_data, power_df, data_fname,
            './plots/77-ABCS_Power_3D_' + date_time_now + '.jpg', date_time_now, analysis_parms)

        
        
        
        
        


def main(fname, date_time_now):

    global data_file

    muse_EEG_data = read_eeg_data(fname, date_time_now)
    generate_plots(muse_EEG_data, fname, date_time_now)





if __name__ == '__main__':

    date_time_now = strftime('%Y-%m-%d-%H.%M.%S', gmtime())

    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--csv_file", help="CSV file to read)")
    parser.add_argument("-v", "--verbose", help="Increase output verbosity", type=int)
    parser.add_argument("-p", "--power", help="Plot Power Bands", action="store_true")
    parser.add_argument("-e", "--eeg", help="Plot EEG Data", action="store_true")
    parser.add_argument("-d", "--display_plots", help="Display Plots", action="store_true")
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

    if args.logging_level:
        print("logging_level:")
        print(args.logging_level)
        
    if args.power:
        print("power:")
        print(args.power)
        
    if args.display_plots:
        print("display_plots:")
        print(args.display_plots)
        
    if args.plot_3D:
        print("plot_3D:")
        print(args.plot_3D)
        
    if args.filter_data:
        print("filter_data:")
        print(args.filter_data)
        
    if args.eeg:
        print("eeg:")
        print(args.eeg)
       
    if args.power_spectrum:
        print("power_spectrum:")
        print(args.power_spectrum)
                      
    if args.integrate:
        print("integrate:")
        print(args.integrate)
                      
    if args.step_size:
        print("step_size:")
        print(args.step_size)                     
        Integrate_Step_Size = args.step_size
                      
    if args.filter_data:
        print("filter_data:")
        print(args.filter_data)
                      
    if args.lowcut:
        print("lowcut:")
        print(args.lowcut)
        Filter_Lowcut = args.lowcut
                      
    if args.highcut:
        print("highcut:")
        print(args.highcut)
        Filter_Highcut = args.highcut
                      
    if args.filter_order:
        print("filter_order:")
        print(args.filter_order)
        Filter_Order = args.filter_order
           
           
    if args.csv_file:
        fname = args.csv_file
        print("Processing file: ", fname)
        
    else:
        print("Filename not specified")
        sys.exit(1)


    ensure_dir("./logs/")

    log_filename = './logs/analyze-meditation-data-' + date_time_now +'.log'
                            
    if args.logging_level == 1:
        # logging.basicConfig()
        # DEBUG INFO  WARNING  ERROR  CRITICAL 
        logging.basicConfig(filename=log_filename, 
                            format='%(asctime)s - %(message)s', 
                            level=logging.INFO)

        mpl_logger = logging.getLogger('matplotlib')
        mpl_logger.setLevel(logging.INFO) 

    if args.logging_level == 2:
        # logging.basicConfig()
        # DEBUG INFO  WARNING  ERROR  CRITICAL 
        logging.basicConfig(filename=log_filename, 
                            format='%(asctime)s - %(message)s', 
                            level=logging.DEBUG)

        mpl_logger = logging.getLogger('matplotlib')
        mpl_logger.setLevel(logging.DEBUG) 


    main(fname, date_time_now)


    sys.exit(0)



# 2019-11-11 21:16:27,491 - plot_coherence() called
# 2019-11-11 21:16:37,634 - plot_time_series_data() called
# 2019-11-11 21:17:09,711 - plot_data_combined() called
# 2019-11-11 21:17:53,105 - plot_power_3D() called
# 2019-11-11 21:17:54,527 - plot_accel_gryo_data() called
# 
