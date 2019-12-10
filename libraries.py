''' 
Temp file of all the libraries needed by the application.

By running this test and getting no errors you'll know if there's libraries to install:
> python libraries.py

If you need to install any missing libraries you can, for example,  you can do so by using pip:
> pip3 install scipy


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



