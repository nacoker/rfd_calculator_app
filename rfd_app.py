# -*- coding: utf-8 -*-
"""
Created on Fri Jul  1 16:47:19 2022

@author: ncoke
"""
import preprocessing


#Import necessary libraries
import streamlit as st
import plotly.express as px
import pandas as pd
import matplotlib.pyplot as plt
from PIL import Image
from sklearn.linear_model import LinearRegression

from streamlit_extras.metric_cards import style_metric_cards
import io

#Create containers for all dropdown menus
header = st.container()
calibration = st.container()
force = st.container()
dataset = st.container()
plot = st.container()
inputs = st.container()
rfd = st.container()

#Create header container and fill with main header text
with header:
    st.header('Welcome to **RFD Analyzer**!')
    st.text("This app will take a csv or txt file consisting of an isometric force-time series \nand calculate the rate of force development for you. To get started, upload your \n.csv or .txt file into the dropbox below. NOTE: your data should look like the image \non the left. If it doesn't, reformat the file so it matches the example.")
 
#Create calibration container and provide uploader for calibration file if necessaary    
with st.expander('Step 1: Upload Your Calibration File'):
    calibrate = st.radio('Will your force file require calibration?', ['Yes','No'])
    if calibrate == 'Yes':
        calFile_path = st.file_uploader('Upload your calibration file here')


#Create force file upload container
with st.expander('Step 2: Upload Your Force-Time Curve'):
    col1, col2 = st.columns(2)
    with col1:
        image = Image.open('force example.PNG')
        st.image(image)
    with col2:
        forceFile_path = st.file_uploader('Upload your force file here')
        filter_data = st.radio('Would you like to filter your data before calculating RFD?',
                               ['Yes','No'])
        if calibrate == 'Yes':
            try:
                forceData = preprocessing.calibrate_force(calFile_path, forceFile_path)
            except:
                pass
            if filter_data == 'Yes':
                forceData['filtered_force'] = preprocessing.filter_data(forceData)
        else:
            forceData = pd.read_csv(forceFile_path,
                                    sep = '\t',
                                    names = ['Time','Force'],
                                    header = 0)
            if filter_data == 'Yes':
                forceData['filtered_force'] = preprocessing.filter_data(forceData)
        force_column = preprocessing.select_force_column(forceData,candidates = ['filtered_force','calibrated_force','Force'])

#Create dataset container to be used for data inspection        
with st.expander('Step 3: Inspect Your Data'):
    if not forceData:
        st.write('Please upload a force file first.')
    else:
        st.header('Here is your raw force-time curve')
        st.text('If you uploaded the correct file type in step 2, you should see your data on the \nleft and a plot of that data on the right.')
        col1,col2 = st.columns(2)
        with col1:
            st.write(forceData.head())
        with col2:
            fig1, ax1 = plt.subplots()
            ax1.plot(forceData['Time'], forceData[force_column])
            ax1.set(xlabel = 'Time (s)',
                    ylabel = 'Force (N)')
            st.pyplot(fig1)
        recordStartTime = st.number_input('For the contraction of interest, what time did you start recording? For example, if you want to analyze rep 2, which starts at 15 seconds, enter 15.',min_value=0.0,max_value=60.0,step=0.1) # Used to store first time value in recording
        stopTime = st.number_input('What time was that contraction supposed to end? If necessary, include rest at the end of the contraction, e.g. 5 second baseline, 5 second contraction, 5 second rest = 15 seconds',min_value=1.0,max_value=60.0,value=15.0,step=0.1) # Used to store last time value in recording

#Create expander for accepting RFD inputs
with st.expander('Step 4: How Do You Want To Calculate RFD?'):
    st.header('How would you like to calculate RFD?')
    col1, col2 = st.columns(2)
    with col1:
        sampleFreq = st.number_input('Enter the sampling rate of your force measurement device:')
        offset = st.radio('Does your force file require offset correction?',['Yes','No'])
    with col2:
        onset = st.radio('Select your onset determination method:',
                         ['Manual onset determination',
                          'Onset will be +3SD of the baseline signal'])
        rfdVals = st.multiselect('Which RFD values would you like to calculate? Select all that apply.',
                                 ['RFD0-50',
                                  'RFD0-100',
                                  'RFD0-200'],
                                 ['RFD0-50',
                                  'RFD0-100',
                                  'RFD0-200'])
    startTime = st.number_input('For the contraction of interest, what time was the contraction supposed to start? For example, if your contraction includes a five-second resting baseline, enter 5.',
                                min_value = 1.0,
                                max_value = 60.0,
                                step = 0.1)
