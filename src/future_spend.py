import pandas as pd
import numpy as np
import math
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, InputLayer
from settings import __SETTINGS__

global_settings = __SETTINGS__

class FutureSpend:
    def __init__(self):
        pass