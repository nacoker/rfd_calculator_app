# -*- coding: utf-8 -*-
"""
Created on Thu Dec 18 07:48:40 2025

@author: nickwork
"""

from preprocessing import calibrate_force

import streamlit as st
import pandas as pd

st.header('Welcome to **RFD Analyzer!**')
st.text("This app will take a csv or txt file consisting of an isometric force-time series \nand calculate the rate of force development for you. To get started, upload your \n.csv or .txt file into the dropbox below. NOTE: your data should look like the image \non the left. If it doesn't, reformat the file so it matches the example.")

st.subheader('Step 1: Calibrate Your Data', divider='gray')
st.text('Does your data require calibration? If so, upload your calibration file and force \nfile to the boxes below. If not, upload your force file and skip to step 2.')

calibrate = st.radio('Does your data require calibration?', ['Yes','No'])
if calibrate == 'Yes':
    calFile_path = st.file_uploader('Upload your calibration file here:',type='csv')
forceFile_path = st.file_uploader('Upload your force file here:',type='csv')

calButton = st.button('Click here to move on to Step 2.')
if calButton:
    if (calibrate == 'Yes') and forceFile_path is not None:
        try:
            forceData = calibrate_force(calFile_path,forceFile_path)
            st.session_state['forceData'] = forceData
            st.switch_page("file_processing.py")
        except (FileNotFoundError, ValueError) as e:
            st.warning('Force data not calibrated. Please upload a calibration file.')
            st.stop()
    elif (calibrate == 'No') and forceFile_path is not None:
        try:
            forceData = pd.read_csv(forceFile_path,
                                    sep = '\t',
                                    names = ['Time','Force'],
                                    header = 0)
            st.session_state['forceData'] = forceData
            st.switch_page('file_processing.py')
        except (FileNotFoundError, ValueError) as e:
            st.warning('Force data not found. Please upload a test file.')
            st.stop()
