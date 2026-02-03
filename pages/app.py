# -*- coding: utf-8 -*-
"""
Created on Tue Jan 13 08:34:09 2026

@author: nickwork
"""

import streamlit as st



calibration_page = st.Page('calibration.py', title = 'Step 1: Calibration')
processing_page = st.Page('file_processing.py', title = 'Step 2: File Processing')
calculation_page = st.Page('rfd_calculator.py', title = 'Step 3: Calculate RFD')
display_page = st.Page('rfd_display.py', title = 'Step 4: Display Your Results')

pg = st.navigation([calibration_page, 
                    processing_page, 
                    calculation_page, 
                    display_page])
pg.run()

