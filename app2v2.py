import streamlit as st
import pandas as pd
import requests
from PIL import Image
import io
import time
from io import BytesIO
from reportlab.lib.pagesizes import letter
from datetime import datetime
from reportlab.pdfgen import canvas
from PyPDF2 import PdfReader, PdfWriter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib import colors
from reportlab.platypus import Paragraph
import numpy as np
import re
from reportlab.pdfgen import canvas
from decimal import Decimal

current_date = datetime.now()
formatted_date = current_date.strftime("%m/%d/%Y")
if "pricingDf" not in st.session_state:
    st.session_state.pricingDf = None
if "ticketDf" not in st.session_state:
    st.session_state.ticketDf = None
if "TRatesDf" not in st.session_state:
    st.session_state.TRatesDf = None
if "LRatesDf" not in st.session_state:
    st.session_state.LRatesDf = None
if "misc_ops_df" not in st.session_state:
    st.session_state.misc_ops_df = None
if "edit" not in st.session_state:
    st.session_state.edit = None
if "workDescription" not in st.session_state:
    st.session_state.workDescription = None
if "editable" not in st.session_state:
    st.session_state.editable = None
if "refresh_button" not in st.session_state:
    st.session_state.refresh_button = None
if "iframe" not in st.session_state:
    st.session_state.iframe = None

if "labor_df" not in st.session_state:
    st.session_state.labor_df = pd.DataFrame()
    st.session_state.trip_charge_df = pd.DataFrame()
    st.session_state.parts_df = pd.DataFrame()
    st.session_state.miscellaneous_charges_df = pd.DataFrame()
    st.session_state.materials_and_rentals_df = pd.DataFrame()
    st.session_state.subcontractor_df = pd.DataFrame()

def mainPage():
    # header_image_url = "https://github.com/Charlieletscode/GuardianFueltech-Visualization-Board-Admin/blob/main/Header.jpg?raw=true"
    # response = requests.get(header_image_url)
    # image = Image.open(io.BytesIO(response.content))
    # image_height = 200
    # resized_image = image.resize((int(image_height * image.width / image.height), image_height))

    st.subheader("Main Page")
    st.write("Welcome to the main page of the Fee Charge Types application.")
    selected_option = st.radio("Select Option:", ["NTE", "Quote"])
    st.write("You selected:", selected_option)
    st.markdown(
        """
       <style>
       [data-testid="stSidebar"][aria-expanded="true"]{
           min-width: 300px;
           max-width: 300px;
       },
       <style>
                .stButton button {
                    float: left;
                }
                .stButton button:first-child {
                    background-color: #0099FF;
                    color: #FFFFFF;
                    width: 120px;
                    height: 50px;
                }
                .stButton button:hover {
                    background-color: #FFFF00;
                    color: #000000;
                    width: 120px;
                    height: 50px;
                }
                </style>
       """,
        unsafe_allow_html=True,
    )   
    st.session_state.ticketN = ""
    st.session_state.ticketN = st.sidebar.text_input("Enter ticket number:")
    if(not st.session_state.refresh_button):
        st.session_state.refresh_button = st.sidebar.button("Refresh")
    # try:
    if 'ticketN' in st.session_state and st.session_state.ticketN:
        if st.session_state.refresh_button or st.session_state.ticketDf is None:
            st.session_state.iframe = "main"
        try:
            left_data = {
                'To': st.session_state.ticketDf['CUST_NAME'] + " " + st.session_state.ticketDf['CUST_ADDRESS1'] + " " +
                    st.session_state.ticketDf['CUST_ADDRESS2'] + " " + st.session_state.ticketDf['CUST_ADDRESS3'] + " " +
                    st.session_state.ticketDf['CUST_CITY'] + " " + st.session_state.ticketDf['CUST_Zip'],
                'ATTN': ['ATTN']
            }
        except (Exception, KeyError) as e:
            st.error("Please enter a ticket number or check the ticket number again")
            st.session_state.ticketN = ""
            st.session_state.refresh_button = True
            st.sidebar.empty()
            st.experimental_rerun()            

        col1, col2 = st.sidebar.columns(2)
        with col1:
            if st.button("Edit", key="1"):
                st.session_state.edit = True
        with col2:
            if st.button("View", key="2"):
                st.session_state.edit = False
        
        col1, col2 = st.columns((2,1))
        df_left = pd.DataFrame(left_data)
        left_table_styles = [
            {'selector': 'table', 'props': [('text-align', 'left'), ('border-collapse', 'collapse')]},
            {'selector': 'th, td', 'props': [('padding', '8px'), ('border', '1px solid black')]}
        ]
        df_left_styled = df_left.style.set_table_styles(left_table_styles)

        col1.dataframe(df_left_styled, hide_index=True)
        # col2.image(resized_image, width=300)

        # Ticket Info table
        data = {
            'Site': st.session_state.ticketDf['LOC_LOCATNNM'],
            'Ticket #': st.session_state.ticketN,
            'Address': st.session_state.ticketDf['LOC_Address'] + " " + st.session_state.ticketDf['CITY'] + " " +
                    st.session_state.ticketDf['STATE'] + " " + st.session_state.ticketDf['ZIP']
        }

