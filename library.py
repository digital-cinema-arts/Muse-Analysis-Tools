
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
import h5py, tables
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

from PyQt5.QtCore import QDateTime, Qt, QTimer, QUrl
from PyQt5.QtWidgets import (QApplication, QCheckBox, QComboBox, QDateTimeEdit,
        QDial, QDialog, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit,
        QProgressBar, QPushButton, QRadioButton, QScrollBar, QSizePolicy,
        QSlider, QSpinBox, QStyleFactory, QTableWidget, QTabWidget, QTextEdit,
        QVBoxLayout, QWidget)
