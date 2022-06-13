# -*- coding: utf-8 -*-
"""
Created on Mon Jun  6 13:57:22 2022

@author: ncoker
"""

import streamlit as st
import plotly.express as px
import pandas as pd
import matplotlib.pyplot as plt
from PIL import Image
from sklearn.linear_model import LinearRegression

header = st.container()
calibration = st.container()
force = st.container()
dataset = st.container()
plot = st.container()
inputs = st.container()
rfd = st.container()


with header:
    st.header('Welcome to **RFD Analyzer**!')
    st.text("This app will take a csv or txt file consisting of an isometric force-time series \nand calculate the rate of force development for you. To get started, upload your \n.csv or .txt file into the dropbox below. NOTE: your data should look like the image \non the left. If it doesn't, reformat the file so it matches the example.")
 
with calibration:
    with st.expander('Step 1: Upload your calibration file'):
        convert = st.radio('Does your file require conversion?',['Yes','No'])
        st.text('If you are uploading a file that \nexpresses force in raw voltage, \nclick below to upload a calibration \nfile.')
        if convert == 'Yes':
            cal = st.file_uploader('Upload your calibration file here')
            calFile = pd.read_csv(cal,sep=',',names=['Voltage','Force'],header=0)
            st.write(calFile.head())
            calibration = LinearRegression()
            calibration.fit(calFile['Voltage'].to_numpy().reshape(-1,1),calFile['Force'].to_numpy().reshape(-1,1))      
    
with force:
    with st.expander('Step 2: Upload your force-time curve'):
        col1, col2 = st.columns(2)
        with col1:
            image = Image.open('force example.PNG')
            st.image(image)
            with col2:
                file = st.file_uploader('Upload your file here')
                if file:
                    file2 = pd.read_csv(file,sep='\t',names=['Time','Force'],header=0)

with dataset:
    with st.expander('Step 3: Inspect your data'):
        st.header('Here is your raw dataset')
        st.text('If you have uploaded the correct file type into the dropbox on the left, \nyou should see a table of your data as well as your force trace below.')
        col1,col2 = st.columns(2)
        with col1:
            if file:
                forceData = pd.DataFrame(file2)             
                if (convert == 'Yes'):
                    forceData['Corrected'] = calibration.predict(forceData['Force'].to_numpy().reshape(-1,1))
                    st.write(forceData.head())
                else: 
                    st.write(forceData.head())
        with col2: 
            if file:
                fig1,ax1 = plt.subplots()
                if 'Corrected' in forceData.columns:
                    ax1.plot(forceData['Time'],forceData['Corrected'])
                    ax1.set(xlabel = 'Time (s)',
                            ylabel = 'Force (N)')
                    st.pyplot(fig1)
                else:
                    ax1.plot(forceData['Time'],forceData['Force'])
                    ax1.set(xlabel = 'Time (s)',
                            ylabel = 'Force (N)')
                    st.pyplot(fig1)
        recordStartTime = st.number_input('For the contraction of interest, what time did you start recording? For example, if you want to analyze rep 2, which starts at 15 seconds, enter 15.',min_value=0.0,max_value=60.0,step=0.1)
        stopTime = st.number_input('What time was that contraction supposed to end? If necessary, include rest at the end of the contraction, e.g. 5 second baseline, 5 second contraction, 5 second rest = 15 seconds',min_value=1.0,max_value=60.0,step=0.1)

