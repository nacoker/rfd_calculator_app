# -*- coding: utf-8 -*-
"""
Created on Fri Jul  1 16:47:19 2022

@author: ncoke
"""
#Import necessary libraries
import streamlit as st
import plotly.express as px
import pandas as pd
import matplotlib.pyplot as plt
from PIL import Image
from sklearn.linear_model import LinearRegression
from scipy.signal import filtfilt,butter
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
with calibration:
    with st.expander('Step 1: Upload your calibration file'):
        convert = st.radio('Does your file require conversion?',['Yes','No']) #Create button for input regarding file calibration
        st.text('If you are uploading a file that \nexpresses force in raw voltage, \nclick below to upload a calibration \nfile.')
        if convert == 'Yes':
            cal = st.file_uploader('Upload your calibration file here') # If yes answered to conversion, provide calibration file uploader
            try:
                calFile = pd.read_csv(cal,sep=',',names=['Voltage','Force'],header=0) # Create dataframe of calibration data
                st.write(calFile.head())
                calibration = LinearRegression() #Create linear regression function for load cell calibration
                calibration.fit(calFile['Voltage'].to_numpy().reshape(-1,1),calFile['Force'].to_numpy().reshape(-1,1)) #Fit load cell data to be used for force conversion     
            except:
                pass

#Create force file upload container
with force:
    with st.expander('Step 2: Upload your force-time curve'):
        col1, col2 = st.columns(2) # Create columns for image and figure generation
        with col1:
            image = Image.open('force example.PNG') # Upload image to use for format comparison
            st.image(image)
            with col2:
                file = st.file_uploader('Upload your file here') # Create file uploader for force-time curve upload
                filter_data = st.radio('Would you like to filter your data before calculating RFD?',['Yes','No']) #Accept input regarding filtering
                if file:
                    file2 = pd.read_csv(file,sep='\t',names=['Time','Force'],header=0) # If file placed into uploader, attempt dataframe creation

#Create dataset container to be used for data inspection
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
                    st.write(forceData.head()) # Display first 6 rows of offset-corrected force-time curve
                else: 
                    st.write(forceData.head()) # Display first 6 rows of uncorrected force-time curve
        with col2: 
            if file:
                if filter_data:
                        def filter_data(forceData,order=4,low_cut=15,sampleFreq=2222): # Define function for filtering force data with 4th order low-pass Butterworth (cutoff = 15 Hz)
                            nyq = sampleFreq * 0.5 # Define Nyquist frequency
                            low = low_cut / nyq # Define cutoff frequency relative to Nyquist
                            b,a = butter(order,low,'lowpass',analog=False) # Calculate filter coefficients
                            if 'Corrected' in forceData.columns:
                                filtered = filtfilt(b,a,forceData['Corrected']) #If data was offset-corrected,filter corrected data
                                filtered = pd.Series(filtered,name='filtered') #Store filtered data as series
                            else:
                                filtered = filtfilt(b,a,forceData['Force']) # If data wasn't offset corrected, filter uncorrected data
                                filtered = pd.Series(filtered,name='filtered') # Store filtered data as series
                            filtered = pd.concat([forceData,filtered],axis=1) #Add filtered data to dataframe as additional column
                            return filtered
                        forceData = filter_data(forceData) # Filter force data and return filtered output
                fig1,ax1 = plt.subplots() # Create figure to be used for plotting filtered data
                if 'filtered' in forceData.columns:
                    ax1.plot(forceData['Time'],forceData['filtered']) #Plot filtered data
                    ax1.set(xlabel = 'Time (s)', 
                            ylabel = 'Force (N)') # Set x/y axis labels
                    st.pyplot(fig1) # show plot
                elif 'Corrected' in forceData.columns:
                    ax1.plot(forceData['Time'],forceData['Corrected']) # If data not filtered but is offset corrected, plot corrected values
                    ax1.set(xlabel = 'Time (s)',
                            ylabel = 'Force (N)') # Set x/y axis labels
                    st.pyplot(fig1) # show plot
                else:
                    ax1.plot(forceData['Time'],forceData['Force']) # Plot uncorrected raw force data
                    ax1.set(xlabel = 'Time (s)',
                            ylabel = 'Force (N)') # Set x/y axis labels
                    st.pyplot(fig1) # show plot
        recordStartTime = st.number_input('For the contraction of interest, what time did you start recording? For example, if you want to analyze rep 2, which starts at 15 seconds, enter 15.',min_value=0.0,max_value=60.0,step=0.1) # Used to store first time value in recording
        stopTime = st.number_input('What time was that contraction supposed to end? If necessary, include rest at the end of the contraction, e.g. 5 second baseline, 5 second contraction, 5 second rest = 15 seconds',min_value=1.0,max_value=60.0,value=15.0,step=0.1) # Used to store last time value in recording

