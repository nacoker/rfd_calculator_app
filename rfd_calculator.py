# -*- coding: utf-8 -*-
"""
Created on Thu Dec 18 08:31:22 2025

@author: nickwork
"""

from preprocessing import determine_onset_index, rfdcalc
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px

if ('forceData' not in st.session_state) | ('inputs_dict' not in st.session_state):
    st.stop('Please complete Steps 1 and 2 first.')

inputs_dict = st.session_state['inputs_dict']
forceData = st.session_state['forceData']

st.subheader('Step 3: Provide the Necessary Inputs',divider='gray')

sampleFreq = st.number_input('Enter the Sampling Rate of Your Device:')
inputs_dict['onset_method'] = st.radio('Select your onset determination method:',
                                       ['Manual onset determination',
                                        'Onset will be +3SD of the baseline signal'])

rfdVals = st.multiselect('Which RFD values would you like to calculate? Select all that apply.',
                         ['RFD0-50',
                          'RFD0-100',
                          'RFD0-200'],
                         ['RFD0-50',
                          'RFD0-100',
                          'RFD0-200'])

st.subheader('Step 4: Determine The Contraction Onset')
if inputs_dict['onset_method'] == 'Manual onset determination':
    manualTime = st.slider('How long would you like your manual viewing window to be in milliseconds?',
                           50,
                           2000,
                           value = 300,
                           step = 50) # Input for determining x-axis of onset plot
    manualTime_ms = manualTime / 1000 # convert manualTime input to seconds
    halfManualTime_ms = manualTime_ms / 2
    window_start = inputs_dict['start_time'] - halfManualTime_ms
    window_end = inputs_dict['start_time'] + halfManualTime_ms
    fig = px.line(forceData.loc[forceData[inputs_dict['time_column']].between(window_start,window_end)],
                  x = inputs_dict['time_column'],
                  y = inputs_dict['force_column'])
    st.write(fig)
    manualOnset = st.number_input('Based on the graph above, what time did your contraction start?',step = 1e-6,format="%.5f")
    onsetIndex = determine_onset_index(forceData,inputs_dict,manual_onset_time = manualOnset)
else:
    onsetIndex = determine_onset_index(forceData,inputs_dict,onset_sd_scale = 3)
    
rfdButton = st.button('Click Here to Calculate Your RFD Values')

if rfdButton:
    inputs_dict.update({'sampleFreq' : sampleFreq,
                        'onset_index' : onsetIndex})
    rfdTable = rfdcalc(forceData, onsetIndex = onsetIndex, inputs_dict = inputs_dict)
    st.session_state['inputs_dict'] = inputs_dict
    st.session_state['forceData'] = forceData
    st.session_state['rfdTable'] = rfdTable
    st.switch_page('rfd_display.py')