# rfd_calculator_app
Streamlit app that will take an isometric force time-series and calculate RFD through either automated or manual detection methods

[You can access the app here](https://share.streamlit.io/nacoker/rfd_calculator_app/main/rfd_app.py)

The rfd_app.py file creates a streamlit app that accepts inputs from the user and calculates commonly used metrics for rate of force development (RFD) based on user responses. The app consists of five collapsible menus that produce a step-by-step walkthrough. 

## Step 1: Uploading a calibration file

The first dropdown menu is used to determine whether or not the data need to be adjusted prior to analysis. If the user plans to upload force data that is expressed in Volts instead of Newtons, then they should select "Yes" and upload a tab-delimited .txt file consisting of two columns: a column of output voltages recorded by their force device with known loads applied, and a column of the weight of the load in Newtons. If this is done, linear regression will be used to convert voltage values to force values on the subsequent dataset. If the data being uploaded are already expressed in Newtons, click "No".

## Step 2: Uploading your force trace

The second dropdown menu is used to import the data that will be used for analysis. This should also be a tab-delimited .txt file consisting of two columns: a column of the time values corresponding to the force measurement, and a column of force measurements. An example image is provided on the left. 

## Step 3: Inspecting your dataset

The third dropdown menu shows a dataframe of the file uploaded in step 2 as well as a plot of force changes over time. **NOTE**: If a calibration file was uploaded in step 1, there will be a 3rd column, 'Corrected', which is the force expressed in Newtons according to the values predicted from the calibration file. In this case, the data plotted will be 'Corrected' over time, not 'Force'. 

This section also accepts user inputs, which is useful in the event that multiple contractions are written onto the same file. These inputs are used to define the beginning and end of the contraction of interest. For example, the sample file 'MVIC TEST.txt' consists of three maximal contractions, each 15 seconds in length: five seconds of quiet recording, a five second maximal isometric contraction, and five seconds of rest following the end of the contraction. If the user would like to analyze the first contraction, they should enter values of '0.0' and '15.0', respectively. However, if they wanted to analyze the second contraction, they should enter values of '15.0' and '30.0', respectively. 

## Step 4: Provide inputs to determine how RFD will be calculated

This section accepts user inputs which are used to make decisions relevant to RFD calculation. The first is to enter the sampling rate in Hz and select whether the data will require offset correction. If the user indicates offset correction is needed, an average of the baseline signal is calculated and subtracted from the entire time series. The second column asks the user to determine the method of determining contraction onset as well as which RFD values they would like to calculate. The onset method selection can be set to either an automatic or manual onset detection. If the automatic input is selected, the mean and 3 standard deviations of the baseline signal will be calculated, and onset will be determined as the first value that exceeds baseline + 3SD. If manual onset detection is selected, the user will be asked when the contraction was supposed to start and a time window they would like to view. A figure is created that is centered on the start input around the viewing window (e.g. if 5 seconds and 300 ms are selected, the figure will show 4.85 to 5.15 s). Based on this figure, the user is asked to visually determine contraction onset. Once these inputs are set, the user can click the button below to calculate RFD. 

## Step 5: View and download RFD values

Once the button in step 4 is clicked, a figure will be created showing the force-time curve, the instant of onset (horizontal red line), and the rfd values selected. Additionally, below the figure, the RFD values are presented in a dataframe, and may also be downloaded as a .csv file. 
