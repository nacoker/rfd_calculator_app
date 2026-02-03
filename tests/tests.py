# -*- coding: utf-8 -*-
"""
Created on Tue Nov 25 07:25:03 2025

@author: nickwork
"""

from pages.preprocessing import calibrate_force,select_force_column, filter_data, offset_correct_force, determine_onset_index, rfdcalc

from sklearn.linear_model import LinearRegression

import pandas as pd
import numpy as np

rng = np.random.default_rng(42) # Set seed


def test_calibrate_force() -> None:
    calFile_path = 'Load Cell Calibration.csv'
    testFile_path = 'MVIC TEST.txt'
    calFile = pd.read_csv(calFile_path,
                          sep = ',',
                          names = ['Voltage','Force'],
                          header = 0)
    testFile = pd.read_csv(testFile_path,
                            sep = '\t',
                            names = ['Time','Force'],
                            header = 0)
    calibration = LinearRegression(fit_intercept=True)
    calibration.fit(calFile['Voltage'].to_numpy().reshape(-1,1),
                    calFile['Force'].to_numpy().reshape(-1,1))
    calibration_coef = float(calibration.coef_.squeeze())
    calibration_intercept = float(calibration.intercept_.squeeze())
    calibrated_force = (testFile['Force'].mul(calibration_coef) + calibration_intercept)
    expected = calibrated_force.to_numpy()
    actual = calibrate_force(calFile_path,testFile_path)['calibrated_force'].to_numpy()
    assert np.allclose(expected,actual,rtol=1e-05,atol=1e-08)

#%%% Unit Tests for select_force_column function    
def test_select_force_column_uncorrected() -> None:
    candidates = ['filtered_force','calibrated_force','Force']
    forceFile_path = 'MVIC TEST.txt'
    forceFile = pd.read_csv(forceFile_path,
                            sep = '\t',
                            names = ['Time','Force'],
                            header = 0)
    force_column = select_force_column(forceFile, candidates)
    assert force_column == 'Force'
    
def test_select_force_column_calibrated() -> None:
    candidates = ['filtered_force','calibrated_force','Force']
    calFile_path = 'Load Cell Calibration.csv'
    forceFile_path = 'MVIC TEST.txt'
    forceFile = calibrate_force(calFile_path,forceFile_path) 
    force_column = select_force_column(forceFile, candidates)
    assert force_column == 'calibrated_force'
    
def test_select_force_column_filtered() -> None:
    candidates = ['filtered_force','calibrated_force','Force']
    calFile_path = 'Load Cell Calibration.csv'
    forceFile_path = 'MVIC TEST.txt'
    forceFile = calibrate_force(calFile_path,forceFile_path) 
    forceFile['filtered_force'] = filter_data(forceFile)
    force_column = select_force_column(forceFile, candidates)
    assert force_column == 'filtered_force'
    
#%%% Unit Tests for offset_correct_force function

def test_offset_correct_force_uncorrected() -> None:
    inputs_dict = {'time_column':'Time',
                   'force_column':'Force',
                   'start_time':5.0}
    def create_simulated_mvic(fs, baseline_time, ramp_time,plateau_time,noise_std,max_force):
        n_base = int(fs * baseline_time)
        n_ramp = int(fs * ramp_time)
        n_plateau = int(fs * plateau_time)
        total_samples = 2*n_base + 2*n_ramp + (n_plateau + 1)
        
        baseline1 = rng.normal(0, noise_std, n_base)
        baseline2 = rng.normal(0, noise_std, n_base)
        def create_smooth_ramp(n, start, end):
            x = np.linspace(0, np.pi, n)
            return start + (end - start) * (1 - np.cos(x)) / 2
        
        ramp_up = create_smooth_ramp(n_ramp,0, max_force)
        ramp_down = create_smooth_ramp(n_ramp,max_force,0)
        plateau = np.ones(n_plateau + 1) * max_force
        
        force = np.concatenate([baseline1,ramp_up,plateau,ramp_down,baseline2])
        t = np.arange(len(force)) / fs
        return pd.DataFrame({'Time':t,'Force':force})
    df = create_simulated_mvic(fs = 50,baseline_time = 5,ramp_time = 0.25,
                               plateau_time = 4.5,noise_std = 0.05,
                               max_force = 250)
    df, inputs_dict, offsetValue = offset_correct_force(df, inputs_dict, offset_time = 1.0)
    assert np.isclose(offsetValue,-0.006410022309157723, rtol = 1e-08,atol=1e-12)
    
