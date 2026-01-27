# -*- coding: utf-8 -*-
"""
Created on Thu Dec 18 08:11:44 2025

@author: nickwork
"""

from preprocessing import select_force_column,offset_correct_force, filter_data
import streamlit as st
import matplotlib.pyplot as plt

st.subheader('Step 2: Inspect and Preprocess Your Data', divider='gray')
if 'forceData' not in st.session_state:
    st.stop('Please upload a force file first.')
else:
    forceData = st.session_state['forceData']
    force_column = select_force_column(forceData,candidates = ['calibrated_force','Force'])
    inputs_dict = {'time_column' : 'Time',
                   'force_column' : force_column}

st.subheader('Your Force-Time Curve', divider='gray')
fig, ax = plt.subplots()
ax.plot(forceData['Time'], forceData[force_column])
ax.set(xlabel = 'Time (s)',
        ylabel = 'Force (N)')
st.pyplot(fig)

st.subheader('Preprocess Your Force-Time Curve', divider='gray')
startTime = st.number_input('For the contraction of interest, what time was the contraction supposed to start? For example, if your contraction includes a five-second resting baseline, enter 5.',
                            min_value = 1.0,
                            max_value = 60.0,
                            step = 0.1)
offset = st.radio('Does your file require offset correction?',['Yes','No'])
filterData = st.radio('Would you like to filter your data before calculating RFD?',['Yes','No'])

processButton = st.button('Click here to preprocess your data.')

if processButton:
    inputs_dict.update({'start_time' : startTime,
                        'offset' : offset,
                        'filter_data' : filterData})
    match (offset,filterData):
        case ('Yes','Yes'):
            forceData, inputs_dict, offsetValue = offset_correct_force(forceData, inputs_dict, startTime)
            forceData['filtered'] = filter_data(forceData)
            inputs_dict['force_column'] = 'filtered'
        case ('Yes', 'No'):
            forceData, inputs_dict, offsetValue = offset_correct_force(forceData, inputs_dict, startTime)
        case ('No','Yes'):
            forceData['filtered'] = filter_data(forceData)
            inputs_dict['force_column'] = 'filtered'            
        case ('No','No'):
            pass
    st.session_state['inputs_dict'] = inputs_dict
    st.session_state['forceData'] = forceData
    st.switch_page('rfd_calculator.py')