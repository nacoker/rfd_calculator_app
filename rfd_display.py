# -*- coding: utf-8 -*-
"""
Created on Tue Jan  6 17:01:17 2026

@author: nickwork
"""

import streamlit as st
import matplotlib.pyplot as plt

if ('forceData' not in st.session_state) | ('inputs_dict' not in st.session_state) | ('rfdTable' not in st.session_state):
    st.stop('Please complete steps 1-4 first.')

forceData = st.session_state['forceData']
inputs_dict = st.session_state['inputs_dict']
rfdTable = st.session_state['rfdTable']

st.subheader('Step 5: View and Download Your RFD Values')

fig,ax = plt.subplots()
ax.plot(forceData[[inputs_dict['time_column']]],
        forceData[[inputs_dict['force_column']]])
ax.scatter(forceData.loc[rfdTable['rfd50_index'],inputs_dict['time_column']],
           forceData.loc[rfdTable['rfd50_index'],inputs_dict['force_column']],
           label='rfd50')
ax.scatter(forceData.loc[rfdTable['rfd100_index'],inputs_dict['time_column']],
           forceData.loc[rfdTable['rfd100_index'],inputs_dict['force_column']],
           label='rfd100')
ax.scatter(forceData.loc[rfdTable['rfd200_index'],inputs_dict['time_column']],
           forceData.loc[rfdTable['rfd200_index'],inputs_dict['force_column']],
           label='rfd200')
ax.hlines(xmin = 0,
          xmax = 15,
          y = forceData.loc[inputs_dict['onset_index'],inputs_dict['force_column']],
          color = 'r',
          linestyle = '--',
          label = 'onset')
legend = ax.legend(loc = 'upper right')
ax.set(xlabel = 'Time (s)',
       ylabel = 'Force (N)')
st.pyplot(fig)

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(label = 'RFD 0 - 50',
              value = rfdTable['rfd50'].round(2))

with col2:
    st.metric(label = 'RFD 0 - 100',
              value = rfdTable['rfd100'].round(2))

with col3:
    st.metric(label = 'RFD 0 - 200',
              value = rfdTable['rfd200'].round(2))