def itemizedView():
    st.write("Itemized View function")
def returnToBid():
    st.write("Return to Bid function")
def savePDF():
    st.write("Save PDF & Load to Email function")
def returnToForm():
    st.write("returntoForm")
def feeCharge():
    fee_charge_types = st.session_state.misc_ops_df

    st.subheader("Fee Charge Types")
    
    df = pd.DataFrame(fee_charge_types, columns=["Fee Charge Type", "Fee Amount"])
    st.table(df)

def payRate():
    st.subheader("Pay Rate Info")
    st.subheader(st.session_state.ticketN)
    if st.session_state.ticketN:
        billing_amount_1 = st.session_state.LRatesDf['Billing_Amount']
        pay_code_description_1 = st.session_state.LRatesDf['Pay_Code_Description']
        df1 = pd.DataFrame({"Billing_Amount": billing_amount_1, "Pay_Code_Description": pay_code_description_1})

        billing_amount_2 = st.session_state.TRatesDf['Billing_Amount']
        pay_code_description_2 = st.session_state.TRatesDf['Pay_Code_Description']
        df2 = pd.DataFrame({"Billing_Amount": billing_amount_2, "Pay_Code_Description": pay_code_description_2})

        st.subheader("Payrate - Labor_Charge")
        st.table(df1)

        st.subheader("Payrate - Travels")
        st.table(df2)

def ticketInfo():
    st.subheader("Ticket Info")
    st.subheader(st.session_state.ticketN)
    if st.session_state.ticketN:
        transposed_df = st.session_state.ticketDf.transpose()
        st.table(transposed_df)
    else:
        st.warning("no ticket Number")

def pricing():
    st.subheader("Pricing")
    st.subheader(st.session_state.ticketN)
    if st.session_state.ticketN:
        st.table(st.session_state.pricingDf)
    else:
        st.warning("no ticket Number")

def iframePage():
    iframe_code = '''<form class="formcontainer">
                <iframe src="http://127.0.0.1:8050/" style="width: 100%; height: calc(100vh - 60px); border: none;" allowfullscreen="False" loading="lazy"></iframe>
                </form>
                <style>
                .formcontainer {
                  position: fixed;
                  bottom: 10px;
                  right: 10px;
                  z-index: 1000;
                  border: 1px solid #ddd;
                  border-radius: 8px;
                  background-color: #fff;
                  box-shadow: 0px 2px 4px rgba(0, 0, 0, 0.1);
                  width: 330px;
                }
                </style>
            '''
    if st.sidebar.button("Main"):
        st.session_state.iframe = "main"
        st.empty()
        st.experimental_rerun()
        
    if st.button("close"):
        st.session_state.iframe = "main"
        st.empty()
        st.experimental_rerun()
    st.markdown(iframe_code, unsafe_allow_html=True)

def main():
    st.set_page_config("Universal Quote Template", layout="wide")
    mainPage()
    st.markdown(
        """
        <style>
        .stButton>button {
            background-color: #555;
            color: white;
            padding: 16px 20px;
            border: none;
            cursor: pointer;
            opacity: 0.8;
            position: sticky;
            bottom: 0%;
            left: 90%;
            float: right;
            width: 280px;
        }.form-popup {
      display: none;
      position: fixed;
      bottom: 0;
      right: 15px;
      border: 3px solid #f1f1f1;
      z-index: 9;
    }
        </style>
        """,
            unsafe_allow_html=True
        )
    
    if st.button("Go to Iframe Page"):
        st.session_state.iframe = "iframe"
        iframePage()


if __name__ == "__main__":
    if st.session_state.iframe is None or st.session_state.iframe == "main":
        main()
    else:
        iframePage()
    if st.session_state.refresh_button:
        st.session_state.refresh_button = False


# if __name__ == "__main__":
#     main()
    # st.sidebar.title("Select Page")
    # hide_menu_style = """
    #     <style>
    #     #MainMenu {visibility: hidden; }
    #     footer {visibility: hidden;}
    #     </style>
    #         """
    # st.markdown(hide_menu_style, unsafe_allow_html=True)
    # selection = st.sidebar.radio("Select Page", ["Main Page", "Fee Charge", "Pay Rate", "Ticket Info", "Pricing"])

    # if selection == "Main Page":
    # elif selection == "Fee Charge":
    #     feeCharge()
    # elif selection == "Pay Rate":
    #     payRate()
    # elif selection == "Ticket Info":
    #     ticketInfo()
    # elif selection == "Pricing":
    #     pricing()