with inputs:
    with st.expander('Step 4: Tell us about how you want to calculate RFD'):
        st.header('How would you like to calculate RFD?')
        col1,col2 = st.columns(2)
        with col1:
            sampleFreq = st.number_input('Enter the sampling rate of your force measurement device:')
            offset = st.radio('Does your file require offset correction?',['Yes','No'])
        with col2:
            onset = st.radio('Select your onset determination method:',['Manual onset determination', 'Onset will be +3SD of the baseline signal'])
            rfdVals = st.multiselect('Which RFD values would you like to calculate? Select all that apply:',['RFD50','RFD100','RFD200'],['RFD50','RFD100','RFD200'])
        startTime = st.number_input('For the contraction of interest, what time was the contraction supposed to start? For example, if you analyzed a contraction that included a five-second resting baseline, enter 5.',min_value=1.0,max_value=60.0,step=0.1)
        if (onset == 'Manual onset determination') & (offset == 'Yes'):
            if file:
                manualTime = st.slider('How long would you like your manual viewing window to be in milliseconds?',50,2000,value=300,step=50)
                manualTime = manualTime / 1000
                startTimeIndex = forceData[forceData['Time'].gt(startTime)].index[0]
                lowViewTime = forceData.loc[startTimeIndex,'Time'] - (manualTime/2)
                lowViewIndex = forceData[forceData['Time'].gt(lowViewTime)].index[0]
                highViewTime = forceData.loc[startTimeIndex,'Time'] + (manualTime/2)
                highViewIndex = forceData[forceData['Time'].gt(highViewTime)].index[0]
                offStart = sampleFreq
                offStop = sampleFreq * 5 #Sloppy code used for proof of concept, adapt to make it more flexible
                if 'Corrected' in forceData.columns:
                    offsetValue = forceData.loc[offStart:offStop,'Corrected'].mean()
                    forceData['Corrected'] = forceData['Corrected'] - offsetValue
                    Manual = forceData[(forceData['Time'] > lowViewTime) & (forceData['Time'] < highViewTime)] 
                    fig = px.line(Manual,x='Time',y='Corrected')
                    st.write(fig)
                    manualOnset = st.number_input('Based on the graph above, what time did your contraction start?')
                else:
                    offsetValue = forceData.loc[offStart:offStop,'Force'].mean()
                    forceData['Force'] = forceData['Force'] - offsetValue
                    Manual = forceData[(forceData['Time'] > lowViewTime) & (forceData['Time'] < highViewTime)] 
                    fig = px.line(Manual,x='Time',y='Force')
                    st.write(fig)
                    manualOnset = st.number_input('Based on the graph above, what time did your contraction start?')
        elif (onset == 'Onset will be +3SD of the baseline signal') & (offset == 'Yes'):
            if file:
                offStart = sampleFreq
                offStop = sampleFreq * 5 #Sloppy code used for proof of concept, adapt to make it more flexible
                if 'Corrected' in forceData.columns:
                    offsetValue = forceData.loc[offStart:offStop,'Corrected'].mean()
                    forceData['Corrected'] = forceData['Corrected'] - offsetValue
                else:
                    offsetValue = forceData.loc[offStart:offStop,'Force'].mean()
                    forceData['Force'] = forceData['Force'] - offsetValue
                fig3, ax3 = plt.subplots()
                if 'Corrected' in forceData.columns:
                    ax3.plot(forceData.loc[(forceData['Time']>recordStartTime) & (forceData['Time']<stopTime),'Time'],forceData.loc[(forceData['Time']>recordStartTime) & (forceData['Time']<stopTime),'Corrected'])
                    ax3.set(xlabel='Time (s)',
                            ylabel='Force')
                    st.pyplot(fig3)
                else:
                    ax3.plot(forceData['Time'],forceData['Force'])
                    ax3.set(xlabel='Time (s)',
                            ylabel='Force')
                    st.pyplot(fig3)
        CalcButton = st.button('Click here to calculate your RFD values')
        
    if CalcButton:
        def baseline(data, time = 'Time', torque = 'Force', start = startTime, avg_duration = 4): # will probably want to update start and avg_duration to make them more flexible
            if 'Corrected' in data.columns:    
                if (onset == 'Manual onset determination'):
                    start = manualOnset
                    torque = 'Corrected'
                    onsetIndex = data[data[time].gt(start)].index[0]
                    startTime = data.iloc[onsetIndex,0]
                    contractionStart = data[data.index >= onsetIndex]
                    startTorque = data.loc[onsetIndex,torque]
                    baselineInfo = pd.DataFrame({#'startIndex':startIndex,
                                                 'startTime':startTime,
                                                 #'baselineAvg':baselineAvg,
                                                 #'baselineSD':baselineSD,
                                                 #'threeSD':threeSD,
                                                 'onsetIndex':onsetIndex,
                                                 'startTorque':startTorque},
                                                index=[0])
                elif onset == 'Onset will be +3SD of the baseline signal':
                    torque = 'Corrected'
                    startIndex = data[data[time].gt(start)].index[0]
                    baselineStart = start - avg_duration
                    baselineStartIndex = data[data[time].gt(baselineStart)].index[0]
                    startTime = data.iloc[startIndex,0]
                    baselineAvg = data[torque].iloc[baselineStartIndex:startIndex].mean()
                    baselineSD = data[torque].iloc[baselineStartIndex:startIndex].std()
                    threeSD = baselineSD * 3
                    contractionStart = data[data.index >= startIndex]
                    onsetIndex = contractionStart[contractionStart[torque]>(baselineAvg + threeSD)].index[0]
                    startTorque = data.loc[onsetIndex,torque]
                    baselineInfo = pd.DataFrame({'startIndex':startIndex,
                                                 'startTime':startTime,
                                                 'baselineAvg':baselineAvg,
                                                 'baselineSD':baselineSD,
                                                 'threeSD':threeSD,
                                                 'onsetIndex':onsetIndex,
                                                 'startTorque':startTorque},
                                                index=[0])
            else:
                startIndex = data[data[time].gt(start)].index[0]
                baselineStart = start - avg_duration
                baselineStartIndex = data[data[time].gt(baselineStart)].index[0]
                startTime = data.iloc[startIndex,0]
                baselineAvg = data[torque].iloc[baselineStartIndex:startIndex].mean()
                baselineSD = data[torque].iloc[baselineStartIndex:startIndex].std()
                threeSD = baselineSD * 3
                contractionStart = data[data.index >= startIndex]
                onsetIndex = contractionStart[contractionStart[torque]>(baselineAvg + threeSD)].index[0]
                startTorque = data.loc[onsetIndex,torque]
                baselineInfo = pd.DataFrame({'startIndex':startIndex,
                                             'startTime':startTime,
                                             'baselineAvg':baselineAvg,
                                             'baselineSD':baselineSD,
                                             'threeSD':threeSD,
                                             'onsetIndex':onsetIndex,
                                             'startTorque':startTorque},
                                            index=[0])
            return baselineInfo 
        
        def rfdcalc(data, onsetIndex, startTorque, time = 'Time', rfd50Time = 0.050, rfd100Time = 0.100, rfd200Time = 0.200):
            rel50Time = data.loc[onsetIndex,time] + rfd50Time
            rel100Time = data.loc[onsetIndex,time] + rfd100Time
            rel200Time = data.loc[onsetIndex,time] + rfd200Time
            rel50Index = data[data[time].gt(rel50Time)].index[0]
            rel100Index = data[data[time].gt(rel100Time)].index[0]
            rel200Index = data[data[time].gt(rel200Time)].index[0]
            if 'Corrected' in data.columns:
                fifty_forcediff = data.loc[rel50Index,'Corrected'] - data.loc[onsetIndex,'Corrected'] 
                fifty_timediff = data.loc[rel50Index,time] - data.loc[onsetIndex,time]
                rfd50 = fifty_forcediff / fifty_timediff
                onehund_forcediff = data.loc[rel100Index,'Corrected'] - data.loc[onsetIndex,'Corrected']
                onehund_timediff = data.loc[rel100Index,time] - data.loc[onsetIndex,time]
                rfd100 = onehund_forcediff / onehund_timediff
                twohund_forcediff = data.loc[rel200Index,'Corrected'] - data.loc[onsetIndex,'Corrected']
                twohund_timediff = data.loc[rel200Index,time] - data.loc[onsetIndex,time]
                rfd200 = twohund_forcediff / twohund_timediff
                output = pd.DataFrame({'fifty_index':rel50Index,
                                       'onehundred_index':rel100Index,
                                       'twohundred_index':rel200Index,
                                       'rfd50':rfd50,
                                       'rfd100':rfd100,
                                       'rfd200':rfd200},
                                      index=[0])
            else:
                fifty_forcediff = data.loc[rel50Index,'Force'] - data.loc[onsetIndex,'Force'] 
                fifty_timediff = data.loc[rel50Index,time] - data.loc[onsetIndex,time]
                rfd50 = fifty_forcediff / fifty_timediff
                onehund_forcediff = data.loc[rel100Index,'Force'] - data.loc[onsetIndex,'Force']
                onehund_timediff = data.loc[rel100Index,time] - data.loc[onsetIndex,time]
                rfd100 = onehund_forcediff / onehund_timediff
                twohund_forcediff = data.loc[rel200Index,'Force'] - data.loc[onsetIndex,'Force']
                twohund_timediff = data.loc[rel200Index,time] - data.loc[onsetIndex,time]
                rfd200 = twohund_forcediff / twohund_timediff
                output = pd.DataFrame({'fifty_index':rel50Index,
                                       'onehundred_index':rel100Index,
                                       'twohundred_index':rel200Index,
                                       'rfd50':rfd50,
                                       'rfd100':rfd100,
                                       'rfd200':rfd200},
                                      index=[0])
            return output
        
        onset = baseline(data=forceData)
        rfdTable = rfdcalc(data=forceData,onsetIndex = onset.loc[0,'onsetIndex'],startTorque = onset.loc[0,'startTorque'])
        finalRfdTable = rfdTable.loc[0,['rfd50','rfd100','rfd200']]
