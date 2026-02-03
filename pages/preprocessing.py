# -*- coding: utf-8 -*-
"""
Created on Thu Oct 16 08:11:34 2025

@author: nickwork
"""

import pandas as pd

from scipy.signal import filtfilt,butter
from sklearn.linear_model import LinearRegression



#%%
def calibrate_force(calFile_path, forceFile_path):
    calFile = pd.read_csv(calFile_path,
                          sep = ',',
                          names = ['Voltage','Force'],
                          header = 0)
    forceFile = pd.read_csv(forceFile_path,
                            sep = '\t',
                            names = ['Time','Force'],
                            header = 0)
    calibration = LinearRegression(fit_intercept=True)
    calibration.fit(calFile['Voltage'].to_numpy().reshape(-1,1),
                    calFile['Force'].to_numpy().reshape(-1,1))
    forceFile['calibrated_force'] = (calibration
                                     .predict(forceFile['Force']
                                              .to_numpy()
                                              .reshape(-1,1)))
    return forceFile

#%%
def filter_data(forceData,order=4,low_cut=15,sampleFreq=2222): # Define function for filtering force data with 4th order low-pass Butterworth (cutoff = 15 Hz)
    nyq = sampleFreq * 0.5 # Define Nyquist frequency
    low = low_cut / nyq # Define cutoff frequency relative to Nyquist
    b,a = butter(order,low,'lowpass',analog=False) # Calculate filter coefficients
    if 'corrected_force' in forceData.columns:
        filtered = filtfilt(b,a,forceData['corrected_force'])
    elif 'calibrated_force' in forceData.columns:
        filtered = filtfilt(b,a,forceData['calibrated_force']) #If data was offset-corrected,filter corrected data
    else:
        filtered = filtfilt(b,a,forceData['Force']) # If data wasn't offset corrected, filter uncorrected data
    filtered = pd.Series(filtered, name = 'filtered_force')
    return filtered

#%%
def select_force_column(df,candidates):
    return next((c for c in candidates if c in df.columns), None)

#%%
def offset_correct_force(df,inputs_dict, start_time,offset_time = 4):
    mask = (
        (df[inputs_dict['time_column']] > (start_time - offset_time)) &
        (df[inputs_dict['time_column']] <= start_time)
        )
    offsetValue = df.loc[mask,inputs_dict['force_column']].mean()
    df['corrected_force'] = df[inputs_dict['force_column']] - offsetValue
    inputs_dict['force_column'] = 'corrected_force'
    return df, inputs_dict, offsetValue
#%%
def determine_onset_index(data,
                          inputs_dict,
                          manual_onset_time = None,
                          avg_duration = 4,
                          onset_sd_scale = None):
    if (inputs_dict['onset_method'] == 'Manual onset determination'):
        onsetIndex = data[data[inputs_dict['time_column']].ge(manual_onset_time)].index[0]
    elif (inputs_dict['onset_method'] == 'Onset will be +3SD of the baseline signal'):
        contractionStartIndex = data[data[inputs_dict['time_column']].ge(inputs_dict['start_time'])].index[0]
        baselineStartIndex = data[data[inputs_dict['time_column']].ge(inputs_dict['start_time'] - avg_duration)].index[0]
        baselineMean = data[inputs_dict['force_column']].iloc[baselineStartIndex:contractionStartIndex].mean()
        baselineStd = data[inputs_dict['force_column']].iloc[baselineStartIndex:contractionStartIndex].std()
        onsetIndex = data[data[inputs_dict['force_column']] > (baselineMean + (baselineStd * 3))].index[0]
    return onsetIndex
    
           
#%%
def rfdcalc(data, onsetIndex, inputs_dict, rfd50Time = 0.050, rfd100Time = 0.100, rfd200Time = 0.200): # Define function for calculation of RFD
    rfd50Index = data[data[inputs_dict['time_column']].gt((data.loc[onsetIndex,inputs_dict['time_column']] + rfd50Time))].index[0]
    rfd100Index = data[data[inputs_dict['time_column']].gt((data.loc[onsetIndex,inputs_dict['time_column']] + rfd100Time))].index[0]    
    rfd200Index = data[data[inputs_dict['time_column']].gt((data.loc[onsetIndex,inputs_dict['time_column']] + rfd200Time))].index[0]
    rfd50 = (data.loc[rfd50Index,inputs_dict['force_column']] - data.loc[onsetIndex,inputs_dict['force_column']]) / (data.loc[rfd50Index,inputs_dict['time_column']] - data.loc[onsetIndex, inputs_dict['time_column']])
    rfd100 = (data.loc[rfd100Index,inputs_dict['force_column']] - data.loc[onsetIndex,inputs_dict['force_column']]) / (data.loc[rfd100Index,inputs_dict['time_column']] - data.loc[onsetIndex, inputs_dict['time_column']])
    rfd200 = (data.loc[rfd200Index,inputs_dict['force_column']] - data.loc[onsetIndex,inputs_dict['force_column']]) / (data.loc[rfd200Index,inputs_dict['time_column']] - data.loc[onsetIndex, inputs_dict['time_column']])
    output = pd.DataFrame({'rfd50_index': rfd50Index,
                           'rfd100_index': rfd100Index,
                           'rfd200_index': rfd200Index,
                           'rfd50': rfd50,
                           'rfd100': rfd100,
                           'rfd200': rfd200},
                          index = [0])
    return output    