#Create inputs container to be used to determine outputs
with inputs:
    with st.expander('Step 4: Tell us about how you want to calculate RFD'):
        st.header('How would you like to calculate RFD?')
        col1,col2 = st.columns(2)
        with col1:
            sampleFreq = st.number_input('Enter the sampling rate of your force measurement device:') # Number input to input sampling frequency
            offset = st.radio('Does your file require offset correction?',['Yes','No']) # Selection for whether data needs to be offset corrected
        with col2:
            onset = st.radio('Select your onset determination method:',['Manual onset determination', 'Onset will be +3SD of the baseline signal']) # Selection for method of onset determination
            rfdVals = st.multiselect('Which RFD values would you like to calculate? Select all that apply:',['RFD50','RFD100','RFD200'],['RFD50','RFD100','RFD200']) # Selection for RFD outputs to calculate
        startTime = st.number_input('For the contraction of interest, what time was the contraction supposed to start? For example, if you analyzed a contraction that included a five-second resting baseline, enter 5.',min_value=1.0,max_value=60.0,step=0.1) # Input value to be used for onset visualization
        if (onset == 'Manual onset determination') & (offset == 'Yes'):
            if file:
                manualTime = st.slider('How long would you like your manual viewing window to be in milliseconds?',50,2000,value=300,step=50) # Input for determining x-axis of onset plot
                manualTime = manualTime / 1000 # convert manualTime input to milliseconds
                startTimeIndex = forceData[forceData['Time'].gt(startTime)].index[0] # Find and store first index where time is greater than startTime value
                lowViewTime = forceData.loc[startTimeIndex,'Time'] - (manualTime/2) # Subtract half of viewing window from start time
                lowViewIndex = forceData[forceData['Time'].gt(lowViewTime)].index[0] # Find index corresponding to lowViewTime
                highViewTime = forceData.loc[startTimeIndex,'Time'] + (manualTime/2) #Repeat steps from previous lines for upper time limit
                highViewIndex = forceData[forceData['Time'].gt(highViewTime)].index[0]
                offStart = sampleFreq * (startTime - 4) # Calculate start of window for time used for offset calculation
                offStop = sampleFreq * startTime # Calculate end of window for time used for offset calculation
                if 'filtered' in forceData.columns:
                    offsetValue = forceData.loc[offStart:offStop,'filtered'].mean() #Calculate mean of baseline signal for offset
                    forceData['filtered'] = forceData['filtered'] - offsetValue #Offset-correct filtered signal
                    Manual = forceData[(forceData['Time'] > lowViewTime) & (forceData['Time'] < highViewTime)] #Create subset of dataframe to only include force data between lowViewTime and highViewTime
                    fig = px.line(Manual,x='Time',y='filtered') #Create line plot of data subset for onset determination
                    st.write(fig) # show plot
                    manualOnset = st.number_input('Based on the graph above, what time did your contraction start?',step=1e-6,format="%.5f") # Create input for time value of force onset to use for RFD calculation
                elif 'Corrected' in forceData.columns:
                    offsetValue = forceData.loc[offStart:offStop,'Corrected'].mean() #Calculate offset as described above
                    forceData['Corrected'] = forceData['Corrected'] - offsetValue # Correct force values based on offset calculation
                    Manual = forceData[(forceData['Time'] > lowViewTime) & (forceData['Time'] < highViewTime)]  # Create subset as described above
                    fig = px.line(Manual,x='Time',y='Corrected') # Create plot of data subset
                    st.write(fig) #show plot
                    manualOnset = st.number_input('Based on the graph above, what time did your contraction start?',step=1e-6,format="%.5f") # Create input for time corresponding to force onset to use for RFD calculation
                else:
                    offsetValue = forceData.loc[offStart:offStop,'Force'].mean()
                    forceData['Force'] = forceData['Force'] - offsetValue
                    Manual = forceData[(forceData['Time'] > lowViewTime) & (forceData['Time'] < highViewTime)] 
                    fig = px.line(Manual,x='Time',y='Force')
                    st.write(fig)
                    manualOnset = st.number_input('Based on the graph above, what time did your contraction start?',step = 1e-6,format="%.5f")
        elif (onset == 'Onset will be +3SD of the baseline signal') & (offset == 'Yes'):
            if file:
                offStart = sampleFreq * (startTime - 4)
                offStop = sampleFreq * startTime 
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
        CalcButton = st.button('Click here to calculate your RFD values') # Button to initiate calculation of RFD
    if CalcButton:
        def baseline(data,time='Time',torque='Force',start=startTime,avg_duration=4):
            if 'filtered' in data.columns:
                if (onset == 'Manual onset determination'):
                    start = manualOnset
                    torque = 'filtered'
                    onsetIndex = data[data[time].gt(start)].index[0]
                    return onsetIndex
                elif (onset == 'Onset will be +3SD of the baseline signal'):
                    torque = 'filtered'
                    startIndex = data[data[time].gt(start)].index[0]
                    baselineStart = start - avg_duration
                    baselineStartIndex = data[data[time].gt(baselineStart)].index[0]
                    baselineAvg = data[torque].iloc[baselineStartIndex:startIndex].mean()
                    baselineSD = data[torque].iloc[baselineStartIndex:startIndex].std()
                    threeSD = baselineSD * 3
                    onsetIndex = data[data[torque]>(baselineAvg + threeSD)].index[0]
                    return onsetIndex
            elif 'Corrected' in data.columns:
                if (onset == 'Manual onset determination'):
                    start = manualOnset
                    torque = 'Corrected'
                    onsetIndex = data[data[time].gt(start)].index[0]
                    return onsetIndex
                elif (onset == 'Onset will be +3SD of the baseline signal'):
                    torque = 'Corrected'
                    startIndex = data[data[time].gt(start)].index[0]
                    baselineStart = start - avg_duration
                    baselineStartIndex = data[data[time].gt(baselineStart)].index[0]
                    baselineAvg = data[torque].iloc[baselineStartIndex:startIndex].mean()
                    baselineSD = data[torque].iloc[baselineStartIndex:startIndex].std()
                    threeSD = baselineSD * 3
                    onsetIndex = data[data[torque]>(baselineAvg + threeSD)].index[0]
                    return onsetIndex
            else:
                if (onset == 'Manual onset determination'):
                    start = manualOnset
                    onsetIndex = data[data[time].gt(start)].index[0]
                    return onsetIndex
                elif (onset == 'Onset will be +3SD of the baseline signal'):
                    startIndex = data[data[time].gt(start)].index[0]
                    baselineStart = start - avg_duration
                    baselineStartIndex = data[data[time].gt(baselineStart)].index[0]
                    baselineAvg = data[torque].iloc[baselineStartIndex:startIndex].mean()
                    baselineSD = data[torque].iloc[baselineStartIndex:startIndex].std()
                    threeSD = baselineSD * 3
                    onsetIndex = data[data[torque]>(baselineAvg + threeSD)].index[0]
                    return onsetIndex
        def rfdcalc(data, onsetIndex, time = 'Time', rfd50Time = 0.050, rfd100Time = 0.100, rfd200Time = 0.200): # Define function for calculation of RFD
            rel50Time = data.loc[onsetIndex,time] + rfd50Time
            rel100Time = data.loc[onsetIndex,time] + rfd100Time
            rel200Time = data.loc[onsetIndex,time] + rfd200Time
            rel50Index = data[data[time].gt(rel50Time)].index[0]
            rel100Index = data[data[time].gt(rel100Time)].index[0]
            rel200Index = data[data[time].gt(rel200Time)].index[0]
            if filter_data:
                fifty_forcediff = data.loc[rel50Index,'filtered'] - data.loc[onsetIndex,'filtered'] 
                fifty_timediff = data.loc[rel50Index,time] - data.loc[onsetIndex,time]
                rfd50 = fifty_forcediff / fifty_timediff
                onehund_forcediff = data.loc[rel100Index,'filtered'] - data.loc[onsetIndex,'filtered']
                onehund_timediff = data.loc[rel100Index,time] - data.loc[onsetIndex,time]
                rfd100 = onehund_forcediff / onehund_timediff
                twohund_forcediff = data.loc[rel200Index,'filtered'] - data.loc[onsetIndex,'filtered']
                twohund_timediff = data.loc[rel200Index,time] - data.loc[onsetIndex,time]
                rfd200 = twohund_forcediff / twohund_timediff
                output = pd.DataFrame({'fifty_index':rel50Index,
                                       'onehundred_index':rel100Index,
                                       'twohundred_index':rel200Index,
                                       'rfd50':rfd50,
                                       'rfd100':rfd100,
                                       'rfd200':rfd200},
                                      index=[0])
            elif 'Corrected' in data.columns:
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
        
                
        onsetIndex = baseline(data=forceData) # Calculate onsetIndex to be used as RFD start point
        if filter_data:
            rfdTable = rfdcalc(data=forceData,onsetIndex = onsetIndex) # Calculate RFD values
        else:
            rfdTable = rfdcalc(data=forceData,onsetIndex = onsetIndex) #Calculate RFD values           
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