with rfd:
    with st.expander('Step 5: View and download your RFD values'):
        st.header('Here are your RFD values')
        st.text("After clicking the button above, a plot of your time points overlaid on the \nforce-time curve and a table of your RFD values should appear below.")
        if CalcButton:
            fig4,ax4 = plt.subplots()
            if 'Corrected' in forceData.columns:
                ax4.plot(forceData['Time'],forceData['Corrected'],label='Force')
                ax4.scatter(forceData.loc[rfdTable['fifty_index'],'Time'],forceData.loc[rfdTable['fifty_index'],'Corrected'],label='rfd50')
                ax4.scatter(forceData.loc[rfdTable['onehundred_index'],'Time'],forceData.loc[rfdTable['onehundred_index'],'Corrected'],label='rfd100')
                ax4.scatter(forceData.loc[rfdTable['twohundred_index'],'Time'],forceData.loc[rfdTable['twohundred_index'],'Corrected'],label='rfd200')
                ax4.hlines(xmin=0,xmax=100,y=forceData.loc[onset.loc[0,'onsetIndex'],'Corrected'],color='r',linestyle='--',label='onset')
                legend = ax4.legend(loc='upper right')
                ax4.set(xlabel = 'Time (s)',
                        ylabel = 'Force (N)',
                        xlim=[0,15])
                st.pyplot(fig4)
            else:
                ax4.plot(forceData['Time'],forceData['Force'],label='Force')
                ax4.scatter(forceData.loc[rfdTable['fifty_index'],'Time'],forceData.loc[rfdTable['fifty_index'],'Force'],label='rfd50')
                ax4.scatter(forceData.loc[rfdTable['onehundred_index'],'Time'],forceData.loc[rfdTable['onehundred_index'],'Force'],label='rfd100')
                ax4.scatter(forceData.loc[rfdTable['twohundred_index'],'Time'],forceData.loc[rfdTable['twohundred_index'],'Force'],label='rfd200')
                ax4.hlines(xmin=0,xmax=100,y=forceData.loc[onset.loc[0,'onsetIndex'],'Force'],color='r',linestyle='--',label='onset')
                legend = ax4.legend(loc='upper right')
                ax4.set(xlabel = 'Time (s)',
                        ylabel = 'Force (N)',
                        xlim=[0,15])
                st.pyplot(fig4)
            st.write(finalRfdTable.head())
            st.download_button('Click here to download your RFD values',finalRfdTable.to_csv(),mime='text/csv')