#%%% Unit tests for determine_onset_index function
def test_determine_onset_index_threeSD() -> None: 
    inputs_dict = {'time_column' : 'Time',
                   'force_column' : 'Force',
                   'start_time' : 5.0,
                   'onset_method' : 'Onset will be +3SD of the baseline signal'}
    def create_simulated_mvic(fs, baseline_time, ramp_time,plateau_time,noise_std,max_force):
        n_base = int(fs * baseline_time)
        n_ramp = int(fs * ramp_time)
        n_plateau = int(fs * plateau_time)
        total_samples = 2*n_base + 2*n_ramp + (n_plateau + 1)
        
        baseline1 = rng.normal(0, noise_std, n_base)
        baseline2 = rng.normal(0, noise_std, n_base)
        def create_smooth_ramp(n, start, end):
            x = np.linspace(0, np.pi, n)
            return start + (end - start) * (1 - np.cos(x)) / 2
        
        ramp_up = create_smooth_ramp(n_ramp,0, max_force)
        ramp_down = create_smooth_ramp(n_ramp,max_force,0)
        plateau = np.ones(n_plateau + 1) * max_force
        
        force = np.concatenate([baseline1,ramp_up,plateau,ramp_down,baseline2])
        t = np.arange(len(force)) / fs
        return pd.DataFrame({'Time':t,'Force':force})
    df = create_simulated_mvic(fs = 50,baseline_time = 5,ramp_time = 0.25,
                               plateau_time = 4.5,noise_std = 0.05,
                               max_force = 250)
    onsetIndex = determine_onset_index(df,inputs_dict)
    assert onsetIndex == 251
    
def test_determine_onset_index_manual() -> None:
    inputs_dict = {'time_column':'Time',
                   'force_column':'Force',
                   'start_time':5.0,
                   'onset_method' : 'Manual onset determination'}
    def create_simulated_mvic(fs, baseline_time, ramp_time,plateau_time,noise_std,max_force):
        n_base = int(fs * baseline_time)
        n_ramp = int(fs * ramp_time)
        n_plateau = int(fs * plateau_time)
        total_samples = 2*n_base + 2*n_ramp + (n_plateau + 1)
        
        baseline1 = rng.normal(0, noise_std, n_base)
        baseline2 = rng.normal(0, noise_std, n_base)
        def create_smooth_ramp(n, start, end):
            x = np.linspace(0, np.pi, n)
            return start + (end - start) * (1 - np.cos(x)) / 2
        
        ramp_up = create_smooth_ramp(n_ramp,0, max_force)
        ramp_down = create_smooth_ramp(n_ramp,max_force,0)
        plateau = np.ones(n_plateau + 1) * max_force
        
        force = np.concatenate([baseline1,ramp_up,plateau,ramp_down,baseline2])
        t = np.arange(len(force)) / fs
        return pd.DataFrame({'Time':t,'Force':force})
    df = create_simulated_mvic(fs = 1000,baseline_time = 5,ramp_time = 0.25,
                               plateau_time = 4.5,noise_std = 0.05,
                               max_force = 250)
    onsetIndex = determine_onset_index(df,inputs_dict, manual_onset_time = 5.003)
    assert onsetIndex == 5003
    
#%%% Unit tests for rfdcalc function
def test_rfdcalc() -> None:
    inputs_dict = {'time_column' : 'Time',
                   'force_column' : 'Force',
                   'start_time' : 5.0,
                   'onset_method' : 'Manual onset determination'}
    def create_simulated_mvic(fs, baseline_time, ramp_time,plateau_time,noise_std,max_force):
        n_base = int(fs * baseline_time)
        n_ramp = int(fs * ramp_time)
        n_plateau = int(fs * plateau_time)
        total_samples = 2*n_base + 2*n_ramp + (n_plateau + 1)
        
        baseline1 = rng.normal(0, noise_std, n_base)
        baseline2 = rng.normal(0, noise_std, n_base)
        def create_smooth_ramp(n, start, end):
            x = np.linspace(0, np.pi, n)
            return start + (end - start) * (1 - np.cos(x)) / 2
        
        ramp_up = create_smooth_ramp(n_ramp,0, max_force)
        ramp_down = create_smooth_ramp(n_ramp,max_force,0)
        plateau = np.ones(n_plateau + 1) * max_force
        
        force = np.concatenate([baseline1,ramp_up,plateau,ramp_down,baseline2])
        t = np.arange(len(force)) / fs
        return pd.DataFrame({'Time':t,'Force':force})
    df = create_simulated_mvic(fs = 1000,baseline_time = 5,ramp_time = 0.25,
                               plateau_time = 4.5,noise_std = 0.05,
                               max_force = 250) # Create sim MVIC with 1000Hz sample rate and max force of 250N
    onsetIndex = determine_onset_index(df,inputs_dict, manual_onset_time = 5.003)
    output = rfdcalc(df, onsetIndex = onsetIndex, inputs_dict = inputs_dict)
    rfd50 = output['rfd50'].iloc[0]
    rfd100 = output['rfd100'].iloc[0]
    rfd200 = output['rfd200'].iloc[0]
    assert np.isclose(rfd50, 536.62691389, rtol = 5e-02) # Test for 5% precision based on manual calculations for all values
    assert np.isclose(rfd100, 914.17029538, rtol = 5e-02)
    assert np.isclose(rfd200, 1147.21317853, rtol = 5e-02)