from dotenv import load_dotenv
load_dotenv()

import streamlit as st
import os
import google.generativeai as genai
import json
import re

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Define research prompt template for soil testing labs
field_prompt = (
    "As an expert in location-based services and geospatial data, your task is to provide a precise and accurate list of nearby soil testing labs "
    "for the specified location. Please return the response in a well-structured JSON format. "
    "Each entry should include the lab's name and a direct Google Maps link for easy navigation. "
    "Ensure the JSON output follows this structure: [{'name': 'Lab 1', 'link': 'https://www.google.com/maps/...'}, ...]. "
    "Please make sure the response is clean and contains only the JSON data, without any additional explanations or text."
)

# Function to load Gemini Pro model and get responses
model = genai.GenerativeModel("gemini-pro")
chat = model.start_chat(history=[])

def extract_json(text):
    # Use regex to find a valid JSON block in the response
    json_pattern = r'\{.*\}|\[.*\]'
    match = re.search(json_pattern, text, re.DOTALL)
    
    if match:
        return match.group(0)
    else:
        return None

def get_gemini_response(location):
    prompt = field_prompt + location
    response = chat.send_message(prompt, stream=True)
    
    # Capture the full response text
    response_text = ""
    for chunk in response:
        response_text += chunk.text
    
    return response_text

# Initialize Streamlit app
st.set_page_config(page_title="Soil Testing Labs Finder")

st.header("Soil Testing Labs Finder")

# User input for location
location_input = st.text_input("Enter your location: ", key="location_input")
submit = st.button("Find Soil Testing Labs")

if submit and location_input:
    response = get_gemini_response(location_input)
    
    # Extract JSON from the response text
    json_data = extract_json(response)
    
    if json_data:
        try:
            # Parse the extracted JSON
            soil_labs = json.loads(json_data)
            st.subheader("Nearby Soil Testing Labs:")
            for lab in soil_labs:
                st.write(f"**{lab['name']}** - [Google Maps Link]({lab['link']})")
        except json.JSONDecodeError:
            st.error("Error decoding the JSON data. Please try again.")
    else:
        st.error("No valid JSON found in the response. Please try again.")

st.markdown("---")