#Create inputs container to be used to determine outputs
with inputs:
    with st.expander('Step 4: Tell us about how you want to calculate RFD'):
        st.header('How would you like to calculate RFD?')
        col1,col2 = st.columns(2)
        with col1:
            sampleFreq = st.number_input('Enter the sampling rate of your force measurement device:') # Number input to input sampling frequency
            offset = st.radio('Does your file require offset correction?',['Yes','No']) # Selection for whether data needs to be offset corrected
        with col2:
            onset_method = st.radio('Select your onset determination method:',['Manual onset determination', 'Onset will be +3SD of the baseline signal']) # Selection for method of onset determination
            rfdVals = st.multiselect('Which RFD values would you like to calculate? Select all that apply:',['RFD50','RFD100','RFD200'],['RFD50','RFD100','RFD200']) # Selection for RFD outputs to calculate
        startTime = st.number_input('For the contraction of interest, what time was the contraction supposed to start? For example, if you analyzed a contraction that included a five-second resting baseline, enter 5.',min_value=1.0,max_value=60.0,step=0.1) # Input value to be used for onset visualization
        if forceData:
            if offset == 'Yes':
                forceData, inputs_dict,offsetValue = preprocessing.offset_correct_force(forceData,inputs_dict) # Need to create inputs_dict earlier
                offStart = sampleFreq * (startTime - 4)
                offStop = sampleFreq * startTime
                if onset_method == 'Manual onset determination':
                    manualTime = st.slider('How long would you like your manual viewing window to be in milliseconds?',
                                           50,
                                           2000,
                                           value = 300,
                                           step = 50) # Input for determining x-axis of onset plot
                    manualTime = manualTime / 1000 # convert manualTime input to milliseconds
                    fig = px.line(forceData.iloc[offStart:offStop], x = inputs_dict['time_column'], y = inputs_dict['force_column'])
                    st.write(fig)
                    manualOnset = st.number_input('Based on the graph above, what time did your contraction start?',step = 1e-6,format="%.5f")
                    onsetIndex = preprocessing.determine_onset_index(forceData,inputs_dict,manual_onset_time = manualOnset)
                elif onset == 'Onset will be +3SD of the baseline signal':
                    onsetIndex = preprocessing.determine_onset_index(forceData,inputs_dict,onset_sd_scale = 3)
        CalcButton = st.button('Click here to calculate your RFD values') # Button to initiate calculation of RFD
#TODO: Left off here, trying to decide if code needs to be rewritten to do all processing steps after CalcButton pressed so final inputs determined
# If so, move lines ~121-138 below CalcButton
    if CalcButton:
        inputs_dict = {'time_column':'Time',
                       'force_column': force_column,
                       'sampling_rate': sampleFreq,
                       'onset_method': onset,
                       'start_time': startTime,
                       'offset': offset}
        if (inputs_dict['onset_method'] == 'Manual onset determination'):
            onsetIndex = preprocessing.determine_onset_index(forceData,
                                                             inputs_dict = inputs_dict,
                                                             manual_onset_time = manualOnset)
        else:
            onsetIndex = preprocessing.determine_onset_index(forceData,
                                                             inputs_dict = inputs_dict)            
        rfdTable = preprocessing.rfdcalc(data=forceData,onsetIndex = onsetIndex) # Calculate RFD values
        finalRfdTable = rfdTable.loc[0,['rfd50','rfd100','rfd200']] #Store RFD values


