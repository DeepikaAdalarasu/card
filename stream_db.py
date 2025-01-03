import streamlit as st
import google.generativeai as genai
from PIL import Image
import pandas as pd
import json
from pymongo import MongoClient

# Set Streamlit page configuration
st.set_page_config(layout="wide")

# Configure Google Generative AI
genai.configure(api_key="AIzaSyCy-adougZMxXlsZp06xx1pJ_a6xwGcE5E")
model = genai.GenerativeModel("gemini-1.5-flash")

# MongoDB Connection
MONGO_URI = "mongodb://localhost:27017/"
client = MongoClient(MONGO_URI)
db = client["image_data"]  # Replace with your database name
collection = db["extracted_info"]  # Replace with your collection name

# Streamlit App
st.title("Image Information Extractor")

# Upload Images
uploaded_images = st.file_uploader(
    "Upload one or two images (e.g., details and/or company info)", 
    type=["jpg", "png", "jpeg"], 
    accept_multiple_files=True, 
)

if uploaded_images:
    if len(uploaded_images) == 1:
        # Single image processing
        image = Image.open(uploaded_images[0])
        st.image(image, caption="Uploaded Image", use_container_width=True)

        with st.spinner("Extracting information from the image..."):
            response = model.generate_content(
                ["Extract the company name, name, profession, email address, address, phone number, and website. Provide the output in JSON format. Don't provide the unwanted string, Provide only json", image]
            )
            js = response.text.strip()
            js = js.replace("```json", "").replace("```", "")  # Clean code block markers

    elif len(uploaded_images) == 2:
        # Two images processing together
        image1 = Image.open(uploaded_images[0])
        image2 = Image.open(uploaded_images[1])

        st.image([image1, image2], caption=["Image 1", "Image 2"], use_container_width=True)

        with st.spinner("Extracting information from both images..."):
            response = model.generate_content(
                [
                    "Combine the information from the following images. Extract the company name, name, profession, email address, address, phone number, and website. Provide the output in JSON format. Don't provide the unwanted string, Provide only json",
                    image1,
                    image2,
                ]
            )
            js = response.text.strip()
            js = js.replace("```json", "").replace("```", "")  # Clean code block markers

    # Parse JSON response
    try:
        data = json.loads(js)

        # Display the extracted data in JSON format
        st.success("Extraction complete!")
        st.json(data)

        # Save to MongoDB only if it's from image processing
        if st.button("Save to Database"):
            collection.insert_one(data)
            st.success("Data saved to database successfully!")

    except json.JSONDecodeError:
        st.error("Failed to parse the response. Please ensure the model output is in JSON format.")

else:
    st.info("Please upload one or two images for processing.")

# Search Functionality
st.header("Search Extracted Information")
search_name = st.text_input("Enter the name to search:")
if st.button("Search"):
    if search_name:
        result = collection.find_one({"name": search_name})
        if result:
            st.success("Record found!")
            st.json(result)
        else:
            st.error("No record found for the given name.")
    else:
        st.warning("Please enter a name to search.")

