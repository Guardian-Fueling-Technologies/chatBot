import streamlit as st
import pandas as pd
import os
import PyPDF2

def login():
    username = ""
    password = "1231"
    entered_username = st.text_input("Username")
    entered_password = st.text_input("Password", type="password")
    if entered_username == username and entered_password == password:
        return True
    else:
        return False

def upload_files():
    file = st.file_uploader("Upload a file", type=["txt"])
    if file is not None:
        if file.type == "text/plain":
            # Process TXT file
            pass
        else:
            st.warning("Unsupported file format.")
    st.write("Welcome to the upload page!")  # Placeholder content for demonstration

def main():
    if not login():
        st.warning("Login failed. Please try again.")
    else:
        upload_files()

if __name__ == "__main__":
    main()