#Create RFD container for viewing results
with rfd:
    with st.expander('Step 5: View and download your RFD values'):
        st.header('Here are your RFD values')
        st.text("After clicking the button above, a plot of your time points overlaid on the \nforce-time curve and a table of your RFD values should appear below.")
        if CalcButton:
            fig4,ax4 = plt.subplots() #Create figure for viewing outputs
            if filter_data: #Generate plot of filtered data with onset and timing info for RFD
                ax4.plot(forceData.loc[(forceData['Time']>recordStartTime) & (forceData['Time']<stopTime),'Time'],forceData.loc[(forceData['Time']>recordStartTime) & (forceData['Time']<stopTime),'filtered'])
                ax4.scatter(forceData.loc[rfdTable['fifty_index'],'Time'],forceData.loc[rfdTable['fifty_index'],'filtered'],label='rfd50')
                ax4.scatter(forceData.loc[rfdTable['onehundred_index'],'Time'],forceData.loc[rfdTable['onehundred_index'],'filtered'],label='rfd100')
                ax4.scatter(forceData.loc[rfdTable['twohundred_index'],'Time'],forceData.loc[rfdTable['twohundred_index'],'filtered'],label='rfd200')
                ax4.hlines(xmin=0,xmax=100,y=forceData.loc[onsetIndex,'filtered'],color='r',linestyle='--',label='onset')
                legend = ax4.legend(loc='upper right')
                ax4.set(xlabel = 'Time (s)',
                        ylabel = 'Force (N)',
                        xlim=[recordStartTime,stopTime])
                st.pyplot(fig4)
            elif 'Corrected' in forceData.columns: #Generate plot of corrected data with onset and timing info for RFD
                ax4.plot(forceData.loc[(forceData['Time']>recordStartTime) & (forceData['Time']<stopTime),'Time'],forceData.loc[(forceData['Time']>recordStartTime) & (forceData['Time']<stopTime),'Corrected'])
                ax4.scatter(forceData.loc[rfdTable['fifty_index'],'Time'],forceData.loc[rfdTable['fifty_index'],'Corrected'],label='rfd50')
                ax4.scatter(forceData.loc[rfdTable['onehundred_index'],'Time'],forceData.loc[rfdTable['onehundred_index'],'Corrected'],label='rfd100')
                ax4.scatter(forceData.loc[rfdTable['twohundred_index'],'Time'],forceData.loc[rfdTable['twohundred_index'],'Corrected'],label='rfd200')
                ax4.hlines(xmin=0,xmax=100,y=forceData.loc[onsetIndex,'Corrected'],color='r',linestyle='--',label='onset')
                legend = ax4.legend(loc='upper right')
                ax4.set(xlabel = 'Time (s)',
                        ylabel = 'Force (N)',
                        xlim=[recordStartTime,stopTime])
                st.pyplot(fig4)
            else: #Generate plot of uncorrected force data with onset and timing info for RFD
                ax4.plot(forceData.loc[(forceData['Time']>recordStartTime) & (forceData['Time']<stopTime),'Time'],forceData.loc[(forceData['Time']>recordStartTime) & (forceData['Time']<stopTime),'Force'])
                ax4.scatter(forceData.loc[rfdTable['fifty_index'],'Time'],forceData.loc[rfdTable['fifty_index'],'Force'],label='rfd50')
                ax4.scatter(forceData.loc[rfdTable['onehundred_index'],'Time'],forceData.loc[rfdTable['onehundred_index'],'Force'],label='rfd100')
                ax4.scatter(forceData.loc[rfdTable['twohundred_index'],'Time'],forceData.loc[rfdTable['twohundred_index'],'Force'],label='rfd200')
                ax4.hlines(xmin=0,xmax=100,y=forceData.loc[onsetIndex,'Force'],color='r',linestyle='--',label='onset')
                legend = ax4.legend(loc='upper right')
                ax4.set(xlabel = 'Time (s)',
                        ylabel = 'Force (N)',
                        xlim=[recordStartTime,stopTime])
                st.pyplot(fig4)
            col1,col2,col3 = st.columns(3) # Create 3 columns to store RFD values
            col1.metric(label='RFD50',value=round(finalRfdTable.loc['rfd50'],2)) # Write RFD50 value to stylized card
            col2.metric(label='RFD100',value=round(finalRfdTable.loc['rfd100'],2)) # Write RFD100 value to stylized card
            col3.metric(label='RFD200',value=round(finalRfdTable.loc['rfd200'],2)) #Write RFD200 value to stylized card
            style_metric_cards() #Stylize col metrics
            st.download_button('Click here to download your RFD values',finalRfdTable.to_csv(),mime='text/csv') # Download button to export RFD values as csv table if desired
            img = io.BytesIO() # Store fig4 with RFD timing values to memory
            plt.savefig(img,format='png',dpi=700) # Save fig4 to memory as high-quality PNG image
            fig_out = st.download_button(label='Download this figure',data=img,file_name='figure.png',mime='image/png') # Download button to allow export of figure 