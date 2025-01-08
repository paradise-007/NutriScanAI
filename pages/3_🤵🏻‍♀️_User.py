import streamlit as st
from PIL import Image
from datetime import date
from Home import url, db, user_collection
from Database import insert_data
from OCR import perform_ocr
from Ingredients_Match import Match_Ingredient
from Output_Generator import display_ingredients

# Display app title
st.markdown("<h1 style='text-align: center; font-weight: bold;'>NutriScanAI</h1>", unsafe_allow_html=True)

# Allergy map
allergy_map = {
    'None': 0,
    'Nut': 1,
    'Lactose': 2,
    'Wheat': 3,
    'Soy': 4,
    'Digestive/Skin': 5
}

# User inputs
Name = st.text_input("Enter Your Name:", max_chars=20)
Gender = st.radio("Select Your Gender:", options=["Male", "Female"], horizontal=True)
State = st.selectbox("Select Your State:", options=[
    'None', 'Andhra Pradesh', 'Bihar', 'Goa', 'Gujarat', 'Haryana', 'Karnataka',
    'Kerala', 'Madhya Pradesh', 'Maharashtra', 'Odisha', 'Punjab', 'Rajasthan',
    'Tamil Nadu', 'Telangana', 'Uttar Pradesh', 'Uttarakhand', 'West Bengal'
])
Allergy = st.selectbox(label='If you Have Any Allergy:', options=['None', 'Nut', 'Lactose', 'Wheat', 'Soy', 'Digestive/Skin'])
Allergy_Number = allergy_map.get(Allergy, 0)
Date = str(date.today())

# Function to handle image processing, OCR, and matching ingredients
def User(image, Name, Gender, State, Date, Allergy_Number):
    try:
        # Perform OCR
        tokens = perform_ocr(image)
        if len(tokens) == 0:
            st.markdown("""
                ### 🚫 - Text Not Found in Image!
                - Please use a clear image with proper lighting.
            """)
            st.stop()

        # Match ingredients based on OCR tokens
        matched_ingredients = Match_Ingredient(tokens, threshold=0.8)
        if len(matched_ingredients) == 0:
            st.error("No ingredients found. The image might not contain readable text. ❌")
            st.stop()

        # Initialize the ingredient data dictionary
        ingredient_data = {
            "name": Name,
            "gender": Gender,
            "state": State,
            "date": Date,
            "type3": {},
            "type2": {},
            "type1": {},
            "type0": {}
        }

        # Process matched ingredients
        for ingredient_data_tuple in matched_ingredients:
            if len(ingredient_data_tuple) == 4:
                ingredient, level, allergy, _ = ingredient_data_tuple
                category = f"type{level}"
                ingredient_data[category][f"ing{len(ingredient_data[category]) + 1}"] = ingredient
            else:
                st.error(f"Malformed ingredient data: {ingredient_data_tuple}. Expected a tuple with 4 elements.")
                break  # Exit loop after error

        # Display ingredients
        display_ingredients(matched_ingredients, user_allergy=Allergy_Number)

        # Insert data into the database
        if insert_data(url, db, user_collection, ingredient_data):
            st.success("Data inserted successfully! 🎉🍾")
        else:
            st.error("Failed to insert data into the database! ❌")

    except Exception as e:
        st.error(f"Error: {e}")

# Main logic
if Name:
    if State != 'None':
        st.write("Choose an Option to Scan Ingredients:")

    # Tabs for file upload or camera input
        Upload, Camera = st.tabs(['Upload File', 'Use Camera'])

    # File upload tab
        with Upload:
            uploaded_image = st.file_uploader("Upload an Image File:", type=["jpg", "png", "jpeg"])
            if uploaded_image is not None:
                image = Image.open(uploaded_image)
                User(image, Name, Gender, State, Date, Allergy_Number)

    # Camera input tab
        with Camera:
            camera_image = st.camera_input("Use Camera for Input:")
            if camera_image is not None:
                image = Image.open(camera_image)
                User(image, Name, Gender, State, Date, Allergy_Number)
