#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat May  1 18:15:23 2021

@author: chrisarnold
"""

#%% ACL Econometrics Project

# Import General Packages

import sys
import os

# Import Packages for the Peer Analysis Portion

import streamlit as st
import altair as alt
import plotly as plt
import datetime as dt
import pandas as pd
import numpy as np

# Import Packages for the Manuel Earnings Release PDF to Excel Download

import subprocess
import camelot
from PyPDF2 import PdfFileWriter
from PyPDF2 import PdfFileReader
from camelot.core import TableList
import datetime as dt
import time
import requests
import shutil
from io import BytesIO
import io
from pathlib import Path


#%% Create a title

st.title("""
         
         Allowance for Credit Losses
         
         **Peer Bank Analysis**
         
         """)
         

#%% Pull in relevant data

github_path = 'https://raw.githubusercontent.com/arnold-798/Bank-_ACL_Forecasting/main/'

@st.cache
def load_peer_data(nrows):
    data_path = os.path.join(github_path, 'panel_bank_data_042021.csv')
    data_path = data_path.replace('\\', '/')
    data = pd.read_csv(data_path, sep = ',', nrows=nrows, error_bad_lines=False)
    return data

@st.cache
def load_fredqd(nrows):
    data_path = os.path.join(github_path, 'fred_qd_042021.csv') 
    data_path = data_path.replace('\\', '/')
    data = pd.read_csv(data_path, sep = ',', skiprows=[i for i in range(1,131)], nrows=nrows, error_bad_lines=False) 
    return data

peer_path = os.path.join(github_path, 'panel_bank_data_042021.csv')
peer_path = peer_path.replace('\\', '/')
peer = pd.read_csv(peer_path, sep = ',', nrows=2400, error_bad_lines=False)

#%% Create the instructions page

def instructions():
    st.header("Instructions")
    
    st.subheader("Functions of the tool")
    
    st.write("This tool aggregates peer bank data from 1990 to present along with macroeconomic data to" + 
            " analysis ACL, loss and provisional trends across peer banks")
    st.write("Utilize the tool to perform simiple arithmetic forecasting as well as econometric" + 
            "forecasting with linear and ARIMA models")
    st.write("The tool also has a tool to download earnings releases pdfs into excel - this is stil" + 
             "in test format so please provide feeedback if it is not working properly")

#%% Individual Bank Earnings Release PDF to Excel Download

def manual_extract():
    
    st.header("Earnings Release PDF to Excel")
    st.write("This tool works best with specific formatting - i.e. banks with full page " + 
             "financial statement tables produce better more defined results")
    
    # Test out direct links to the internet pdf path
    # Maybe even a section to just download the file to a working directory and then use the function below to grab them



    def extract_xlsx(directory):
    
        def total_pages(pdf):
            pdf_object = PdfFileReader(open(pdf, 'rb'))
            pages = ','.join([str(i) for i in list(range(pdf_object.getNumPages()))])
            return pages
        
        # Figure out how to manipulate the extraction formuala to export to a new path

        for pdf in os.listdir(directory):
               file_name, file_extension = os.path.splitext(pdf)
               if file_extension == '.pdf':
                   #cmd = "pdfgrep -Pn '^(?s:(?=.*Revenue)|(?=.*Income))' " + pdf + " | awk -F\":\" '$0~\":\"{print $1}' | tr '\n' ','"
                   #pages = subprocess.check_output(cmd, shell=True).decode("utf-8")
                   #print(pdf)
                   pages = total_pages(pdf)
                   tables = camelot.read_pdf(pdf, flavor='stream', pages=pages, edge_tol=100)
                   filtered = []
                   st.text((str(pages)))
                   for index, table in enumerate(tables):
                       whitespace = tables[index].parsing_report.get('whitespace')
                       if whitespace <= 100000: 
                           filtered.append(tables[index])
                           filtered_tables = TableList(filtered)
                           filtered_tables.export((file_name + ".xlsx"), f='excel', compress=True)
    
    st.subheader("Step 1: Downlaod the earnings release PDFs and upload the PDF files")
    
    pdf_upload = st.file_uploader(label = "File Upload Link - Upload Earnings Release PDFs Here:", type = ["pdf", "png"])
    
    if pdf_upload is not None: 
        file_details = {"FileName":pdf_upload.name,"FileType":pdf_upload.type,"FileSize":pdf_upload.size}
        st.write(file_details)
        st.write(type(pdf_upload))
        #pdf_mem = PdfFileReader(pdf_upload)
        #st.write(dir(pdf_upload))
        
     
    er_file_path = st.text_input(label="Paste the file path to a 'working directory' where you want to save the files to", 
                                 help=("- C:/Users/User/Desktop for Windows" + "or" + "/Users/User/Desktop for macs " + 
                                       "It's recomended that you just set the working directory path to your desktop " + 
                                       "Code will create new folder for each quarter identified"))
    
    bank_nm = st.text_input(label="Which bank is this for?")
    
    year_quarter = st.text_input(label="What year and quarter is it?", help="Recomended Format: YYYYQQ")
       
    
    start_button = st.button("Run", key = "Run")
    
    if start_button: 
        
        # Export zip files to a new folder 
    
        new_path = os.path.join(er_file_path, year_quarter)
        
        path_exists_ind = os.path.exists(new_path)
        
        def change_permissions_recursive(path, mode):
            for root, dirs, files in os.walk(path, topdown=False):
                for dir in [os.path.join(root,d) for d in dirs]:
                    os.chmod(dir, mode)
            for file in [os.path.join(root, f) for f in files]:
                    os.chmod(file, mode)
                    
        change_permissions_recursive(new_path, 0o777)
        
        st.write(path_exists_ind, "Still working through permissions / access issues to create new folders for each Year_Quarter")
        
        # Need to figure out how to make a new directory from streamlit
        
        #if not os.path.exists('my_folder'):
            #os.chmod()
            #os.makedirs(new_path)
            
        os.chdir(new_path)
        
        #pdf_writer = PdfFileWriter()
        
        #with Path().open(mode="wb") as output_file: 
        #    pdf_writer.write(output_file) 
        
        def save_uploadedfile(uploadedfile):
            with open(os.path.join(new_path,uploadedfile.name),"wb") as f:
                f.write(uploadedfile.getbuffer())
                return st.success(("Saved File:{} " + new_path).format(uploadedfile.name))
        
        save_uploadedfile(pdf_upload)
        
        extract_xlsx(new_path)

        st.spinner()
        with st.spinner(text="In Progress"):
            time.sleep(300)
            st.success("Done - Double check the xlsx output to the PDF before finalizing any data as 'FTP'")
           
    
    st.subheader("Step 2: Check that a zip file has been created for each of your PDFs")
    
    start_button_v2 = st.button("Check", key = "Check")
    
    if start_button_v2:
        st.text("There should be 3 files in the working directory for each earnings release downloaded; pdf, zipfile, xlsx")
        st.write(os.listdir())
        
    st.subheader("Next Steps: ")
    st.text("Incorporate an append function to the existing dataset with the existing historical")
    st.text("dataset in order to perform analysis with most up to date data")
    
    st.text("Potentially a specific ACL report? Provision, Coverage Rate, ACL % Change, NCO Rates")
    st.text("Other ideas???")


#%% Peer Analysis Standard Visuals & Tables

def peer_visuals():
    st.header("Peer Analysis Standard Deck Visuals")
    
    fred_qd_raw = load_fredqd(120) 
    peer_bank_raw = load_peer_data(2400)
        
    # Select Quarter
    
    quarter = st.selectbox(label = "Select the current quarter or quarter you want to view:", options = ['Q1', 'Q2', 'Q3', 'Q4'])
    year = st.selectbox(label = "Select the current year or year you want to view:", 
                        options = ['1990', '1991', '1992', '1993', '1994', '1995', '1996', '1997', '1998', '1999', 
                                   '2000', '2001', '2002', '2003', '2004', '2005', '2006', '2007', '2008', '2009',
                                   '2010', '2011', '2012', '2013', '2014', '2015', '2016', '2017', '2018', '2019',
                                   '2020', '2021', '2022', '2023', '2024', '2025', '2026', '2027', '2028', '2029'])
    curr_year_quarter = "".join([year, quarter])
    
    # Subset the dataframe to only the selected year
    
    current_bank_data = peer_bank_raw[peer_bank_raw['YEAR_QUARTER'] == curr_year_quarter]
    
    # Select Bank
    
    bank_list = peer_bank_raw['BANK_NAME_ABBR'].values
    
    def unique(list1):
        x = np.array(list1)
        return (np.unique(x))
    
    bank_list = unique(bank_list)
    
    bank_name = st.selectbox(label = "Select the bank you wish to analyze:", options = bank_list)
    bank_data = current_bank_data[current_bank_data["BANK_NAME_ABBR"] == bank_name]
    
    # Coverage Rate Waterfall Walks - Past 5 Quarters
    
    st.subheader("Coverage Rate Waterfall - Current Quarter")
          
    peer_group = current_bank_data[current_bank_data['BANK_NAME_ABBR'] != bank_name]

    new_bank_type = bank_name
    
    bank_data['BANK_TYPE'] = bank_data['BANK_TYPE'].replace(['Peer'], new_bank_type)
    
    peer_compare_data = pd.concat([peer_group, bank_data])
           
    agg_peer = peer_compare_data.groupby('BANK_TYPE').agg('sum')[['NCO_TO_AVG_LOAN_CU', 'TOTAL_LOAN_LEASES_EXCL_HFS', 'TOTAL_RESV', 'PROV_FOR_LOAN_LEASE_LOSS', 
                                                                  'LN_AND_LS_HFI_AMORT_COST_RE_CONST_LOAN',
                                                                  'LN_AND_LS_HFI_AMORT_COST_COM_RE_LOAN',
                                                                  'LN_AND_LS_HFI_AMORT_COST_RES_RE_LOAN',
                                                                  'LN_AND_LS_HFI_AMORT_COST_COM_LOAN',
                                                                  'LN_AND_LS_HFI_AMORT_COST_CREDIT_CARD',
                                                                  'LN_AND_LS_HFI_AMORT_COST_OTHER_CONSUMER_LOAN',
                                                                  'LN_AND_LS_HFI_AMORT_COST_TOTAL',
                                                                  'LN_AND_LS_HFI_ALLOWANCE_RE_CONST_LOAN',
                                                                  'LN_AND_LS_HFI_ALLOWANCE_COM_RE_LOAN',
                                                                  'LN_AND_LS_HFI_ALLOWANCE_RES_RE_LOAN',
                                                                  'LN_AND_LS_HFI_ALLOWANCE_COM_LOAN',
                                                                  'LN_AND_LS_HFI_ALLOWANCE_CREDIT_CARD',
                                                                  'LN_AND_LS_HFI_ALLOWANCE_OTHER_CONSUMER_LOAN',
                                                                  'LN_AND_LS_HFI_ALLOWANCE_UNALLOCATED', 
                                                                  'LN_AND_LS_HFI_ALLOWANCE_TOTAL']]
    
    #agg_peer = pd.concat([agg_peer, bank_data], axis = 0)

    # Peer Coverage Rates by FRB Y9-C Industry Code

    st.subheader("Peer Coverage Rates Across FRB Y9-C Defined Products")
    
    agg_peer_pct = agg_peer
    agg_peer_num = agg_peer
    
    agg_peer_pct = agg_peer_pct.assign(Construction_RE_Coverage_Rate = agg_peer_pct['LN_AND_LS_HFI_ALLOWANCE_RE_CONST_LOAN'] / agg_peer_pct['LN_AND_LS_HFI_AMORT_COST_RE_CONST_LOAN'])
    agg_peer_num = agg_peer_num.assign(Construction_RE_Coverage_Rate = agg_peer_num['LN_AND_LS_HFI_ALLOWANCE_RE_CONST_LOAN'] / agg_peer_num['LN_AND_LS_HFI_AMORT_COST_RE_CONST_LOAN'])
       
    agg_peer_pct['Construction_RE_Coverage_Rate'] = pd.Series([round(val, 6) for val in agg_peer_pct['Construction_RE_Coverage_Rate']], index = agg_peer_pct.index)
    agg_peer_pct['Construction_RE_Coverage_Rate'] = pd.Series(["{0:.2f}%".format(val * 100) for val in agg_peer_pct['Construction_RE_Coverage_Rate']], index = agg_peer_pct.index)    
    
    agg_peer_pct = agg_peer_pct.assign(Commercial_RE_Coverage_Rate = agg_peer_pct['LN_AND_LS_HFI_ALLOWANCE_COM_RE_LOAN'] / agg_peer_pct['LN_AND_LS_HFI_AMORT_COST_COM_RE_LOAN'])
    agg_peer_num = agg_peer_num.assign(Commercial_RE_Coverage_Rate = agg_peer_num['LN_AND_LS_HFI_ALLOWANCE_COM_RE_LOAN'] / agg_peer_num['LN_AND_LS_HFI_AMORT_COST_COM_RE_LOAN'])

    agg_peer_pct['Commercial_RE_Coverage_Rate'] = pd.Series([round(val, 6) for val in agg_peer_pct['Commercial_RE_Coverage_Rate']], index = agg_peer_pct.index)
    agg_peer_pct['Commercial_RE_Coverage_Rate'] = pd.Series(["{0:.2f}%".format(val * 100) for val in agg_peer_pct['Commercial_RE_Coverage_Rate']], index = agg_peer_pct.index)    

    agg_peer_pct = agg_peer_pct.assign(Residential_RE_Coverage_Rate = agg_peer_pct['LN_AND_LS_HFI_ALLOWANCE_RES_RE_LOAN'] / agg_peer_pct['LN_AND_LS_HFI_AMORT_COST_RES_RE_LOAN'])
    agg_peer_num = agg_peer_num.assign(Residential_RE_Coverage_Rate = agg_peer_num['LN_AND_LS_HFI_ALLOWANCE_RES_RE_LOAN'] / agg_peer_num['LN_AND_LS_HFI_AMORT_COST_RES_RE_LOAN'])
    
    agg_peer_pct['Residential_RE_Coverage_Rate'] = pd.Series([round(val, 6) for val in agg_peer_pct['Residential_RE_Coverage_Rate']], index = agg_peer_pct.index)
    agg_peer_pct['Residential_RE_Coverage_Rate'] = pd.Series(["{0:.2f}%".format(val * 100) for val in agg_peer_pct['Residential_RE_Coverage_Rate']], index = agg_peer_pct.index)    
   
    agg_peer_pct = agg_peer_pct.assign(Commercial_Coverage_Rate = agg_peer_pct['LN_AND_LS_HFI_ALLOWANCE_COM_LOAN'] / agg_peer_pct['LN_AND_LS_HFI_AMORT_COST_COM_LOAN'])
    agg_peer_num = agg_peer_num.assign(Commercial_Coverage_Rate = agg_peer_num['LN_AND_LS_HFI_ALLOWANCE_COM_LOAN'] / agg_peer_num['LN_AND_LS_HFI_AMORT_COST_COM_LOAN'])
    
    agg_peer_pct['Commercial_Coverage_Rate'] = pd.Series([round(val, 6) for val in agg_peer_pct['Commercial_Coverage_Rate']], index = agg_peer_pct.index)
    agg_peer_pct['Commercial_Coverage_Rate'] = pd.Series(["{0:.2f}%".format(val * 100) for val in agg_peer_pct['Commercial_Coverage_Rate']], index = agg_peer_pct.index)    

    agg_peer_pct = agg_peer_pct.assign(Credit_Card_Coverage_Rate = agg_peer_pct['LN_AND_LS_HFI_ALLOWANCE_CREDIT_CARD'] / agg_peer_pct['LN_AND_LS_HFI_AMORT_COST_CREDIT_CARD'])
    agg_peer_num = agg_peer_num.assign(Credit_Card_Coverage_Rate = agg_peer_num['LN_AND_LS_HFI_ALLOWANCE_CREDIT_CARD'] / agg_peer_num['LN_AND_LS_HFI_AMORT_COST_CREDIT_CARD'])
    
    agg_peer_pct['Credit_Card_Coverage_Rate'] = pd.Series([round(val, 6) for val in agg_peer_pct['Credit_Card_Coverage_Rate']], index = agg_peer_pct.index)
    agg_peer_pct['Credit_Card_Coverage_Rate'] = pd.Series(["{0:.2f}%".format(val * 100) for val in agg_peer_pct['Credit_Card_Coverage_Rate']], index = agg_peer_pct.index)    

    agg_peer_pct = agg_peer_pct.assign(Other_Consumer_Coverage_Rate = agg_peer_pct['LN_AND_LS_HFI_ALLOWANCE_OTHER_CONSUMER_LOAN'] / agg_peer_pct['LN_AND_LS_HFI_AMORT_COST_OTHER_CONSUMER_LOAN'])
    agg_peer_num = agg_peer_num.assign(Other_Consumer_Coverage_Rate = agg_peer_num['LN_AND_LS_HFI_ALLOWANCE_OTHER_CONSUMER_LOAN'] / agg_peer_num['LN_AND_LS_HFI_AMORT_COST_OTHER_CONSUMER_LOAN'])

    agg_peer_pct['Other_Consumer_Coverage_Rate'] = pd.Series([round(val, 6) for val in agg_peer_pct['Other_Consumer_Coverage_Rate']], index = agg_peer_pct.index)
    agg_peer_pct['Other_Consumer_Coverage_Rate'] = pd.Series(["{0:.2f}%".format(val * 100) for val in agg_peer_pct['Other_Consumer_Coverage_Rate']], index = agg_peer_pct.index)    

    agg_peer_pct = agg_peer_pct.assign(Total_ACL_Coverage_Rate = agg_peer_pct['LN_AND_LS_HFI_ALLOWANCE_TOTAL'] / agg_peer_pct['LN_AND_LS_HFI_AMORT_COST_TOTAL'])
    agg_peer_num = agg_peer_num.assign(Total_ACL_Coverage_Rate = agg_peer_num['LN_AND_LS_HFI_ALLOWANCE_TOTAL'] / agg_peer_num['LN_AND_LS_HFI_AMORT_COST_TOTAL'])

    agg_peer_pct['Total_ACL_Coverage_Rate'] = pd.Series([round(val, 6) for val in agg_peer_pct['Total_ACL_Coverage_Rate']], index = agg_peer_pct.index)
    agg_peer_pct['Total_ACL_Coverage_Rate'] = pd.Series(["{0:.2f}%".format(val * 100) for val in agg_peer_pct['Total_ACL_Coverage_Rate']], index = agg_peer_pct.index)    

    acl_coverage_rates_pct = agg_peer_pct[['Construction_RE_Coverage_Rate', 'Commercial_RE_Coverage_Rate', 
                                           'Residential_RE_Coverage_Rate', 'Commercial_Coverage_Rate', 'Credit_Card_Coverage_Rate', 'Other_Consumer_Coverage_Rate', 
                                           'Total_ACL_Coverage_Rate']]  
    
    test1 = acl_coverage_rates_pct.transpose()
    st.write(test1)
    
    acl_coverage_rates_num = agg_peer_num[['Construction_RE_Coverage_Rate', 'Commercial_RE_Coverage_Rate', 
                                           'Residential_RE_Coverage_Rate', 'Commercial_Coverage_Rate', 'Credit_Card_Coverage_Rate', 'Other_Consumer_Coverage_Rate', 
                                           'Total_ACL_Coverage_Rate']]
    
    test2 = acl_coverage_rates_num
        
    st.bar_chart(test2)
    
    # Peer Portfolio Mix by FRB Y9-C Industry Code
    
    agg_peer_mix = agg_peer
    
    agg_peer_mix = agg_peer_mix.assign(Construction_Pct_Mix = agg_peer_mix['LN_AND_LS_HFI_ALLOWANCE_RE_CONST_LOAN'] / agg_peer_mix['LN_AND_LS_HFI_AMORT_COST_RE_CONST_LOAN'])
    agg_peer_mix = agg_peer_mix.assign(Commercial_RE_Pct_Mix = agg_peer_mix['LN_AND_LS_HFI_ALLOWANCE_COM_RE_LOAN'] / agg_peer_mix['LN_AND_LS_HFI_AMORT_COST_COM_RE_LOAN'])
    agg_peer_mix = agg_peer_mix.assign(Residential_RE_Pct_Mix = agg_peer_mix['LN_AND_LS_HFI_ALLOWANCE_RES_RE_LOAN'] / agg_peer_mix['LN_AND_LS_HFI_AMORT_COST_RES_RE_LOAN'])
    agg_peer_mix = agg_peer_mix.assign(Commercial_Pct_Mix = agg_peer_mix['LN_AND_LS_HFI_ALLOWANCE_COM_LOAN'] / agg_peer_mix['LN_AND_LS_HFI_AMORT_COST_COM_LOAN'])
    agg_peer_mix = agg_peer_mix.assign(Credit_Card_Pct_Mix = agg_peer_mix['LN_AND_LS_HFI_ALLOWANCE_CREDIT_CARD'] / agg_peer_mix['LN_AND_LS_HFI_AMORT_COST_CREDIT_CARD'])
    agg_peer_mix = agg_peer_mix.assign(Other_Consumer_Pct_Mix = agg_peer_mix['LN_AND_LS_HFI_ALLOWANCE_OTHER_CONSUMER_LOAN'] / agg_peer_mix['LN_AND_LS_HFI_AMORT_COST_OTHER_CONSUMER_LOAN'])
    agg_peer_mix = agg_peer_mix.assign(Total_ACL_Pct_Mix = agg_peer_mix['LN_AND_LS_HFI_ALLOWANCE_TOTAL'] / agg_peer_mix['LN_AND_LS_HFI_AMORT_COST_TOTAL'])
    
    test2 = agg_peer_mix[['Construction_Pct_Mix', 'Commercial_RE_Pct_Mix', 
                                   'Residential_RE_Pct_Mix', 'Commercial_Pct_Mix', 'Credit_Card_Pct_Mix', 
                                   'Other_Consumer_Pct_Mix', 'Total_ACL_Pct_Mix']]
    
    
    # Peer Reserves Schedule - QoQ
    
    ## ACL Walk - Beg ACL, NCOs, Provision, Plug, Ending Balance
    
    ### Upload individual table or picture?
    
    # Provision / NCO Stacked Bar Chart 
    
    peer_bankv1 = peer_bank_raw[['']]
    
    bank_datav1 = peer_bank_raw[['YEAR_QUARTER', 'PROV_FOR_LOAN_LEASE_LOSS', ]]
    
    ## Select Quarter
    
    
    # Subset the dataframe to only the selected year
    
    peer_compare_data 
    
    
    alt.Chart(source).mark_bar().encode(
    x='sum(yield)',
    y='variety',
    color='site',
    order=alt.Order(
      # Sort the segments of the bars by this field
      'site',
      sort='ascending'
    )
    )
    
    reserve_build_release = alt.Chart(current_bank_data_v1).mark_bar().encode(
        x = )
    
    st.altair_chart(reserve_build_release)
    
    # CECL Coverage Rate Index
    
    # Loan Growth QoQ Percent Changes
    
    
    st.write()

#%% Create data summary and exploration tool

def data_exploration():
    st.header("Explore the Peer Bank and Macroeconomic Data")
    
    st.subheader("Peer Bank Data Analysis")
    
    st.subheader("Macroeconomic Data and Trend - Fred QD Database")
    

#%% Create the coverage rate analysis page

def coverage_rates():
    st.header("Coverage Rates Across Peer Banks")
    
    fred_qd_raw = load_fredqd(120) 
    peer_bank_raw = load_peer_data(2400) 
   
    quarter = st.selectbox(label = "Select the current quarter or quarter you want to view:", options = ['Q1', 'Q2', 'Q3', 'Q4'])
    year = st.selectbox(label = "Select the current year or year you want to view:", 
                        options = ['1990', '1991', '1992', '1993', '1994', '1995', '1996', '1997', '1998', '1999', 
                                   '2000', '2001', '2002', '2003', '2004', '2005', '2006', '2007', '2008', '2009',
                                   '2010', '2011', '2012', '2013', '2014', '2015', '2016', '2017', '2018', '2019',
                                   '2020', '2021', '2022', '2023', '2024', '2025', '2026', '2027', '2028', '2029'])
    curr_year_quarter = "".join([year, quarter])
    
    # Subset the dataframe to only the selected year
    
    current_bank_data = peer_bank_raw[peer_bank_raw['YEAR_QUARTER'] == curr_year_quarter]
    
    # Select Bank
    
    bank_list = peer_bank_raw['BANK_NAME_ABBR'].values
    
    def unique(list1):
        x = np.array(list1)
        return (np.unique(x))
    
    bank_list = unique(bank_list)
    
    bank_name = st.selectbox(label = "Select the bank you wish to analyze:", options = bank_list)
    bank_data = current_bank_data[current_bank_data["BANK_NAME_ABBR"] == bank_name]
    
    
    
    # QoQ Coverage Rate Walk

    # CECL Coverage Rate Index
    
    
#%% Create provision and NCOs across peer banks

def provision_nco():
    st.header("Provision and NCOs Across Peer Banks")
    
    fred_qd_raw = load_fredqd(120) 
    peer_bank_raw = load_peer_data(2400) 
    
    st.subheader("Provision Analysis")
    
    st.subheader("Loss Rate Analysis")

#%% Create the loan balances analysis page

def loan_balances():
    st.header("Loan Balances Across Peer Banks")
    
    fred_qd_raw = load_fredqd(120) 
    peer_bank_raw = load_peer_data(2400) 
    
#%% Create forecasting analysis tool

def nco_analysis():
    st.header("Loss Rates Across Peer Banks")
    
    fred_qd_raw = load_fredqd(120) 
    peer_bank_raw = load_peer_data(2400) 

#%% Create the forecasting tool

def forecast_tool():
    st.header("Forecasting Tool for ACL Metrics")   
    
    fred_qd_raw = load_fredqd(120) 
    peer_bank_raw = load_peer_data(2400) 

    def nco_run_off():
        st.subheader("Flat Loan Balance & NCO Run-Off Scenario")
        
        fred_qd_raw = load_fredqd(120) 
        peer_bank_raw = load_peer_data(2400) 
        
        # Create the forecast input dataset
        
        ## Straightline ncos while holding loan balances constant throughout forecasted periods
        
        ## Arthmetic: Taking ncos off of the ACL each quarter for a forecasted 12 quarters 
        
        
        # Function to return the period when the forecasted coverage rate is less than or equal to LD1 coverage rate
        
        ## Calculation should have a reasonable margin of error (within 5 bps) or whichever delta between the periods is less
        
        ### For each bank, store the forecast period where coverage rate returns to LD1 levels and put it together in a dataframe
        
        
        # Concatenate forecasted periods and values into a dataframe
        
        ## Append the actual values + forecasted values along with comparison types - save dataframe as individual_analysis
        
        ## Aggreagate / group (sum) the data by comparison type - recaculate ratios to align with simple weighted means
        
        ## Aggregagte / group (weighted average) the data by comparison type - recaculated ratios to align with simple weighted averages
        
        
        
    def provision_plug():
        st.subheader("Flat Loan Balance, Provision Plug Scenario")
        
        fred_qd_raw = load_fredqd(120) 
        peer_bank_raw = load_peer_data(2400) 
        
        st.text("")
        st.subheader("Make your selections and change sensitivity widgets to conduct analysis")
        
        st.date_input(label="Current Quarter:")
        
        return_quarters = st.slider('Slide Me: # of Quarters to Return to LD1', min_value=0, max_value=10)
        
        
    def linear_model():
        st.subheader("Linear Forecast of ACL Metrics")
        
        fred_qd_raw = load_fredqd(120) 
        peer_bank_raw = load_peer_data(2400) 
        
    def arima():
        st.subheader("ARIMA Forecast of ACL Metrics")
        
        fred_qd_raw = load_fredqd(120) 
        peer_bank_raw = load_peer_data(2400) 
    
    def main():
        selected_box = st.sidebar.selectbox('Select the Forecast Type', 
                                            ('Flat Loan Balance & NCO Run-Off Scenario','Flat Loan Balance, Provision Plug Scenario',
                                             'Linear Forecast of ACL Metrics', 'ARIMA Forecast of ACL Metrics'))
        if selected_box == 'Flat Loan Balance & NCO Run-Off Scenario': 
            nco_run_off() 
        if selected_box == 'Flat Loan Balance, Provision Plug Scenario': 
            provision_plug()
        if selected_box == 'Linear Forecast of ACL Metrics': 
            linear_model()
        if selected_box == 'ARIMA Forecast of ACL Metrics': 
            arima()
        
    if __name__ == "__main__":
        main()

#%% Create the app with loaded data


def main():
    selected_box = st.sidebar.selectbox('Choose one of the following', 
                                        ('Tutotrial and Instructions', 'PDF to Excel (Earnings Releases Download)', 'Standard Peer Deck Visuals','Data Exploration', 
                                         'Coverage Rate Analysis', 'Provision and Loss Rates Analysis',
                                         'Loan Balances', 'Loss Rates and NCO Analysis', 'Forecasting Analysis'))
    if selected_box == 'Tutotrial and Instructions': 
        instructions() 
    if selected_box == 'PDF to Excel (Earnings Releases Download)':
        manual_extract()
    if selected_box == 'Standard Peer Deck Visuals':
        peer_visuals()
    if selected_box == 'Data Exploration': 
        data_exploration()
    if selected_box == 'Coverage Rate Analysis': 
        coverage_rates()
    if selected_box == 'Provision and Loss Rates Analysis': 
        provision_nco()
    if selected_box == 'Loan Balances': 
        loan_balances()
    if selected_box == 'Loss Rates and NCO Analysis': 
        nco_analysis()
    if selected_box == 'Forecasting Analysis': 
        forecast_tool()
    
if __name__ == "__main__":
    main()
