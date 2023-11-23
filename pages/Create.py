import streamlit as st
import cv2
import numpy as np
import sys
from datetime import datetime
import pytz
import pandas as pd
from streamlit_gsheets import GSheetsConnection


# Create a connection object.
conn = st.connection("gsheets", type=GSheetsConnection)

img_file_buffer = st.camera_input("Capture le QR")
sheet_write = conn.read(worksheet="Scan",usecols=list(range(32)),ttl=5)
sheet_write.index = sheet_write['Matricule']
point = st.selectbox("Point of day",sheet_write.columns[1:])
date = datetime.now(pytz.timezone('Africa/Abidjan'))

if img_file_buffer is not None:
    # To read image file buffer with OpenCV:
    bytes_data = img_file_buffer.getvalue()
    cv2_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)

    qrDecoder = cv2.QRCodeDetector()
    
    # Detect and decode the qrcode
    data,bbox,rectifiedImage = qrDecoder.detectAndDecode(cv2_img)
    if len(data)>0:
        rectifiedImage = np.uint8(rectifiedImage)
        st.success(f"QR code detected {data}",icon="✅")
        sheet_write.at[int(data), point] = date.strftime("%d/%m/%y %H:%M")
        conn.update(worksheet="Scan", data=sheet_write)
    else:
        st.warning('QR Code not detected', icon="⚠️")

st.dataframe(sheet_write,hide_index=True)
