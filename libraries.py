''' 
Temp file of all the libraries needed by the application.

By running geting no errors you'll know if there's libraries to install:
> python libraries.py

If you need to install any missing libraries you can, for example,  do so by running:
> pip3 install scipy


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

